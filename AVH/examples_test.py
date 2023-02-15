import logging
import os
import sys
import unittest

import os

from utils.avh_client import AvhClient
from utils.avh_fast_models_instance import AvhFastModelsInstance

if "AVH_API_TOKEN" not in os.environ:
    raise Exception("Please set AVH_API_TOKEN environment variable!")


class TestCmsisDspExamples(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        stdout_logger_handler = logging.StreamHandler(sys.stdout)
        stdout_logger_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)-8s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        self.logger.addHandler(stdout_logger_handler)

        self.avh_client = AvhClient(os.environ["AVH_API_TOKEN"])

        # TODO: cleanup any left over instances

        self.fast_models_instance = AvhFastModelsInstance(
            self.avh_client, "CMSIS-DSP Examples Test - Corstone-300 FVP"
        )

        self.logger.info("creating instance ...")
        self.addCleanup(self.cleanupInstances)

        self.fast_models_instance.create()
        self.fast_models_instance.wait_for_state_on()

        self.logger.info("waiting for OS to boot ...")
        self.fast_models_instance.wait_for_os_boot()

    def test_arm_bayes_example(self):
        self.logger.info("testing  arm_bayes_example ...")

        expected_output = "".join(
            [
                "Class = 0\r\n",
                "Max proba = -2.899159\r\n",
                "Class = 1\r\n",
                "Max proba = -2.827732\r\n",
                "Class = 2\r\n",
                "Max proba = -3.108092\r\n",
            ]
        )

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_bayes_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn(expected_output, output)

    def cleanupInstances(self):
        self.logger.info("deleting instance ...")
        self.fast_models_instance.delete()

        self.fast_models_instance.wait_for_state_deleted()

        self.avh_client.close()


if __name__ == "__main__":
    unittest.main()


# avh_client = AvhClient(os.environ["AVH_API_TOKEN"])


# print("creating instance")
# fast_models_instance.create()

# print("waiting for instance state on")
# fast_models_instance.wait_for_state_on()

# print("waiting for instance OS to boot")
# fast_models_instance.wait_for_os_boot()


# print(exit_code, output)

# print("deleting instance")
# fast_models_instance.delete()

# print("waiting for instance state deleted")
# fast_models_instance.wait_for_state_deleted()

# avh_client.close()
