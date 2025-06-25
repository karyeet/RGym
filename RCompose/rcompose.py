import requests
import time
import re
port = 7070

"""
Was the job successful.
For building, this is if a bzImage was produced.
For reproducing, this is if the job ran without triggernig a bug.
"""
def isSuccess(jobid: str) -> bool:
    response = requests.get(f'http://localhost:{port}/issuccess?jobid={jobid}')
    return response.json()

# Is the job complete (has the job ran once, successfully or with failure).
def isComplete(jobid: str) -> bool:
    response = requests.get(
        f'http://localhost:{port}/iscomplete?jobid={jobid}')
    return response.json()

# Is the job started (running)
def isStarted(jobid: str) -> bool:
    response = requests.get(f'http://localhost:{port}/isstarted?jobid={jobid}')
    return response.json()

# Get the logs for a job as a string
def getLogs(jobid: str) -> str:
    response = requests.get(f'http://localhost:{port}/getlogs?jobid={jobid}')
    return response.text

# Get the state for a job as a json
def getState(jobid: str) -> dict:
    response = requests.get(f'http://localhost:{port}/getstate?jobid={jobid}')
    return response.json()

# Return full compiler string from a .config file
def read_full_compiler(file_contents: str) -> str:
    lines = file_contents.splitlines()
    for line in lines:
        if line.startswith("CONFIG_CC_VERSION_TEXT="):
            return line.strip().split("=")[1].strip().strip('"')
        if line.startswith("# Compiler: "):
            return line.strip().split(": ")[1].strip()
    #print("No compiler found in", file)
    return None

# Parse the compiler string to type and version
def parse_compiler_string(compiler_str: str) -> dict:
    compiler = re.search(r'(gcc|clang)', compiler_str)
    version = re.search(r'\d+\.\d+\.\d+', compiler_str)
    if compiler and version:
        version = version.group(0).split('.') # major, minor, patch
        version = [int(num) for num in version]  # Convert to integers
        return {"type": compiler.group(0), "major": version[0], "minor": version[1], "patch": version[2]}
    else:
        raise ValueError("Invalid compiler string format")
    





"""
kernel_config is the .config file,
git_repo is the git repository,
git_hash is the git commit hash,
patch is the patch to apply, can be an empty string
timeout is the maximum time the job can run in seconds (not implemented for build)
cores is the number of cores to use
metadata is a string that will be stored with the job, can be an empty string although I suggest it be the bug link
compiler is gcc or clang
""" 
def addBuildJob(kernel_config: str,
                git_repo: str,
                git_hash: str,
                patch: str,
                timeout: int,
                cores: int,
                metadata: str,
                compiler: str,
                compilerMajorVersion: int) -> str:
    response = requests.post(f'http://localhost:{port}/addjobbuild', json={
        'kernel_config': kernel_config,
        'git_repo': git_repo,
        'git_hash': git_hash,
        'patch': patch,
        'timeout': timeout,
        'cores': cores,
        'metadata': metadata,
        'compiler': compiler,
        'compilerMajorVersion': compilerMajorVersion 
    })
    return response.text


"""
bzImageJobId is the job id of the build job that produced the bzImage
memory is the amount of memory to give the VM in GB
boot_options is the boot options to pass to the VM (not implemented)
reproducer is the c reproducer, syz reproducer not yet implemented
timeout is the maximum time the job can run in seconds (so probably do 60*10)
cores is the number of cores to use (4 is a good number)
metadata is a string that will be stored with the job, can be an empty string although I suggest it be the bug link
reproducerType is c or syz
"""
def addReproduceJob(bzImageJobId: str,
                    memory: int,
                    boot_options: str,
                    reproducer: str,
                    timeout: int,
                    cores: int,
                    metadata: str,
                    reproducerType: str
                    ) -> str:
    response = requests.post(f'http://localhost:{port}/addjobreproducer', json={
        'bzImageJobId': bzImageJobId,
        'memory': memory,
        'boot_options': boot_options,
        'reproducer': reproducer,
        'timeout': timeout,
        'cores': cores,
        'metadata': metadata,
        'reproducerType': reproducerType
    })
    return response.text

# wait for job to complete, blocking, returns success
def waitForJob(jobid: str) -> bool:
    while not isComplete(jobid):
        time.sleep(4)
    return isSuccess(jobid)


def start(jobid: str):
    response = requests.post(f'http://localhost:{port}/start', json={'jobid': jobid})
    return response.json()

