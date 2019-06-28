vpn-setup
=========

This role is for automation of a hardened VPN setup on Digital Ocean

Requirements
------------

`--extravars="temppass=[INITIAL_VPN_PASSWORD]"` is required to successfully run this playbook.

Variables
--------------

* `temppass=[ADMIN_USER_PASSWORD]` is required and used to set up admin password on new VPN
* `vpn_connected=yes` should only be used when running while connected to an already provisioned VPN
using this script
* `droplet_name=[NAME]` overrides the droplet name
* `do_hosted_region=[DIGITAL_OCEAN_HOSTED_REGION_CODE]` changes where this VPN is hosted
* `rsa_key_size=[NUMBER]` specifies the size of the key size of any RSA key generated
* `ca_expiration=[NUMBER]h` specifes number of hours until VPN certificate expiration
* `ansible_ssh_private_key_file=[PATH]` overrides SSH key used in ansible


TODO

Dependencies
------------

`requests` library - currently used in `library/` directory-contained modules to do the API requests
until Digital Ocean support is better in Ansible


Example Playbook
----------------

Invocation should be as follows:

`DO_API_KEY=[KEY] ansible-playbook -K -i vpn-setup/inventory vpn-setup.yml [--extra-vars="vpn_connected=yes"]`

where `vpn-setup.yml` contains the following:

```
---
- hosts: localhost
  connection: local
  roles:
  - { role: vpn-setup, target: local }
- hosts: vpn 
  remote_user: root
  gather_facts: no
  tasks:
  - name: Wait for SSH to become available
    wait_for_connection:
- hosts: vpn
  remote_user: root
  roles:
  - { role: vpn-setup, target: vpn }
- hosts: localhost
  connection: local
  roles:
  - { role: vpn-setup, target: local_connected }
```

License
-------

BSD

Author Information
------------------

John Baublitz

Freenode IRC handle: jbaublitzzz
