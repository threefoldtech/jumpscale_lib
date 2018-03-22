"""
zc = j.clients.zerotier.get(name="geert", data={'token_':"jkhljhbljb"})
mynetworks = zc.list_networks()-> [ZerotierNetwork]
mynetwork = zc.get_network(networkid='khgfghvhgv') -> ZerotierNetwork
zc.create_network(public=True, subnet="10.0.0.0/24", auto_assign=True, routes=[])
mymembers = mynetwork.list_members() -> [ZerotierNetworkMember]
mymember = mynetwork.get_member(address='hfivivk' || name='geert' || public_ip='...' || private_ip='...')
mymember.authorize()
mymember.deauthorize()
"""

from js9 import j

import zerotier
import requests
import json
import copy
import time
import ipcalc

JSConfigFactory = j.tools.configmanager.base_class_configs
JSConfigClient = j.tools.configmanager.base_class_config

TEMPLATE = """
token_ = ""
"""
JSBASE = j.application.jsbase_get_class()


class ZerotierClientInteral(JSBASE):
    def __init__(self, apikey):
        JSBASE.__init__(self)
        self.apikey = apikey
        self.apibase = "https://my.zerotier.com/api"


    def request(self, path, data=None):
        if data is None:
            return requests.get(self.apibase + path, headers={'Authorization': 'Bearer ' + self.apikey})

        else:
            return requests.post(self.apibase + path, headers={'Authorization': 'Bearer ' + self.apikey}, json=data)

    def delete(self, path):
        return requests.delete(self.apibase + path, headers={'Authorization': 'Bearer ' + self.apikey})

    def status(self):
        return self.request("/status").json()

    def user(self, id):
        return self.request("/user/%s" % id).json()

    def networks(self):
        return self.request("/network").json()

    # def network_create(self, name):
    #     data = {
    #         "config": {
    #             "name": name,
    #             "rules": [{"ruleNo": 1, "action": "accept"}],
    #             "v4AssignMode": "zt",
    #             "routes": [{"target": "10.147.17.0/24", "via": None, "flags": 0, "metric": 0}],
    #             "ipAssignmentPools": [{"ipRangeStart": "10.147.17.1", "ipRangeEnd": "10.147.17.254"}]
    #         }
    #     }

    #     return self.request("/network", data).json()

    def network_delete(self, id):
        return self.delete("/network/%s" % id)


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


    def _refresh(self):
        """
        Refresh the data of the member by querying the lastest info from the server
        """
        member = self._network.get_member(address=self.address)
        self.data = member.data


    def authorize(self, timeout=30):
        """
        Authorize the member if not already authorized

        @param timeout: Timeout to wait until giving up updating the current state of the member
        """
        # check if the network is private/public, it does not make sense to authorize on public nets
        if self._network.config['private'] is False:
            self.logger.warn('Cannot authorize on public network.')
            return
        if self.data['config']['authorized'] is False:
            data = copy.deepcopy(self.data)
            data['config']['authorized'] = True
            self._network._client.network.updateMember(data=data, address=self.address, id=self._network.id)
            self._refresh()
            timeout_ = timeout
            while self.data['config']['authorized'] is False and timeout_:
                self._refresh()
                time.sleep(2)
                timeout_ -= 2
            if self.data['config']['authorized'] is False:
                self.logger.warn('Authorization request sent but data is not updated after {} seconds'.format(timeout))
        else:
            self.logger.info("Member {}/{} already authorized".format(self._network.id, self.address))


    def deauthorize(self, timeout=30):
        """
        Deauthorize the member if already authorized

        @param timeout: Timeout to wait until giving up updating the current state of the member
        """
        # check if the network is private/public, it does not make sense to authorize on public nets
        if self._network.config['private'] is False:
            self.logger.warn('Cannot deauthorize on public network.')
            return
        if self.data['config']['authorized'] is True:
            data = copy.deepcopy(self.data)
            data['config']['authorized'] = False
            self._network._client.network.updateMember(data=data, address=self.address, id=self._network.id)
            self._refresh()
            timeout_ = timeout
            while self.data['config']['authorized'] is True and timeout_:
                self._refresh()
                time.sleep(2)
                timeout_ -= 2
            if self.data['config']['authorized'] is True:
                self.logger.warn('Deauthorization request sent but data is not updated after {} seconds'.format(timeout))
        else:
            self.logger.info("Member {}/{} is not authorized".format(self._network.id, self.address))




class ZeroTierNetwork(JSBASE):
    """
    Represent a zerotier network
    """
    def __init__(self, network_id, name, description, config, client):
        """
        Initialize new netowrk
        """
        JSBASE.__init__(self)
        self.id = network_id
        self.name = name
        self.description = description
        self.config = config
        self._client = client


    def list_members(self, raw=False):
        """
        Lists the members of the current network

        @param raw: If true, then members info will be returned as dict and not @NetworkMember objects
        """
        resp = self._client.network.listMembers(id=self.id)
        if resp.status_code != 200:
            msg = 'Failed to list network memebers. Error: {}'.format(resp.text)
            self.logger.error(msg)
            raise j.exceptions.RuntimeError(msg)
        items=resp.json()

        return items if raw else self._create_netork_memebers_from_dict(items=items)


    def get_member(self, address='', name='', public_ip='', private_ip=''):
        """
        Retrieves a member of the network that match the given filter
        @TODO: handle conflict between filters like providing two filters that conflict with each other
        """
        filters = [address, name, public_ip, private_ip]
        if not any(filters):
            msg = 'At least one filter need to be specified'
            self.logger.error(msg)
            raise j.exceptions.RuntimeError(msg)

        filters_map = dict(zip(['nodeId', 'name', 'physicalAddress', 'private_ip'], filters))
        members = self.list_members(raw=True)
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
            raise j.exceptions.RuntimeError(msg)
        return result


    def _create_netork_memebers_from_dict(self, items):
        """
        Convert network members info into @NetworkMember objects
        """
        result = []
        for item in items:
            result.append(NetworkMember(network=self, address=item['nodeId'], data=item))
        return result


    def delete_member(self, address):
        """
        Deletes a member from the network
        """
        resp = self._client.network.deleteMember(address=address, id=self.id)
        if resp.status_code != 200:
            msg = 'Failed to delete member. Error: {}'.format(resp.text)
            self.logger.error(msg)
            raise j.exceptions.RuntimeError(msg)

        return True



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


    def list_networks(self):
        """
        Lists all the networks for that belongs to the current instance
        """
        resp = self.client.network.listNetworks()
        if resp.status_code != 200:
            msg = 'Failed to list networks. Error: {}'.format(resp.text)
            self.logger.error(msg)
            raise j.exceptions.RuntimeError(msg)
        return self._create_networks_from_dict(items=resp.json())


    def get_network(self, network_id):
        """
        Retrieves details information about a netowrk

        @param network_id: ID of the network
        """
        resp = self.client.network.getNetwork(id=network_id)
        if resp.status_code != 200:
            msg = 'Failed to retrieve network. Error: {}'.format(resp.text)
            self.logger.error(msg)
            raise j.exceptions.RuntimeError(msg)
        return self._create_networks_from_dict(items=[resp.json()])[0]


    def _create_networks_from_dict(self, items):
        """
        Will create network objects from a dictionary format
        """
        result = []
        for item in items:
            result.append(ZeroTierNetwork(network_id=item['id'], name=item['config']['name'],
                        description=item['description'], config=item['config'], client=self.client))
        return result


    def create_network(self, public, subnet, auto_assign=True, routes=None):
        """
        Create new network
        """
        if routes is None:
            routes = []
        config = {
            'private': not public,
            'v4AssignMode': {
                'zt': auto_assign
            },
            'routes': routes,
        }
        data = {
            ''
        }


    def memberAuthorize(self, zerotierNetworkId, ip_pub):
        res = self.client.network.listMembers(id=zerotierNetworkId).json()
        members = [item for item in res if item['physicalAddress'] == ip_pub]
        if not members:
            raise RuntimeError('no such memeber as %s' % zerotierNetworkId)
        member = members[0]
        if member['config']["authorized"] is False:
            id = member["nodeId"]
            member['config']['authorized'] = True
            data = json.dumps(member)
            self._client.request("/network/%s/member/%s" % (zerotierNetworkId, id), member)
            self.logger.info('[+] authorized %s on %s' % (member['physicalAddress'], zerotierNetworkId))

    def networksGet(self):
        """
        returns [(id,name,onlinecount)]
        """
        res0 = self.client.network.listNetworks().json()
        res = []
        for item in res0:
            res.append((item["id"], item["config"]["name"],
                        item["onlineMemberCount"]))
        return res

    def networkMembersGet(self, networkId, online=True):
        res = self.client.network.listMembers(id=networkId).json()
        result = []
        for item in res:
            res2 = {}
            res2["authorized"] = item["config"]["authorized"]
            # item["creationTime"]
            res2["name"] = item["name"]
            res2["id"] = item["id"]
            if online and item["online"] is False:
                continue
            res2["online"] = item["online"]
            res2["lastOnlineHR"] = j.data.time.epoch2HRDateTime(
                item["lastOnline"] / 1000)
            res2["lastOnline"] = item["lastOnline"]
            res2["ipaddr_priv"] = item["config"]["ipAssignments"]
            res2["ipaddr_pub"] = item["physicalAddress"].split(
                "/")[0] if item["physicalAddress"] else None
            result.append(res2)
        return result

    def networkMemberGetFromIPPub(self, ip_pub, networkId, online=True):
        res = self.networkMembersGet(networkId, online)

        res = [item for item in res if item['ipaddr_pub'] == ip_pub]

        if len(res) is 0:
            raise RuntimeError(
                "Did not find network member with ipaddr:%s" % ip_pub)

        return res[0]


class ZerotierFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.zerotier"
        self.__imports__ = "zerotier"
        self.connections = {}
        JSConfigFactory.__init__(self, ZerotierClient)
