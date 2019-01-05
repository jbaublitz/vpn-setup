#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

import requests

class DO():
    def __init__(self, module, result, api_token, base_url='https://api.digitalocean.com/v2'):
        self.module = module
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

def ssh_key_request(module, result, api_token, name, ssh_pub_key):
    do = DO(module, result, api_token)
    keys_json = do.request('GET', '/account/keys', None)
    if 'ssh_keys' not in keys_json:
        module.fail_json(msg='Invalid response from API: {}'.format(keys_json), **result)

    for key in keys_json['ssh_keys']:
        if key['name'] == name:
            if key['public_key'] == ssh_pub_key:
                module.exit_json(ssh_key=key, **result)
            else:
                do.request('DELETE', '/account/keys/{}'.format(key['id']), None)
    key = do.request('POST', '/account/keys', {'name': name, 'public_key': ssh_pub_key})
    result['changed'] = True
    return key

def run_module():
    module_args = dict(
        api_token=dict(type='str', required=True),
        name=dict(type='str', required=True),
        ssh_pub_key=dict(type='str', required=True),
    )

    result = dict(changed=False, original_message='', message='')

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
            
    if module.check_mode:
        return result

    key = ssh_key_request(module, result, module.params.get('api_token'), module.params.get('name'),
            module.params.get('ssh_pub_key'))
    result['ssh_key'] = key

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
