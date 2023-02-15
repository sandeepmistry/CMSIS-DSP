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
    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger(__name__)
        cls.logger.setLevel(logging.INFO)
        stdout_logger_handler = logging.StreamHandler(sys.stdout)
        stdout_logger_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)-8s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        cls.logger.addHandler(stdout_logger_handler)

        cls.avh_client = AvhClient(os.environ["AVH_API_TOKEN"])

        # TODO: cleanup any left over instances

        cls.fast_models_instance = AvhFastModelsInstance(
            cls.avh_client, "CMSIS-DSP Examples Test - Corstone-300 FVP"
        )

        cls.logger.info("creating instance ...")
        cls.addClassCleanup(cls.cleanupInstances)

        cls.fast_models_instance.create()
        cls.fast_models_instance.wait_for_state_on()

        cls.logger.info("waiting for OS to boot ...")
        cls.fast_models_instance.wait_for_os_boot()

    def test_arm_bayes_example(self):
        self.logger.info("testing arm_bayes_example ...")

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

    def test_arm_class_marks_example(self):
        self.logger.info("testing arm_class_marks_example ...")

        expected_output = "".join(["mean = 212.300003, std = 50.912827\r\n"])

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_class_marks_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn(expected_output, output)

    @classmethod
    def cleanupInstances(cls):
        cls.logger.info("deleting instance ...")
        cls.fast_models_instance.delete()

        cls.fast_models_instance.wait_for_state_deleted()

        cls.avh_client.close()


if __name__ == "__main__":
    unittest.main()
