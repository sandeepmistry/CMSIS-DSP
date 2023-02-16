#
# SPDX-FileCopyrightText: Copyright 2019-2023 Arm Limited and/or its affiliates <open-source-office@arm.com>
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

cmake_minimum_required(VERSION 3.15.6)

project(cmsis_dsp_examples VERSION 0.0.1)

set(CMSIS_PATH "</path/to/CMSIS>" CACHE PATH "Path to CMSIS.")
set(CMSISCORE ${CMSIS_PATH}/CMSIS/Core)

# CMSIS-DSP config
set(CONFIGTABLE OFF)
set(ALLFAST ON)
set(ALLFFT ON)
set(HELIUM ON)

add_compile_options(
  -Ofast
  -ffast-math
  -Wall
  -Wextra
  -flax-vector-conversions
)

if (${CMSIS_PATH} STREQUAL "</path/to/CMSIS>")
  message(FATAL_ERROR "CMSIS not set. Did you provide -DCMSIS=<path/to/CMSIS>?")
endif()

set(FVP_CORSTONE_300_PATH "${CMAKE_CURRENT_SOURCE_DIR}/Corstone-300" CACHE PATH
    "Dependencies for using FVP based on Arm Corstone-300 software.")
set(CMAKE_EXECUTABLE_SUFFIX ".elf")

# Build the functions to be tested.
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/.. CMSISDSP)

# Target for all unit tests.
add_custom_target(cmsis_dsp_examples)

add_library(retarget STATIC
    ${FVP_CORSTONE_300_PATH}/retarget.c
    ${FVP_CORSTONE_300_PATH}/uart.c)

# Build CMSIS startup dependencies based on TARGET_CPU.
string(REGEX REPLACE "^cortex-m([0-9]+)$" "ARMCM\\1" ARM_CPU ${CMAKE_SYSTEM_PROCESSOR})
if(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "cortex-m33")
    set(ARM_FEATURES "_DSP_FP")
elseif(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "cortex-m4")
    set(ARM_FEATURES "_FP")
elseif(${CMAKE_SYSTEM_PROCESSOR} STREQUAL "cortex-m7")
    set(ARM_FEATURES "_DP")
else()
    set(ARM_FEATURES "")
endif()
add_library(cmsis_startup STATIC)
target_sources(cmsis_startup PRIVATE
    ${CMSIS_PATH}/Device/ARM/${ARM_CPU}/Source/startup_${ARM_CPU}.c
    ${CMSIS_PATH}/Device/ARM/${ARM_CPU}/Source/system_${ARM_CPU}.c)
target_include_directories(cmsis_startup PUBLIC
    ${CMSIS_PATH}/Device/ARM/${ARM_CPU}/Include
    ${CMSIS_PATH}/CMSIS/Core/Include)
target_compile_options(cmsis_startup INTERFACE -include${ARM_CPU}${ARM_FEATURES}.h)
target_compile_definitions(cmsis_startup PRIVATE ${ARM_CPU}${ARM_FEATURES})


# This function should be used instead of add_executable.
set_property(GLOBAL PROPERTY cmsis_dsp_example_executables)
function(add_cmsis_dsp_example)
    get_property(tmp GLOBAL PROPERTY cmsis_nn_unit_test_executables)
    foreach(target ${ARGV})
        set(tmp "${tmp} ${target}")
        add_executable(${target})
        target_link_libraries(${target} PRIVATE $<TARGET_OBJECTS:cmsis_startup> cmsis_startup CMSISDSP m c rdimon)
        add_dependencies(${target} cmsis_startup CMSISDSP)

        # define SEMIHOSTING to enable the printf statements in the examples
        target_compile_definitions(${target} PUBLIC SEMIHOSTING)

        # Link in FVP dependencies to every example.
        target_link_options(${target} PRIVATE -T ${FVP_CORSTONE_300_PATH}/linker.ld)
        set_target_properties(${target} PROPERTIES LINK_DEPENDS ${FVP_CORSTONE_300_PATH}/linker.ld)

        add_dependencies(cmsis_dsp_examples ${target})
    endforeach()
    set_property(GLOBAL PROPERTY cmsis_dsp_example_executables "${tmp}")
endfunction(add_cmsis_dsp_example)

add_cmsis_dsp_example(arm_bayes_example)
target_sources(arm_bayes_example PRIVATE
    ../Examples/ARM/arm_bayes_example/arm_bayes_example_f32.c
)

add_cmsis_dsp_example(arm_class_marks_example)
target_sources(arm_class_marks_example PRIVATE
    ../Examples/ARM/arm_class_marks_example/arm_class_marks_example_f32.c
)

add_cmsis_dsp_example(arm_convolution_example)
target_sources(arm_convolution_example PRIVATE
    ../Examples/ARM/arm_convolution_example/arm_convolution_example_f32.c
    ../Examples/ARM/arm_convolution_example/math_helper.c
)

add_cmsis_dsp_example(arm_dotproduct_example)
target_sources(arm_dotproduct_example PRIVATE
    ../Examples/ARM/arm_dotproduct_example/arm_dotproduct_example_f32.c
)

add_cmsis_dsp_example(arm_fft_bin_example)
target_sources(arm_fft_bin_example PRIVATE
    ../Examples/ARM/arm_fft_bin_example/arm_fft_bin_data.c
    ../Examples/ARM/arm_fft_bin_example/arm_fft_bin_example_f32.c
)

add_cmsis_dsp_example(arm_fir_example)
target_sources(arm_fir_example PRIVATE
    ../Examples/ARM/arm_fir_example/arm_fir_data.c
    ../Examples/ARM/arm_fir_example/arm_fir_example_f32.c
    ../Examples/ARM/arm_fir_example/math_helper.c
)

add_cmsis_dsp_example(arm_graphic_equalizer_example)
target_sources(arm_graphic_equalizer_example PRIVATE
    ../Examples/ARM/arm_graphic_equalizer_example/arm_graphic_equalizer_data.c
    ../Examples/ARM/arm_graphic_equalizer_example/arm_graphic_equalizer_example_q31.c
    ../Examples/ARM/arm_graphic_equalizer_example/math_helper.c
)

add_cmsis_dsp_example(arm_linear_interp_example)
target_sources(arm_linear_interp_example PRIVATE
    ../Examples/ARM/arm_linear_interp_example/arm_linear_interp_data.c
    ../Examples/ARM/arm_linear_interp_example/arm_linear_interp_example_f32.c
    ../Examples/ARM/arm_linear_interp_example/math_helper.c
)

add_cmsis_dsp_example(arm_matrix_example)
target_sources(arm_matrix_example PRIVATE
    ../Examples/ARM/arm_matrix_example/arm_matrix_example_f32.c
    ../Examples/ARM/arm_matrix_example/math_helper.c
)

add_cmsis_dsp_example(arm_signal_converge_example)
target_sources(arm_signal_converge_example PRIVATE
    ../Examples/ARM/arm_signal_converge_example/arm_signal_converge_data.c
    ../Examples/ARM/arm_signal_converge_example/arm_signal_converge_example_f32.c
    ../Examples/ARM/arm_signal_converge_example/math_helper.c
)

add_cmsis_dsp_example(arm_sin_cos_example)
target_sources(arm_sin_cos_example PRIVATE
    ../Examples/ARM/arm_sin_cos_example/arm_sin_cos_example_f32.c
)

add_cmsis_dsp_example(arm_svm_example)
target_sources(arm_svm_example PRIVATE
    ../Examples/ARM/arm_svm_example/arm_svm_example_f32.c
)

add_cmsis_dsp_example(arm_variance_example)
target_sources(arm_variance_example PRIVATE
    ../Examples/ARM/arm_variance_example/arm_variance_example_f32.c
)
