
from js9 import j

import zerotier
import copy
import time
import ipcalc

JSBASE = j.application.jsbase_get_class()
JSConfigClient = j.tools.configmanager.base_class_config

class NetworkMember(JSBASE):
    """
    Represent a zerotier network member
    """
    def __init__(self, network, address, data):
        """
        Initialize new memeber
        """
        JSBASE.__init__(self)
        self.data = data
        self._network = network
        self.address = address
        self._private_ip = None



    @property
    def private_ip():
        """
        Gets the private ip address of the member node
        """
        if not self._private_ip:
            timeout = 120
            while not self.data['config']['ipAssignments'] and timeout:
                timeout -= 2
                time.sleep(2)
                self._refresh()
            if not not self.data['config']['ipAssignments']:
                raise ValueError('Cannot get private ip address for zerotier member')
            self._private_ip = self.data['config']['ipAssignments'][0]
        return self._private_ip


    def _refresh(self):
        """
        Refresh the data of the member by querying the lastest info from the server
        """
        member = self._network.member_get(address=self.address)
        self.data = member.data


    def _update_authorization(self, authorize=True, timeout=30):
        """
        Update authorization setting
        """
        # check if the network is private/public, it does not make sense to authorize on public nets
        if self._network.config['private'] is False:
            self.logger.warn('Cannot authorize on public network.')
            return
        if self.data['config']['authorized'] != authorize:
            data = copy.deepcopy(self.data)
            data['config']['authorized'] = authorize
            self._network._client.network.updateMember(data=data, address=self.address, id=self._network.id)
            self._refresh()
            timeout_ = timeout
            while self.data['config']['authorized'] != authorize and timeout_:
                self._refresh()
                time.sleep(2)
                timeout_ -= 2
            if self.data['config']['authorized'] != authorize:
                self.logger.warn('{}uthorization request sent but data is not updated after {} seconds'.format('A' if authorize else 'Dea', timeout))
        else:
            self.logger.info("Member {}/{} already {}".format(self._network.id, self.address, 'authorized' if authorize else 'deauthorized'))



    def authorize(self, timeout=30):
        """
        Authorize the member if not already authorized

        @param timeout: Timeout to wait until giving up updating the current state of the member
        """
        self._update_authorization(authorize=True, timeout=timeout)


    def deauthorize(self, timeout=30):
        """
        Deauthorize the member if already authorized

        @param timeout: Timeout to wait until giving up updating the current state of the member
        """
        self._update_authorization(authorize=False, timeout=timeout)



class ZeroTierNetwork(JSBASE):
    """
    Represent a zerotier network
    """
    def __init__(self, network_id, name, description, config, client):
        """
        Initialize new network
        """
        JSBASE.__init__(self)
        self.id = network_id
        self.name = name
        self.description = description
        self.config = config
        self._client = client


    def members_list(self, raw=False):
        """
        Lists the members of the current network

        @param raw: If true, then members info will be returned as dict and not @NetworkMember objects
        """
        resp = self._client.network.listMembers(id=self.id)
        if resp.status_code != 200:
            msg = 'Failed to list network memebers. Error: {}'.format(resp.text)
            self.logger.error(msg)
            raise RuntimeError(msg)
        items=resp.json()

        return items if raw else self._create_netork_memebers_from_dict(items=items)


    def member_get(self, address='', name='', public_ip='', private_ip=''):
        """
        Retrieves a member of the network that match the given filter
        @TODO: handle conflict between filters like providing two filters that conflict with each other
        """
        filters = [address, name, public_ip, private_ip]
        if not any(filters):
            msg = 'At least one filter need to be specified'
            self.logger.error(msg)
            raise RuntimeError(msg)

        filters_map = dict(zip(['nodeId', 'name', 'physicalAddress', 'private_ip'], filters))
        members = self.members_list(raw=True)
        result = None
        for member in members:
            for filter_name, filter_value in filters_map.items():
                if filter_name == 'private_ip' and filter_value and filter_value in member['config']['ipAssignments']:
                    result = self._create_netork_memebers_from_dict(items=[member])[0]
                    break
                elif filter_name !='private_ip' and filter_value and filter_value == member[filter_name]:
                    result = self._create_netork_memebers_from_dict(items=[member])[0]
                    break

        if result is None:
            msg = 'Cannot find a member that match the provided filters'
            self.logger.error(msg)
            raise RuntimeError(msg)
        return result


    def _create_netork_memebers_from_dict(self, items):
        """
        Convert network members info into @NetworkMember objects
        """
        result = []
        for item in items:
            result.append(NetworkMember(network=self, address=item['nodeId'], data=item))
        return result


    def member_delete(self, address):
        """
        Deletes a member from the network
        """
        resp = self._client.network.deleteMember(address=address, id=self.id)
        if resp.status_code != 200:
            msg = 'Failed to delete member. Error: {}'.format(resp.text)
            self.logger.error(msg)
            raise RuntimeError(msg)

        return True

TEMPLATE = """
token_ = ""
"""

class ZerotierClient(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        super().__init__(instance=instance, data=data, parent=parent, template=TEMPLATE, interactive=interactive)

        if not self.config.data['token_']:
            self.configure()
        if not self.config.data['token_']:
            raise RuntimeError("Missing auth token in config instance {}".format(instance))
        self.client = zerotier.client.Client()
        self.client.set_auth_header("Bearer " + self.config.data['token_'])
        # self._client = ZerotierClientInteral(self.config.data['token_'])
        self._defaultnet = None


    def networks_list(self):
        """
        Lists all the networks for that belongs to the current instance
        """
        resp = self.client.network.listNetworks()
        if resp.status_code != 200:
            msg = 'Failed to list networks. Error: {}'.format(resp.text)
            self.logger.error(msg)
            raise RuntimeError(msg)
        return self._network_creates_from_dict(items=resp.json())


    def network_get(self, network_id):
        """
        Retrieves details information about a netowrk

        @param network_id: ID of the network
        """
        resp = self.client.network.getNetwork(id=network_id)
        if resp.status_code != 200:
            msg = 'Failed to retrieve network. Error: {}'.format(resp.text)
            self.logger.error(msg)
            raise RuntimeError(msg)
        return self._network_creates_from_dict(items=[resp.json()])[0]


    def _network_creates_from_dict(self, items):
        """
        Will create network objects from a dictionary format
        """
        result = []
        for item in items:
            result.append(ZeroTierNetwork(network_id=item['id'], name=item['config']['name'],
                        description=item['description'], config=item['config'], client=self.client))
        return result


    def network_create(self, public, subnet=None, name=None, auto_assign=True, routes=None):
        """
        Create new network
        """

        if routes is None:
            routes = []
        subnet_info = None
        if subnet is not None:
            net = ipcalc.Network(subnet)
            routes.append({
                'target': subnet,
                'via': None,
            })
            subnet_info = [{
                'ipRangeStart': net.host_first().dq,
                'ipRangeEnd': net.host_last().dq,
            }]

        config = {
            'private': not public,
            'v4AssignMode': {
                'zt': auto_assign
            },
            'routes': routes,
        }
        if subnet_info:
            config.update({
                'ipAssignmentPools': subnet_info,
            })

        if name:
            config.update({'name': name})

        data = {
            'config': config,
        }
        resp = self.client.network.createNetwork(data=data)
        if resp.status_code != 200:
            msg = "Failed to create network. Error: {}".format(resp.text)
            self.logger.error(msg)
            raise RuntimeError(msg)
        return self._network_creates_from_dict([resp.json()])[0]


    def network_delete(self, network_id):
        """
        Delete netowrk

        @param network_id: ID of the network to delete
        """
        resp = self.client.network.deleteNetwork(id=network_id)
        if resp.status_code != 200:
            msg = "Failed to delete network. Error: {}".format(resp.text)
            self.logger.error(msg)
            raise RuntimeError(msg)
        return True
