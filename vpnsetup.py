#!/usr/bin/env python3

import json
import os
import sys

from digitalocean.client import DropletClient

from vpn.config import ConfigurationController

from http.client import HTTPSConnection

from paramiko.rsakey import RSAKey
from paramiko.client import SSHClient

class ExternalIPClient(HTTPSConnection):
    def __init__(self):
        super().__init__(host='api.ipify.org')

    def query(self):
        self.request("GET", "/", None, {})
        return self.getresponse().read().decode('ascii')

def prompt(resource):
    print('Enter {}:'.format(resource))
    return sys.stdin.readline()

def generate_ssh_key(id_rsa_name):
    if os.path.isfile(id_rsa_name):
        print('SSH key file already exists - using key...')
    else:
        priv = RSAKey.generate(2048)
        priv.write_private_key_file(id_rsa_name)

    pub = RSAKey.from_private_key_file(id_rsa_name)
    return 'ssh-rsa {}'.format(pub.get_base64())

def main():
    if len(sys.argv) < 3:
        print('USAGE: vpn-setup.py [VPN_NAME] [SSH_PRIV_KEY_PATH]')
        sys.exit(0)

    public_ip_client = ExternalIPClient()
    public_ip = public_ip_client.query()

    print('Generating SSH key for VPN box')
    pubkey = generate_ssh_key(sys.argv[2])

    print('Starting hardened VPN configuration')
    client = DropletClient('api.digitalocean.com', os.environ.get('API_KEY') or prompt('Digital Ocean API key'))
    pubkey_id = client.pubkey(sys.argv[2], pubkey)
    if pubkey_id is None:
        sys.exit(1)
    droplet_id, droplet_ip = client.droplet(sys.argv[1], 'ams2', 's-1vcpu-1gb', 'ubuntu-18-04-x64',
            ssh_keys=[pubkey_id])
    if droplet_id is None:
        sys.exit(1)
    client.firewall('ssh-from-host', [droplet_id],
            [{'protocol': 'tcp', 'ports': '22', 'sources': { 'addresses': public_ip }}],
            [{'protocol': 'tcp', 'ports': '1-65535', 'destinations': { 'addresses': '0.0.0.0/0' }},
             {'protocol': 'udp', 'ports': '1-65535', 'destinations': { 'addresses': '0.0.0.0/0'}}])

    ssh = ConfigurationController(droplet_ip, sys.argv[2])
    ssh.install_packages()
    ssh.copy_setup_scripts()
    ssh.run_setup()

if __name__ == '__main__':
    main()
