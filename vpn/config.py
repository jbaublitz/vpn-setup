import os

import paramiko
from paramiko.client import SSHClient
from paramiko.rsakey import RSAKey 

class ConfigurationController(SSHClient):
    def __init__(self, host, key_filename):
        super().__init__()
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect(host, username='root', pkey=RSAKey.from_private_key_file(key_filename))

    def __run_command__(self, cmd):
        print(cmd)
        stdin, stdout, stderr = self.exec_command(cmd)
        print('STDOUT:\n{}\nSTDERR:\n{}'.format(stdout.read().decode('utf-8'),
            stderr.read().decode('utf-8')))

    def install_packages(self):
        self.__run_command__('apt update')
        self.__run_command__('apt install -y libpam-google-authenticator openvpn golang-cfssl python3')

    def copy_setup_scripts(self):
        transport = self.get_transport()
        sftp = transport.open_sftp_client()

        sftp_file = sftp.file('/root/setup-script.py', mode='w')
        sftp_file.write(open('{}/setup-script.py'.format(os.path.dirname(__file__))).read())
        sftp_file.close()

    def run_setup(self):
        self.__run_command__('/usr/bin/python3 /root/setup-script.py')
