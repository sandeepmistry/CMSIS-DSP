import os

from utils.avh_client import AvhClient
from utils.avh_fast_models_instance import AvhFastModelsInstance

avh_client = AvhClient(os.environ["AVH_API_TOKEN"])

fast_models_instance = AvhFastModelsInstance(
    avh_client, "CMSIS-DSP Examples - Corstone-300 FVP Test"
)

print("creating instance")
fast_models_instance.create()

print("waiting for instance state on")
fast_models_instance.wait_for_state_on()

print("waiting for instance OS to boot")
fast_models_instance.wait_for_os_boot()

output, exit_code = fast_models_instance.run_elf(
    "./build/arm_bayes_example.elf", "./Corstone-300/fvp_config.txt"
)

print(exit_code, output)

print("deleting instance")
fast_models_instance.delete()

print("waiting for instance state deleted")
fast_models_instance.wait_for_state_deleted()

avh_client.close()
