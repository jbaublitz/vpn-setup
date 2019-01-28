vpn-setup
=========

This role is for automation of a hardened VPN setup on Digital Ocean

Requirements
------------

requests

Role Variables
--------------

TODO

Dependencies
------------

None

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
