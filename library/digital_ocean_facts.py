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

def droplet_request(module, result, api_token, name):
    do = DO(module, result, api_token)
    droplets_json = do.request('GET', '/droplets', None)
    if 'droplets' not in droplets_json:
        module.fail_json(msg='Invalid response from API: {}'.format(keys_json), **result)

    for droplet in droplets_json['droplets']:
        if droplet['name'] == name:
            module.exit_json(droplet=droplet, **result)
    module.exit_json(droplet={}, **result)

def run_module():
    module_args = dict(
        api_token=dict(type='str', required=True),
        name=dict(type='str', required=True),
    )

    result = dict(changed=False, original_message='', message='')

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
            
    if module.check_mode:
        return result

    droplet_request(module, result, module.params.get('api_token'),
            module.params.get('name'))

def main():
    run_module()

if __name__ == '__main__':
    main()
