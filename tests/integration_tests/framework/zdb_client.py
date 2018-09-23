import socket


class ZDBCLIENT:
    def __init__(self, ip, port=9900):
        self._zdb_server = (ip, port)
        self._connect_to_zdb_server()

    def _encode(self, cmd):
        terms = cmd.split(' ')
        arr_protocol = "*{}\r\n".format(len(terms))
        for term in terms:
            str_protocol = "${}\r\n{}\r\n".format(len(term), term)
            arr_protocol += str_protocol
        return arr_protocol

    def _decode(self, response):
        if response[0] in ['-', '+', ':']:
            return response[1:].replace('\r\n', '')
        elif response[0] == '$':
            return response[2:].replace('\r\n', '')
        elif response[0] == '*':
            if '*' not in response[1:]:
                data = ''
                items = response.split('\r\n')
                for item in items:
                    if item[0] not in ['-', '+', ':', '$', '*']:
                        data += '{} '.format(item)
                return data[:-1]
            else:
                # TODO
                return response

    def _connect_to_zdb_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self._zdb_server)
        self.sock.settimeout(5)

    def _send_cmd(self, cmd):
        data = self._encode(cmd)
        self.sock.sendall(bytes(data, "utf-8"))
        # try:
        #     self.sock.sendall(bytes(data, "utf-8"))
        # except:
        #     self._connect_to_zdb_server()
        #     self._send_cmd(cmd)

    def _receive(self):
        try:
            response = self._decode(str(self.sock.recv(128), "utf-8"))
            return response
        except socket.timeout:
            print(' [x] Timeout error! ')

    def send_receive(self, cmd):
        self._send_cmd(cmd)
        return self._receive()

    def ping(self):
        cmd = 'PING'
        return self.send_receive(cmd)

    def set(self, key, value):
        cmd = 'SET {} {}'.format(key, value)
        return self.send_receive(cmd)

    def get(self, key):
        cmd = 'GET {}'.format(key)
        return self.send_receive(cmd)

    def delete(self, key):
        cmd = 'DEL {}'.format(key)
        return self.send_receive(cmd)

    def stop(self):
        cmd = 'STOP'
        return self.send_receive(cmd)

    def exists(self, key):
        cmd = 'EXISTS {}'.format(key)
        return self.send_receive(cmd)

    def check(self, key):
        cmd = 'CHECK {}'.format(key)
        return self.send_receive(cmd)

    def info(self):
        cmd = 'INFO'
        return self.send_receive(cmd)

    def nsnew(self, namespace):
        cmd = 'NSNEW {}'.format(namespace)
        return self.send_receive(cmd)

    def nsdel(self, namespace):
        cmd = 'NSDEL {}'.format(namespace)
        return self.send_receive(cmd)

    def nsinfo(self, namespace):
        cmd = 'NSINFO {}'.format(namespace)
        return self.send_receive(cmd)

    def nslist(self):
        cmd = 'NSLIST'
        return self.send_receive(cmd)

    def nsset(self, namespace, property, value):
        if property not in ['maxsize', 'password', 'public']:
            return " [-] property should be in ['maxsize', 'password', 'public'] "

        cmd = 'NSSET {} {} {} '.format(namespace, property, value)
        return self.send_receive(cmd)

    def select(self, namespace, password=''):
        cmd = 'SELECT {} {}'.format(namespace, password)
        return self.send_receive(cmd)

    def dbsize(self):
        cmd = 'DBSIZE'
        return self.send_receive(cmd)

    def time(self):
        cmd = 'TIME'
        return self.send_receive(cmd)

    def auth(self, password):
        cmd = 'AUTH {}'.format(password)
        return self.send_receive(cmd)

    def scan(self, key=''):
        cmd = 'SCAN {}'.format(key)
        return self.send_receive(cmd)

    def rscan(self, key=''):
        cmd = 'RSCAN {}'.format(key)
        return self.send_receive(cmd)
