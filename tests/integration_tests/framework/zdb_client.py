import redis


class ZDBCLIENT:
    def __init__(self, ip, port=9900):
        self.zdb_server_ip = ip
        self.zdb_server_port = port
        self._connect_to_zdb_server()

    def _connect_to_zdb_server(self):
        self.zdb_client = redis.StrictRedis(host=self.zdb_server_ip, port=self.zdb_server_port, db=0)

    def execute_command(self, cmd, arg=None):
        return self.zdb_client.execute_command(cmd, arg)

    def send_receive(self, cmd):
        response = self.zdb_client.execute_command(cmd)
        try:
            return response.decode()
        except:
            return response

    def ping(self, case='lower'):
        cmd = 'PING'
        if case == "lower":
            cmd = cmd.lower()
        return self.send_receive(cmd)

    def set(self, key, value, case='lower'):
        cmd = 'SET'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {} {}'.format(cmd, key, value)
        return self.send_receive(cmd)

    def get(self, key, case='lower'):
        cmd = 'GET'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, key)
        return self.send_receive(cmd)

    def delete(self, key, case='lower'):
        cmd = 'DEL'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, key)
        return self.send_receive(cmd)
    
    def key_cursor(self, key, case='lower'):
        cmd = 'KEYCUR'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, key)
        return self.send_receive(cmd)

    def stop(self, case='lower'):
        cmd = 'STOP'
        if case == "lower":
            cmd = cmd.lower()
        return self.send_receive(cmd)

    def exists(self, key, case='lower'):
        cmd = 'EXISTS'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, key)
        return self.send_receive(cmd)

    def check(self, key, case='lower'):
        cmd = 'CHECK'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, key)
        return self.send_receive(cmd)

    def info(self, case='lower'):
        cmd = 'INFO'
        if case == "lower":
            cmd = cmd.lower()
        return self.send_receive(cmd)

    def nsnew(self, namespace, case='lower'):
        cmd = 'NSNEW'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, namespace)
        return self.send_receive(cmd)

    def nsdel(self, namespace, case='lower'):
        cmd = 'NSDEL'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, namespace)
        return self.send_receive(cmd)

    def nsinfo(self, namespace, case='lower'):
        cmd = 'NSINFO'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, namespace)
        return self.send_receive(cmd)

    def nslist(self, case='lower'):
        cmd = 'NSLIST'
        if case == "lower":
            cmd = cmd.lower()

        result = []
        namespaces = self.send_receive(cmd)
        for namespace in namespaces:
            result.append(namespace.decode('utf-8')) 
        return result

    def nsset(self, namespace, property, value, case='lower'):
        if property not in ['maxsize', 'password', 'public']:
            return " [-] property should be in ['maxsize', 'password', 'public'] "

        cmd = 'NSSET'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {} {} {}'.format(cmd, namespace, property, value)
        return self.send_receive(cmd)

    def select(self, namespace, password='', case='lower'):
        cmd = 'SELECT'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {} {}'.format(cmd, namespace, password)
        return self.send_receive(cmd)

    def dbsize(self, case='lower'):
        cmd = 'DBSIZE'
        if case == "lower":
            cmd = cmd.lower()
        return self.send_receive(cmd)

    def time(self, case='lower'):
        cmd = 'TIME'
        if case == "lower":
            cmd = cmd.lower()
        return self.send_receive(cmd)

    def auth(self, password, case='lower'):
        cmd = 'AUTH'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, password)
        return self.send_receive(cmd)

    def scan(self, key='', case='lower'):
        cmd = 'SCAN '
        if case == "lower":
            cmd = cmd.lower()
        return self.execute_command(cmd, key)

    def rscan(self, key='', case='lower'):
        cmd = 'RSCAN'
        if case == "lower":
            cmd = cmd.lower()
        return self.execute_command(cmd, key)