import io
import socket
import time

import avh_api
import websocket

DEFAULT_INSTANCE_FLAVOR = "corstone-300fvp"
DEFAULT_INSTANCE_OS = "FastModels"
DEFAULT_INSTANCE_OS_VERSION = "11.16.14"

DEFAULT_DEVICE_BOOTED_OUTPUT = "Info: /OSCI/SystemC: Simulation stopped by user."


class AvhFastModelsInstance:
    def __init__(
        self,
        avh_client,
        name,
        flavor=DEFAULT_INSTANCE_FLAVOR,
        os=DEFAULT_INSTANCE_OS,
        os_version=DEFAULT_INSTANCE_OS_VERSION,
    ):
        self.avh_client = avh_client
        self.name = name
        self.flavor = flavor
        self.os = os
        self.os_version = os_version
        self.instance_id = None
        self.console = None

    def create(self):
        self.instance_id = self.avh_client.create_instance(
            name=self.name,
            flavor=self.flavor,
            os=self.os_version,
            osbuild=self.os,
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

        if self.console is not None:
            self.console.close()

        self.console = websocket.create_connection(
            self.avh_client.instance_console_url(self.instance_id)
        )

    def wait_for_os_boot(self, booted_output=DEFAULT_DEVICE_BOOTED_OUTPUT, timeout=240):
        start_time = time.monotonic()

        console_log = ""

        while True:
            console_log += self.console.recv().decode()

            if booted_output in console_log:
                break
            elif (time.monotonic() - start_time) > timeout:
                raise Exception(
                    f"Timed out waiting for OS to boot for instance id {self.instance_id}",
                    f"Did not find {booted_output} in {console_log}",
                )

            time.sleep(1.0)

        # sleep is needed here to avoid corrupting the license file on reboot ...
        # time.sleep(120.0)

    def wait_for_state_rebooting(self, timeout=240):
        start_time = time.monotonic()

        while True:
            instance_state = self.avh_client.instance_state(self.instance_id)

            if instance_state == "rebooting":
                break
            elif instance_state == "error":
                raise Exception("VM entered error state")
            elif (time.monotonic() - start_time) > timeout:
                raise Exception(
                    f"Timed out waiting for state 'rebooting' for instance id {self.instance_id}"
                )

            time.sleep(1.0)

    def delete(self):
        if self.console is not None:
            self.console.close()

            self.console = None

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

    def run_elf(self, elf_path, config_path, timeout=120):
        try:
            self.avh_client.upload_vmfile("config-file", config_path, self.instance_id)
        except:
            # TODO: this should not fail
            pass

        try:
            self.avh_client.upload_vmfile("application", elf_path, self.instance_id)
        except:
            # TODO: this should not fail
            pass

        self.avh_client.reboot_instance(self.instance_id)

        self.wait_for_state_rebooting()
        self.wait_for_state_on()

        self.console.settimeout(1.0)

        start_time = time.monotonic()
        output = ""

        while True:
            if (time.monotonic() - start_time) > timeout:
                raise Exception(
                    f"Timed out waiting for '{DEFAULT_DEVICE_BOOTED_OUTPUT}' in console output"
                    f"Current output is {output}"
                )

            try:
                output += self.console.recv().decode()
            except websocket.WebSocketTimeoutException as wste:
                pass

            print("console_log = ", output)

            if DEFAULT_DEVICE_BOOTED_OUTPUT in output:
                break

        return console_log, 0
