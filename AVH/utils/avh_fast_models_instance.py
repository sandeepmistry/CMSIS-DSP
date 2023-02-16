import io
import socket
import time

import avh_api
import paramiko

DEFAULT_INSTANCE_FLAVOR = "corstone-300fvp"
DEFAULT_INSTANCE_OS = "FastModels"
DEFAULT_INSTANCE_OS_VERSION = "11.16.14"

DEFAULT_OS_BOOTED_OUTPUT = "Info: /OSCI/SystemC: Simulation stopped by user."

DEFAULT_SSH_USERNAME = "ubuntu"
DEFAULT_SSH_PASSWORD = "password"


class AvhFastModelsInstance:
    def __init__(
        self,
        avh_client,
        name,
        flavor=DEFAULT_INSTANCE_FLAVOR,
        os=DEFAULT_INSTANCE_OS,
        os_version=DEFAULT_INSTANCE_OS_VERSION,
        username=DEFAULT_SSH_USERNAME,
        password=DEFAULT_SSH_PASSWORD,
    ):
        self.avh_client = avh_client
        self.name = name
        self.flavor = flavor
        self.os = os
        self.os_version = os_version
        self.username = username
        self.password = password
        self.instance_id = None
        self.ssh_pkey = None
        self.ssh_key_id = None

    def create(self):
        self.instance_id = self.avh_client.create_instance(
            name=self.name, flavor=self.flavor, os=self.os_version, osbuild=self.os
        )

    def wait_for_state_on(self, timeout=240):
        start_time = time.monotonic()

        while True:
            instance_state = self.avh_client.instance_state(self.instance_id)

            if instance_state == "on":
                break
            elif instance_state == "error":
                raise Exception("VM entered error state")
            elif (time.monotonic() - start_time) > timeout:
                raise Exception(
                    f"Timed out waiting for state 'on' for instance id {self.instance_id}"
                )

            time.sleep(1.0)

    def wait_for_os_boot(self, booted_output=DEFAULT_OS_BOOTED_OUTPUT, timeout=240):
        start_time = time.monotonic()

        while True:
            console_log = self.avh_client.instance_console_log(self.instance_id)

            if booted_output in console_log:
                break
            elif (time.monotonic() - start_time) > timeout:
                raise Exception(
                    f"Timed out waiting for OS to boot for instance id {self.instance_id}",
                    f"Did not find {booted_output} in {console_log}",
                )

            time.sleep(1.0)

    def ssh_client(self, timeout=30):
        if self.ssh_pkey is None:
            self.ssh_pkey = paramiko.ecdsakey.ECDSAKey.generate()

            self.ssh_key_id = self.avh_client.create_ssh_project_key(
                self.name, f"{self.ssh_pkey.get_name()} {self.ssh_pkey.get_base64()}"
            )

        proxy_username = self.avh_client.default_project_id
        proxy_hostname = "proxy.app.avh.arm.com"
        instance_ip = self.avh_client.instance_ip_address(self.instance_id)

        ssh_proxy_client = paramiko.SSHClient()
        ssh_proxy_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_proxy_client.connect(
            hostname=proxy_hostname,
            username=proxy_username,
            pkey=self.ssh_pkey,
            look_for_keys=False,
            timeout=timeout,
        )

        try:
            proxy_sock = ssh_proxy_client.get_transport().open_channel(
                kind="direct-tcpip",
                dest_addr=(instance_ip, 22),
                src_addr=("", 0),
                timeout=timeout,
            )

            ssh_client.connect(
                hostname=instance_ip,
                username=self.username,
                password=self.password,
                sock=proxy_sock,
                timeout=timeout,
                look_for_keys=False,
            )
        except Exception as e:
            raise Exception(
                f"Failled to connect to {instance_ip} via SSH proxy {proxy_username}@{proxy_hostname}"
            )

        return ssh_client

    def delete(self):
        if self.ssh_key_id is not None:
            self.avh_client.delete_ssh_project_key(self.ssh_key_id)

            self.ssh_key_id = None

        if self.instance_id is not None:
            self.avh_client.delete_instance(self.instance_id)

    def wait_for_state_deleted(self, timeout=60):
        if self.instance_id is None:
            return

        start_time = time.monotonic()

        while True:
            try:
                instance_state = self.avh_client.instance_state(self.instance_id)
            except avh_api.exceptions.NotFoundException:
                break

            if (time.monotonic() - start_time) > timeout:
                raise Exception(
                    f"Timedout waiting for instance id {self.instance_id} to be deleted"
                )

            time.sleep(1.0)

        self.instance_id = None

    def run_elf(self, elf_path, config_path, timeout=30):
        ssh_client = self.ssh_client()

        stfp_client = ssh_client.open_sftp()
        stfp_client.put(elf_path, "/tmp/application.elf")
        stfp_client.put(config_path, "/tmp/fvp-config.txt")
        stfp_client.close()
        ssh_client.close()

        ssh_client = self.ssh_client()

        stdin, stdout, stderr = ssh_client.exec_command(
            "./VHT-arm64/VHT_MPS3_Corstone_SSE-300 -f /tmp/fvp-config.txt -a /tmp/application.elf",
            timeout=timeout,
        )
        channel = stdout.channel

        stdout_data = b""

        for i in range(timeout):
            if channel.recv_ready():
                try:
                    stdout_data += stdout.read()
                except TimeoutError:
                    print("TimeoutError")
                except paramiko.buffered_pipe.PipeTimeout:
                    print("paramiko.buffered_pipe.PipeTimeout")
            elif channel.exit_status_ready():
                break
            time.sleep(1.0)

        exit_status = channel.exit_status

        stdin.close()
        stdout.close()
        stderr.close()

        ssh_client.close()

        return stdout_data.decode(), exit_status
