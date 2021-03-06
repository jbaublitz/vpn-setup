#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

import json
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

            json_response = requests.request(method, '{}{}'.format(self.base_url, endpoint),
                    json=json, headers=headers).json()
        except Exception as e:
            self.module.fail_json(msg=e, **self.result)

        return json_response

    def list_firewalls(self):
        firewalls = []
        json_response = self.request('GET', '/firewalls')
        if 'firewalls' not in json_response:
            self.module.fail_json(msg="Invalid API response: {}".format(json_response), **self.result)
        firewalls.extend(json_response['firewalls'])
        while 'pages' in json_response['links'] and 'next' in json_response['links']['pages']:
            json_response = requests.request(method, absolute_url=json_response['links']['pages']['next'])
            firewalls.extend(json_response['firewalls'])

        return firewalls

def firewall_request(module, result, api_token, name, inbound_rules, outbound_rules, droplet_ids):
    do = DO(module, result, api_token)
    firewall_json = do.list_firewalls()

    for firewall in firewall_json:
        if firewall['name'] != name:
            continue

        equal = True
        if set((rule['protocol'], frozenset(rule['sources']['addresses'])) for rule in inbound_rules) != \
                set((rule['protocol'], frozenset(rule['sources']['addresses'])) for rule in firewall['inbound_rules']):
            equal = False
        if droplet_ids != [str(i) for i in firewall['droplet_ids']]:
            equal = False

        if equal:
            module.exit_json(firewall=firewall, **result)
        else:
            firewall_change_response = do.request('PUT', '/firewalls/{}'.format(firewall['id']),
                {'name': name, 'inbound_rules': inbound_rules, 'outbound_rules': outbound_rules,
                'droplet_ids': droplet_ids})
            if 'firewall' not in firewall_change_response:
                module.fail_json(msg='Invalid API response: {}'.format(firewall_change_response), **result)
            result['changed'] = True
            module.exit_json(firewall=firewall_change_response, **result)

    firewall_json_response = do.request('POST', '/firewalls', {'name': name,
        'inbound_rules': inbound_rules, 'outbound_rules': outbound_rules,
        'droplet_ids': droplet_ids})
    result['changed'] = True
    return firewall_json_response

def run_module():
    module_args = dict(
        api_token=dict(type='str', required=True),
        name=dict(type='str', required=True),
        inbound_rules=dict(type='list'),
        outbound_rules=dict(type='list'),
        droplet_ids=dict(type='list'),
    )

    result = dict(changed=False, original_message='', message='')

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
            
    if module.check_mode:
        return result

    firewall_request(module, result, module.params.get('api_token'), module.params.get('name'),
            module.params.get('inbound_rules'), module.params.get('outbound_rules'),
            module.params.get('droplet_ids'))

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
