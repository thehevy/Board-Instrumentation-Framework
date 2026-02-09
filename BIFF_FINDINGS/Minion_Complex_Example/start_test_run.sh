#!/bin/bash
# This script is used to start a netperf test in the specified directory.
# set -x

# <Actor ID="start_netperf_test_tx">
#     <Executable>start_netperf_test.sh</Executable>
#     <!-- ./run_demo.sh -r 5 -p "1 2 3 4 5" -l 10 -d 30 -t tx -->
#     <Param>5</Param>
#     <Param>"1 2 3 4 5"</Param>
#     <Param>10</Param>
#     <Param>30</Param>
#     <Param>tx</Param>
# </Actor>

current_dir=$(pwd)
# Set script_dir to the directory above the current_dir
script_dir=$(dirname "$current_dir")

# Default values
#script_dir="${script_dir:-/home/Connorsville/INTEL_VISION_DEMO}"
#test_script="${script_dir}/run_demo.sh"
test_script="run_demo.sh"

TEST_RUNS="${1:-10}"
PORTS="${2:-ALL}"
LOOPS="${3:-5}"
DURATION="${4:-60}"
TEST_TYPE="${5:-bx}"

# Log file for the netperf test
netperf_test_log="${current_dir}/netperf_test.log"
test_parameters_log="${current_dir}/test_parameters.log"
# Check if the log file exists, if not create it
if [ ! -f "${netperf_test_log}" ]; then
    touch "${netperf_test_log}"
fi
# Check if the log file is writable
if [ ! -w "${netperf_test_log}" ]; then
    echo "Log file ${netperf_test_log} is not writable. Exiting."
    exit 1
fi

if [[ "$PORTS" == "All" ]]; then
    PORTS="1 2 3 4 5"
fi

echo "Starting netperf test with the following parameters:" > "${netperf_test_log}"
{
    echo "Test runs: $TEST_RUNS"
    echo "Ports: ""\"${PORTS}"\" 
    echo "Loops: $LOOPS" 
    echo "Duration: $DURATION" 
    echo "Test type: $TEST_TYPE" 
    echo "Test.Number: NA"   
} >> "${netperf_test_log}" 2>&1

{
    echo "Test.Runs=$TEST_RUNS"
    echo "Test.Ports=""\"${PORTS}"\" 
    echo "Test.Loops=$LOOPS" 
    echo "Test.Duration=$DURATION" 
    echo "Test.Type=$TEST_TYPE" 
    echo "Test.Number=NA"
} > "${test_parameters_log}" 2>&1

cd "$script_dir" || exit
# Check if the "${test_script}" script exists, create it if it doesn't and reset it if it does
if [ ! -f "${test_script}" ]; then
    echo "${test_script} not found in $script_dir"
    exit 1
else
    # Check if the "${test_script}" script is executable
    if [ ! -x "${test_script}" ]; then
        echo "${test_script} is not executable. Making it executable."
        chmod +x "${test_script}"
    fi
    echo "Starting run_demo script" >> "${netperf_test_log}" 2>&1
    echo "Test.Status=Test Started"  >> "${test_parameters_log}" 2>&1
fi

# Check if netperf, run_demo.sh, or start_netperf_test.sh are already running and kill them
for process in netperf "${test_script}"; do
    pkill -f "$process" && echo "Killed running process: $process" || echo "No running process found for: $process" >> "${netperf_test_log}" 2>&1
done
sleep 2

# Start the netperf test in the background
# Redirect output to the log file
# Start the netperf test with the specified parameters
sed -i 's/Test.Status=Test Started/Test.Status=Test Running/' "${test_parameters_log}"

pwd 
./"${test_script}" -r "${TEST_RUNS}" -p "${PORTS}" -l "${LOOPS}" -d "${DURATION}" -t "${TEST_TYPE}" >> "${netperf_test_log}" 2>&1 
# Wait for the netperf test to finish
echo "Waiting for netperf test to finish..." 
wait
sleep 5
echo "Done Waiting for netperf test to finish..."
# Check if the netperf test was successful
if [ $? -eq 0 ]; then
    echo "Netperf test completed successfully."
    sed -i 's/Test.Status=Test Running/Test.Status=Test Clean Up/' "${test_parameters_log}"
    sleep 5
    sed -i 's/Test.Status=Test Clean Up/Test.Status=Test Completed/' "${test_parameters_log}"

else
    echo "Netperf test failed."
    sed -i 's/Test.Status=Test Running/Test.Status=Test Failed/' "${test_parameters_log}"
fi
cd "${current_dir}" || exit

# Usage:
# ./start_netperf_test.sh
# This script will send the following parameters to the run_demo.sh script:
# -r: Number of repetitions
# -p: Number of ports to test
# -l: Number of loops
# -d: Duration of the test
# -t: Type of test (tx, rx, or both)


# #!/bin/bash
# # This script is used to start a netperf test in the specified directory.
# # set -x

# # <Actor ID="start_netperf_test_tx">
# #     <Executable>start_netperf_test.sh</Executable>
# #     <!-- ./run_demo.sh -r 5 -p "1 2 3 4 5" -l 10 -d 30 -t tx -->
# #     <Param>5</Param>
# #     <Param>"1 2 3 4 5"</Param>
# #     <Param>10</Param>
# #     <Param>30</Param>
# #     <Param>tx</Param>
# # </Actor>

# current_dir=$(pwd)
# # Set script_dir to the directory above the current_dir
# script_dir=$(dirname "$current_dir")

# # Default values
# #script_dir="${script_dir:-/home/Connorsville/INTEL_VISION_DEMO}"
# #test_script="${script_dir}/run_demo.sh"
# test_script="run_demo.sh"

# TEST_RUNS="${1:-10}"
# PORTS="${2:-ALL}"
# LOOPS="${3:-5}"
# DURATION="${4:-60}"
# TEST_TYPE="${5:-bx}"

# # Log file for the netperf test
# netperf_test_log="${current_dir}/netperf_test.log"
# echo "Starting netperf test with the following parameters:" > "${netperf_test_log}"
# {
#     echo "Test runs: $TEST_RUNS"
#     echo "Ports: ""\"${PORTS}"\" 
#     echo "Loops: $LOOPS" 
#     echo "Duration: $DURATION" 
#     echo "Test type: $TEST_TYPE" 
# } >> "${netperf_test_log}"

# if [[ "$PORTS" == "All" ]]; then
#     PORTS="1 2 3 4 5"
# fi

# cd "$script_dir" || exit
# # Check if the "${test_script}" script exists, create it if it doesn't and reset it if it does
# if [ ! -f "${test_script}" ]; then
#     echo "${test_script} not found in $script_dir"
#     exit 1
# else
#     # Check if the "${test_script}" script is executable
#     if [ ! -x "${test_script}" ]; then
#         echo "${test_script} is not executable. Making it executable."
#         chmod +x "${test_script}"
#     fi
#     echo "Starting run_demo script" >> "${netperf_test_log}"
# fi

# # Check if netperf, run_demo.sh, or start_netperf_test.sh are already running and kill them
# for process in netperf "${test_script}"; do
#     pkill -f "$process" && echo "Killed running process: $process" || echo "No running process found for: $process" >> "${netperf_test_log}" 2>&1
# done
# sleep 2

# # Start the netperf test in the background
# # Redirect output to the log file
# # Start the netperf test with the specified parameters
# pwd 
# ./"${test_script}" -r "${TEST_RUNS}" -p "${PORTS}" -l "${LOOPS}" -d "${DURATION}" -t "${TEST_TYPE}" >> "${netperf_test_log}" 2>&1 
# # Wait for the netperf test to finish
# echo "Waiting for netperf test to finish..." 
# wait
# echo "Done Waiting for netperf test to finish..."
# # Check if the netperf test was successful
# if [ $? -eq 0 ]; then
#     echo "Netperf test completed successfully."
# else
#     echo "Netperf test failed."
# fi
# cd "${current_dir}" || exit

# # Usage:
# # ./start_netperf_test.sh
# # This script will send the following parameters to the run_demo.sh script:
# # -r: Number of repetitions
# # -p: Number of ports to test
# # -l: Number of loops
# # -d: Duration of the test
# # -t: Type of test (tx, rx, or both)