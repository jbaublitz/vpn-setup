# vpn-setup
Configuration scripts for setting up a cloud-hosted VPN node

## Invocation
The invocation is meant to be incredibly simple.

```
API_KEY=[DO_API_KEY] python -m vpn-setup [VPN_NODE_NAME] [PATH_TO_SSH_KEY]
```

is the current recommended way to run this.

## Why not use Ansible?
It's true, I'm emulating the idempotent behavior of Ansible in raw Python code.

Here are a few reasons I decided to do this:
* At the time of writing this code, no modules were available for Digital Ocean firewall rules
* There is a need for interactive input and output including scanning a QR code for the 2FA
registration piece that would have been non-trival in Ansible
* At one point in the script, the firewall rules lock down SSH except through the VPN - to fully
automate this, I need to spin off a process that lives after the connection is killed as a daemon
to finish configuring the VPN and to restart sshd so it only listens on the tun interface, also
non-trivial in Ansible
