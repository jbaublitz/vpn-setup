import json
import math
import os

from http.client import HTTPSConnection

class DropletClient(HTTPSConnection):
    def __init__(self, host='api.digitialocean.com', api_key=None):
        self.digital_ocean_api_key = api_key
        super().__init__(host)

    def __name_to_id__(self, name, endpoint, key):
        self.request("GET", "{}?per_page=100".format(endpoint), None, {"Authorization": "Bearer {}"
            .format(self.digital_ocean_api_key)})
        response = self.getresponse().read()
        json_response = json.loads(response)
        value = json_response[key]

        total = json_response['meta']['total']
        if total > 100:
            for i in range(2, math.ceil(total / 100) + 1):
                self.request("GET", "{}?per_page=100&page={}".format(endpoint, i),
                             None, {"Authorization": "Bearer {}".format(self.digital_ocean_api_key)})
                response = self.getresponse().read()
                json_response = json.loads(response)
                value += json_response[key]

        entity = [v for v in value if v['name'] == name]
        if len(entity) > 1:
            print('ERROR: Duplicates of {} named {} found! Please remove duplicate names'
                    .format(key, name))
            sys.exit(1)
        elif len(entity) < 1:
            return None
        else:
            return entity[0]['id']

    def __droplet_exists__(self, name):
        return self.__name_to_id__(name, "/v2/droplets", "droplets")

    def droplet(self, name, region, size, image, **kwargs):
        droplet_id = self.__droplet_exists__(name)
        if droplet_id is not None:
            print("Droplet exists - skipping creation step")
            return droplet_id

        print("Droplet creation started")
        request_body = {'name': name, 'region': region, 'size': size, 'image': image}
        request_body.update(kwargs)
        headers = {"Content-Type": "application/json", "Authorization": "Bearer {}"
                .format(self.digital_ocean_api_key)}
        self.request("POST", "/v2/droplets", json.dumps(request_body), headers)
        response = self.getresponse().read()
        try:
            return json.loads(response)['droplet']['id']
        except KeyError:
            print('ERROR - Invalid response: {}'.format(response))
            return None

    def __pubkey_exists__(self, name):
        return self.__name_to_id__(name, "/v2/account/keys", "ssh_keys")

    def pubkey(self, pubkey_path, key_content):
        pubkey_name = os.path.basename(pubkey_path)
        ssh_key_id = self.__pubkey_exists__(pubkey_name)
        if ssh_key_id is not None:
            print("Public key exists - skipping creation step")
            return ssh_key_id

        headers = {"Content-Type": "application/json", "Authorization": "Bearer {}"
                .format(self.digital_ocean_api_key)}
        self.request("POST", "/v2/account/keys", json.dumps({'name': pubkey_name,
            'public_key': key_content}), headers)
        response = self.getresponse().read()
        try:
            return json.loads(response)['ssh_key']['id']
        except KeyError:
            print('ERROR - Invalid response: {}'.format(response))
            return None

    def __firewall_exists__(self, name):
        return self.__name_to_id__(name, "/v2/firewalls", "firewalls")

    def firewall(self, name, rules):
        firewall_id = self.__firewall_exists__(name)
        if firewall_id is not None:
            print("Firewall exists - skipping creation step")
            return firewall_id 

        headers = {"Content-Type": "application/json", "Authorization": "Bearer {}"
                .format(self.digital_ocean_api_key)}
        self.request("POST", "/v2/firewall", json.dumps({'name': name,
            'inbound_rules': rules}), headers)
        response = self.getresponse().read()
        try:
            return json.loads(response)['firewall']['id']
        except KeyError:
            print('ERROR - Invalid response: {}'.format(response))
            return None
