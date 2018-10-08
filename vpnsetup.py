#!/usr/bin/env python3

import os
import sys

from digitalocean.client import DropletClient

def prompt(resource):
    print('Enter {}:'.format(resource))
    return sys.stdin.readline()

def main():
    print('Starting hardened VPN configuration')
    client = DropletClient('api.digitalocean.com', os.environ.get('API_KEY') or prompt('Digital Ocean API key'))
    client.droplet('my-test', 'ams2', 's-1vcpu-1gb', 'ubuntu-18-04-x64')

if __name__ == '__main__':
    main()
