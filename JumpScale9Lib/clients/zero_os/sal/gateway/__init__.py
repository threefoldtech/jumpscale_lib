from .gateway import Gateway

class Gateways:
    def get(self, container, data):
        """
        param data: dict object containing detailed information about the gateway
            See: https://github.com/zero-os/0-templates/blob/master/templates/gateway/README.md
        """
        return Gateway(container, data)

