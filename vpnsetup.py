#!/usr/bin/env python3

import os
import sys

from paramiko.rsakey import RSAKey

from digitalocean.client import DropletClient

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

    print('Generating SSH key for VPN box')
    pubkey = generate_ssh_key(sys.argv[2])

    print('Starting hardened VPN configuration')
    client = DropletClient('api.digitalocean.com', os.environ.get('API_KEY') or prompt('Digital Ocean API key'))
    pubkey_id = client.pubkey(sys.argv[2], pubkey)
    if pubkey_id is None:
        sys.exit(1)
    droplet_id = client.droplet(sys.argv[1], 'ams2', 's-1vcpu-1gb', 'ubuntu-18-04-x64',
            ssh_keys=[pubkey_id])
    if droplet_id is None:
        sys.exit(1)

if __name__ == '__main__':
    main()
