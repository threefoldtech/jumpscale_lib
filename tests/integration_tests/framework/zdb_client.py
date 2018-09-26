import redis


class ZDBCLIENT:
    def __init__(self, ip, port=9900):
        self.zdb_server_ip = ip
        self.zdb_server_port = port
        self._connect_to_zdb_server()

    def _connect_to_zdb_server(self):
        self.zdb_client = redis.StrictRedis(host=self.zdb_server_ip, port=self.zdb_server_port, db=0)

    def execute_command(self, cmd):
        return self.zdb_client.execute_command(cmd)

    def send_receive(self, cmd):
        response = self.zdb_client.execute_command(cmd)
        try:
            return response.decode()
        except:
            return response

    def ping(self, case):
        cmd = 'PING'
        if case == "lower":
            cmd = cmd.lower()
        return self.send_receive(cmd)

    def set(self, key, value, case):
        cmd = 'SET'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {} {}'.format(cmd, key, value)
        return self.send_receive(cmd)

    def get(self, key, case):
        cmd = 'GET'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, key)
        return self.send_receive(cmd)

    def delete(self, key, case):
        cmd = 'DEL'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, key)
        return self.send_receive(cmd)

    def stop(self, case):
        cmd = 'STOP'
        if case == "lower":
            cmd = cmd.lower()
        return self.send_receive(cmd)

    def exists(self, key, case):
        cmd = 'EXISTS'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, key)
        return self.send_receive(cmd)

    def check(self, key, case):
        cmd = 'CHECK'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, key)
        return self.send_receive(cmd)

    def info(self, case):
        cmd = 'INFO'
        if case == "lower":
            cmd = cmd.lower()
        return self.send_receive(cmd)

    def nsnew(self, namespace, case):
        cmd = 'NSNEW'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, namespace)
        return self.send_receive(cmd)

    def nsdel(self, namespace, case):
        cmd = 'NSDEL'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, namespace)
        return self.send_receive(cmd)

    def nsinfo(self, namespace, case):
        cmd = 'NSINFO'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, namespace)
        return self.send_receive(cmd)

    def nslist(self, case):
        cmd = 'NSLIST'
        if case == "lower":
            cmd = cmd.lower()
        return self.send_receive(cmd)

    def nsset(self, namespace, property, value, case):
        if property not in ['maxsize', 'password', 'public']:
            return " [-] property should be in ['maxsize', 'password', 'public'] "

        cmd = 'NSSET'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {} {} {}'.format(cmd, namespace, property, value)
        return self.send_receive(cmd)

    def select(self, namespace, case, password=''):
        cmd = 'SELECT'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {} {}'.format(cmd, namespace, password)
        return self.send_receive(cmd)

    def dbsize(self, case):
        cmd = 'DBSIZE'
        if case == "lower":
            cmd = cmd.lower()
        return self.send_receive(cmd)

    def time(self, case):
        cmd = 'TIME'
        if case == "lower":
            cmd = cmd.lower()
        return self.send_receive(cmd)

    def auth(self, password, case):
        cmd = 'AUTH'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, password)
        return self.send_receive(cmd)

    def scan(self, case, key=''):
        cmd = 'SCAN'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, key)
        return self.send_receive(cmd)

    def rscan(self, case, key=''):
        cmd = 'RSCAN'
        if case == "lower":
            cmd = cmd.lower()
        cmd = '{} {}'.format(cmd, key)
        return self.send_receive(cmd)