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

        instance_name = "CMSIS-DSP Examples Test - Corstone-300 FVP"
        if "TARGET_CPU" in os.environ:
            instance_name += f" ({os.environ['TARGET_CPU']})"

        cls.fast_models_instance = AvhFastModelsInstance(cls.avh_client, instance_name)

        cls.logger.info("creating instance ...")
        cls.addClassCleanup(cls.cleanupInstances)

        cls.fast_models_instance.create()
        cls.fast_models_instance.wait_for_state_on()

        cls.logger.info("waiting for OS to boot ...")
        cls.fast_models_instance.wait_for_os_boot()

    def test_arm_bayes_example(self):
        self.logger.info("testing arm_bayes_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_bayes_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)

        # NOTE: last floating point digit of Max proba is removed from check
        self.assertIn("Class = 0\nMax proba = -2.89915", output)
        self.assertIn("Class = 1\nMax proba = -2.82773", output)
        self.assertIn("Class = 2\nMax proba = -3.10809", output)

    def test_arm_class_marks_example(self):
        self.logger.info("testing arm_class_marks_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_class_marks_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("mean = 212.300003, std = 50.912827\n\n", output)

    def test_arm_convolution_example(self):
        self.logger.info("testing arm_convolution_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_convolution_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("START\nSUCCESS\n", output)

    def test_arm_dotproduct_example(self):
        self.logger.info("testing arm_dotproduct_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_dotproduct_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("SUCCESS\n", output)

    def test_arm_fft_bin_example(self):
        self.logger.info("testing arm_fft_bin_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_fft_bin_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("SUCCESS\n", output)

    def test_arm_fir_example(self):
        self.logger.info("testing arm_fir_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_fir_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("SUCCESS\n", output)

    def test_arm_graphic_equalizer_example(self):
        self.logger.info("testing arm_graphic_equalizer_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_graphic_equalizer_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("SUCCESS\n", output)

    def test_arm_linear_interp_example(self):
        self.logger.info("testing arm_linear_interp_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_linear_interp_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("SUCCESS\n", output)

    def test_arm_matrix_example(self):
        self.logger.info("testing arm_matrix_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_matrix_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("SUCCESS\n", output)

    def test_arm_signal_converge_example(self):
        self.logger.info("testing arm_signal_converge_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_signal_converge_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("SUCCESS\n", output)

    def test_arm_sin_cos_example(self):
        self.logger.info("testing arm_sin_cos_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_sin_cos_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("SUCCESS\n", output)

    def test_arm_svm_example(self):
        self.logger.info("testing arm_svm_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_svm_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Result = 0\nResult = 1\n", output)

    def test_arm_variance_example(self):
        self.logger.info("testing arm_variance_example ...")

        output, exit_code = self.fast_models_instance.run_elf(
            "./build/arm_variance_example.elf", "./Corstone-300/fvp_config.txt"
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("SUCCESS\n", output)

    @classmethod
    def cleanupInstances(cls):
        cls.logger.info("deleting instance ...")
        cls.fast_models_instance.delete()

        cls.fast_models_instance.wait_for_state_deleted()

        cls.avh_client.close()


if __name__ == "__main__":
    unittest.main()
