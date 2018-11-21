from Jumpscale import j
import json
import requests
import pickle
import collections


JSConfigBase = j.tools.configmanager.base_class_config

BASE_API = "http://127.0.0.1:9993"
controller = collections.defaultdict()

class ZeroTierController():
    def __init__(self, instance='main', data={}, parent=None, interactive=None):
        self.set_headers()
        self.load_ctrlr()
        self.set_id()


    def ddict(self):
        return collections.defaultdict()

    def get_filepath(self):
        """Get filepath """
        return "/var/lib/zerotier-one"

    @property
    def save_ctrlr(self):
        with open(self.get_filepath()+"/ctrlr.pickle", "wb") as file:
            pickle.dump(dict(controller), file)

    def request(self, url, payload=None, method="get"):
        """Simple request wrapper
        Takes a couple of variables and wraps around the requests
        module
        Args:
            url: API URL
            method: Query method (default: {"get"})
            payload: JSON payload (default: {None})
        Returns:
            Dataset as result from query
            JSON Object
        """
        r = None
        if payload is not None:
            r = requests.post(
                BASE_API+url, headers=controller["headers"], json=payload)
        elif method == "get":
            r = requests.get(
                BASE_API+url, headers=controller["headers"])
        elif method == "delete":
            r = requests.delete(
                BASE_API+url, headers=controller["headers"])
        return r.json()
    
    def set_headers(self):
        """Sets authentication headers globally
        Automatically detect system and reads authtoken.secret
        to set authenticaiton headers used in request method
        globally.
        """
        with open(self.get_filepath()+"/authtoken.secret") as file:
            controller["headers"] = {"X-ZT1-Auth": file.read().split('\n')[0]}
            controller["network"] = {}
            print(controller)

    def set_id(self):
        controller["ztid"] = self.request("/status").get("address")

    def load_ctrlr(self):
        global controller
        try:
            with open(self.get_filepath()+"/ctrlr.pickle", "rb") as file:
                controller = pickle.load(file)
        except:
            controller = self.ddict()

    def network_add(self, network_id):
        controller["network"][network_id] = (self.request("/controller/network/"+network_id, {}))
        return self.request("/controller/network/"+network_id, {})

    def network_del(self, network_id):
        if network_id in controller["network"]:
            controller["network"][network_id].clear()
            del controller["network"][network_id]
        return self.request("/controller/network/"+controller, method="delete")

    def network_info(self, network_id):
        controller["network"][network_id] = self.request("/controller/network/"+network_id)
        return controller["network"][network_id]

    def networks_list(self):
        nwids = self.request("/controller/network")
        for nwid in nwids:
            self.network_info(nwid)
        return controller

    def member_auth(self, network_id, adress):

        return self.request("/controller/network/"+network_id+"/member/"+adress, {'authorized':'true'})

    def member_deauth(self, network_id, adress):

        return self.request("/controller/network/"+network_id+"/member/"+adress, {'authorized':'false'})

    def member_list(self, network_id):
        ztids = self.request("/controller/network/"+network_id+"/member")
        return ztids