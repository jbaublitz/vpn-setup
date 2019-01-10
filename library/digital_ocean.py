#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

import requests

class DO():
    def __init__(self, module, result, api_token, base_url='https://api.digitalocean.com/v2'):
        self.module = module
        self.result = result
        self.api_token = api_token
        self.base_url = base_url

    def request(self, method, endpoint, json=None, endpoint_is_absolute=False):
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer {}'.format(self.api_token)
        try:
            if endpoint_is_absolute:
                url = endpoint
            else:
                url = '{}{}'.format(self.base_url, endpoint)

            json_response = requests.request(method, url, json=json, headers=headers).json()
        except Exception as e:
            self.module.fail_json(msg=e, **self.result)

        return json_response 

    def list_droplets(self):
        droplets = []
        json_response = self.request('GET', '/droplets')
        if 'droplets' not in json_response:
            self.module.fail_json(msg="Invalid API response: {}".format(json_response), **self.result)
        droplets.extend(json_response['droplets'])
        while 'pages' in json_response['links'] and 'next' in json_response['links']['pages']:
            json_response = requests.request(method, absolute_url=json_response['links']['pages']['next'])
            droplets.extend(json_response['droplets'])

        return droplets 

def droplet_request(module, result, api_token, name, region_id, image_id, size_id, ssh_key_ids=[]):
    do = DO(module, result, api_token)
    droplets = do.list_droplets()

    for droplet in droplets:
        if droplet['name'] == name:
            module.exit_json(droplet=droplet, **result)
    droplet_json_response = do.request('POST', '/droplets', {'name': name, 'region': region_id,
        'size': size_id, 'image': image_id, 'ssh_keys': ssh_key_ids})
    result['changed'] = True
    return droplet_json_response

def run_module():
    module_args = dict(
        api_token=dict(type='str', required=True),
        name=dict(type='str', required=True),
        region_id=dict(type='str', required=True),
        image_id=dict(type='str', required=True),
        size_id=dict(type='str', required=True),
        ssh_key_ids=dict(type='list'),
    )

    result = dict(changed=False, original_message='', message='')

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
            
    if module.check_mode:
        return result

    droplet = droplet_request(module, result, module.params.get('api_token'),
            module.params.get('name'), module.params.get('region_id'),
            module.params.get('image_id'), module.params.get('size_id'),
            module.params.get('ssh_key_ids'))

    module.exit_json(droplet=droplet['droplet'], **result)

def main():
    run_module()

if __name__ == '__main__':
    main()
