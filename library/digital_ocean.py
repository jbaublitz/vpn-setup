#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

import requests

class DO():
    def __init__(self, module, result, api_token, base_url='https://api.digitalocean.com/v2'):
        self.module = module
        self.result = result
        self.api_token = api_token
        self.base_url = base_url

    def request(self, method, endpoint, json):
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer {}'.format(self.api_token)
        try:
            json_response = requests.request(method, '{}{}'.format(self.base_url, endpoint),
                    json=json, headers=headers).json()
        except Exception as e:
            self.module.fail_json(msg=e, **self.result)

        return json_response

def droplet_request(module, result, api_token, name, region_id, image_id, size_id, ssh_key_ids=[]):
    do = DO(module, result, api_token)
    droplets_json = do.request('GET', '/droplets', None)
    if 'droplets' not in droplets_json:
        module.fail_json(msg='Invalid response from API: {}'.format(keys_json), **result)

    for droplet in droplets_json['droplets']:
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

    module.exit_json(droplet=droplet, **result)

def main():
    run_module()

if __name__ == '__main__':
    main()