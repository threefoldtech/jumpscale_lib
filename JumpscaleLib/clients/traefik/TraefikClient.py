from Jumpscale import j

JSConfigBase = j.tools.configmanager.JSBaseClassConfig

TEMPLATE = """
etcd_instance = "main"
"""


class TraefikClient(JSConfigBase):
    def __init__(self, instance, data={}, parent=None, interactive=None):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        self._etcd_client = None
        self._etcd_instance = self.config.data['etcd_instance']

    @property
    def etcd_client(self):
        if not self._etcd_client:
            self._etcd_client = j.clients.etcd.get(self._etcd_instance)
        return self._etcd_client

    @property
    def proxy(self):
        return Proxy(self.etcd_client)

    def backend_get(self, name, servers=None, load_balance_method="wrr", cb_expression=""):
        """
        :param name: the name of backend to be referred to
        :param servers: list of backend servers objects `BackendServer`
        :param load_balance_method: the load balancing method to be used by traefik.
        it is either:
         - "wrr": weight round robin [the default]
         - "drr": dynamic round robin
        :param cb_expression: str: the circuit breaker expression. It can be configured using:
            Methods: LatencyAtQuantileMS, NetworkErrorRatio, ResponseCodeRatio
            Operators: AND, OR, EQ, NEQ, LT, LE, GT, GE
        For example:
            'NetworkErrorRatio() > 0.5': watch error ratio over 10 second sliding window for a frontend.
            'LatencyAtQuantileMS(50.0) > 50': watch latency at quantile in milliseconds.
            'ResponseCodeRatio(500, 600, 0, 600) > 0.5': ratio of response codes in ranges [500-600) and [0-600).
        :return: Backend Object
        """
        return Backend(name, servers, load_balance_method, cb_expression)

    def frontend_get(self, name, backend_name="", rules=None):
        """
        :param name: the name of backend to be referred to
        :param rules: the list of rules to be added for this frontend
        :return: Frontend Object
        """
        return Frontend(name, backend_name, rules)

    def backend_server_get(self, ip, port="80", scheme="http", weight="10"):
        return BackendServer(ip, port, scheme, weight)

    def frontend_rule_get(self, rule_value, rule_type="Host"):
        """
        :param rule_type:
        is the type of rule to be applied for url, you can use any rule of the matchers and modifiers:
            - matchers:
                - Headers, HeadersRegexp, Host, HostRegexp, Method, Path, PathStrip, PathStripRegex
                  PathPrefix, PathPrefixStrip, PathPrefixStripRegex, Query
            - modifiers:
                - AddPrefix, ReplacePath, ReplacePathRegex
        for more info: https://docs.traefik.io/basics/#modifiers
        :param rule_value: the value for this rule, it depends on the rule type
        """
        return FrontendRule(rule_value, rule_type)


class Proxy:
    """
    The main class to use for adding/deleting reverse proxy forwarding into etcd
    """

    def __init__(self, etcd_client):
        """
        :param etcd_client: etcd client instance (j.clients.etcd.get())
        """
        self.etcd_client = etcd_client

    def deploy(self, backends=None, frontends=None):
        """
        add proxy configurations in etcd
        :param frontends: list of `Frontend` objects that needs to be added
        :param backends: list of `Backend` objects that will be connected to the frontend
        """
        # register the backends and frontends for traefik use
        self._deploy_backends(backends)
        self._deploy_frontends(frontends)

    def delete(self, backends=None, frontends=None):
        """
        remove backends or frontends from etcd
        """
        backends = backends or []
        frontends = frontends or []

        for backend in backends:
            backend_key = "/traefik/backends/{}".format(backend.name)
            self.etcd_client.api.delete_prefix(backend_key)

        for frontend in  frontends:
            frontend_key = "/traefik/frontends/{}".format(frontend.name)
            self.etcd_client.api.delete_prefix(frontend_key)

    def _deploy_backends(self, backends=None):
        backends = backends or []
        for backend in backends:
            # Set the load balance method
            load_balance_key = "/traefik/backends/{}/loadBalancer/method".format(backend.name)
            self.etcd_client.put(load_balance_key, backend.load_balance_method)

            # Set the circuit breaker config if exists
            if backend.cb_expression:
                cb_key = "/traefik/backends/{}/circuitBreaker".format(backend.name)
                self.etcd_client.put(cb_key, backend.cb_expression)

            # Set the backend servers
            for i, server in enumerate(backend.servers):
                server_key = "/traefik/backends/{}/servers/server{}/url".format(backend.name, i)
                server_value = "{}://{}:{}".format(server.scheme, server.ip, server.port)
                self.etcd_client.put(server_key, server_value)
                server_weight_key = "/traefik/backends/{}/servers/server{}/weight".format(backend.name, i)
                self.etcd_client.put(server_weight_key, str(server.weight))
        return

    def _deploy_frontends(self, frontends):
        frontends = frontends or []
        for frontend in frontends:
            frontend_key1 = "/traefik/frontends/{}/backend".format(frontend.name)
            frontend_value1 = frontend.backend_name
            self.etcd_client.put(frontend_key1, frontend_value1)

            for i, rule in enumerate(frontend.rules):
                rule_key = "/traefik/frontends/{}/routes/rule{}/rule".format(frontend.name, i)
                rule_value = "{}:{}".format(rule.rule_type, rule.rule_value)
                self.etcd_client.put(rule_key, rule_value)
        return


class Backend:
    def __init__(self, name, servers=None, load_balance_method="wrr", cb_expression=""):
        """
        :param name: the name of backend to be referred to
        :param servers: list of backend servers objects `BackendServer`
        :param load_balance_method: the load balancing method to be used by traefik.
        it is either:
         - "wrr": weight round robin [the default]
         - "drr": dynamic round robin
        :param cb_expression: str: the circuit breaker expression. It can be configured using:
            Methods: LatencyAtQuantileMS, NetworkErrorRatio, ResponseCodeRatio
            Operators: AND, OR, EQ, NEQ, LT, LE, GT, GE
        For example:
            'NetworkErrorRatio() > 0.5': watch error ratio over 10 second sliding window for a frontend.
            'LatencyAtQuantileMS(50.0) > 50': watch latency at quantile in milliseconds.
            'ResponseCodeRatio(500, 600, 0, 600) > 0.5': ratio of response codes in ranges [500-600) and [0-600).
        """
        self.name = name
        self.servers = servers
        self.load_balance_method = load_balance_method
        self.cb_expression = cb_expression  # TODO validate the cb_expression to be a valid one


class BackendServer:
    def __init__(self, ip, port="80", scheme="http", weight="10"):
        self.ip = ip
        self.port = port
        self.scheme = scheme
        self.weight = weight


class Frontend:
    def __init__(self, name, backend_name="", rules=None):
        """
        :param name: the name of backend to be referred to
        :param rules: the list of rules to be added for this frontend
        """
        self.name = name
        self.backend_name = backend_name
        self.rules = rules


class FrontendRule:
    def __init__(self, rule_value, rule_type="Host"):
        """
        :param rule_type:
        is the type of rule to be applied for url, you can use any rule of the matchers and modifiers:
            - matchers:
                - Headers, HeadersRegexp, Host, HostRegexp, Method, Path, PathStrip, PathStripRegex
                  PathPrefix, PathPrefixStrip, PathPrefixStripRegex, Query
            - modifiers:
                - AddPrefix, ReplacePath, ReplacePathRegex
        for more info: https://docs.traefik.io/basics/#modifiers
        :param rule_value: the value for this rule, it depends on the rule type
        """
        self.rule_value = rule_value
        self.rule_type = rule_type
