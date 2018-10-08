#!/usr/bin/env python3

from distutils.core import setup
import setuptools

setup(name="vpn-setup",
      version="0.1.0",
      description="Automated setup for VPNs on Digital Ocean",
      author="John Baublitz",
      author_email="john.m.baublitz@gmail.com",
      url="https://github.com/jbaublitz/vpn-setup",
      scripts=["vpnsetup.py"],
      packages=["digitalocean", "vpn"],
      install_requires=[
          'paramiko',
      ])
