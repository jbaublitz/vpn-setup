import json

from http.client import HTTPSConnection

def prompt():
    return stdin.readline()

class DropletClient(HTTPSConnection):
    def __init__(self, host='api.digitialocean.com', api_key=None):
        self.digital_ocean_api_key = api_key
        super().__init__(host)

    def droplet(self, name, region, size, image, **kwargs):
        print("Droplet creation started")
        request_body = {'name': name, 'region': region, 'size': size, 'image': image}
        request_body.update(kwargs)
        headers = {"Content-Type": "application/json", "Authorization": "Bearer {}"
                .format(self.digital_ocean_api_key)}
        self.request("POST", "/v2/droplets", json.dumps(request_body), headers)
        print("Droplet creation response: {}".format(self.getresponse.read()))
