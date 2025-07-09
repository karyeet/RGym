import requests
import time
import re
import os

port = 7070

# Exit code reported by run script of job.
def get_exit_code(jobid: str) -> int:
    endpoint = "getExitCode"
    response = requests.get(f'http://localhost:{port}/{endpoint}?jobid={jobid}')
    return response.json()

# If the job is running.
def is_running(jobid: str) -> bool:
    endpoint = "isRunning"
    response = requests.get(f'http://localhost:{port}/{endpoint}?jobid={jobid}')
    return response.json()

# Get the logs for a job as a string
def get_logs(jobid: str) -> str:
    response = requests.get(f'http://localhost:{port}/getlogs?jobid={jobid}')
    return response.text

# Get the state for a job as a json
def get_state(jobid: str) -> dict:
    response = requests.get(f'http://localhost:{port}/getstate?jobid={jobid}')
    return response.json()

# Return full compiler string from a .config file
def read_full_compiler(config_file_contents: str) -> str:
    lines = config_file_contents.splitlines()
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
Extract kernel version from the .config file contents, expected format in .config:
# Linux/arm 6.12.0-rc1 Kernel Configuration
# Linux/x86_64 6.14.0 Kernel Configuration
"""
def get_kernel_version(config_file_contents: str) -> dict:
    lines = config_file_contents.splitlines()
    for line in lines:
        if line.startswith("# Linux/"):
            version_match = re.search(r'Linux\/([A-z0-9]*) (\d+)\.(\d+).(\d)(-[A-z0-9]*)?', line).groups()
            arch = version_match[0]
            major = version_match[1]
            minor = version_match[2]
            patch = version_match[3]
            suffix = version_match[4] if len(version_match) > 4 else ""
            return {"arch": arch, "major": major, "minor": minor, "patch": patch, "suffix": suffix}
    return None

"""
Generate a dict giving compiler versions used per kernel version.
This will read all .config files in the given directory and extract the compiler version and kernel version.
The result is a nested dictionary with major, minor, and patch versions as keys.
"""
def generate_compiler_mapping(kernel_configs_dir: str) -> dict:
    compiler_mapping = {}
    files = os.listdir(kernel_configs_dir)
    total_files = len(files)
    no_compiler = 0
    print(f"Found {total_files} kernel config files in {kernel_configs_dir}")
    for file_i in range(len(files)):
        file = files[file_i]
        print(f"Processing {file_i}/{total_files} || No compiler found in {no_compiler}", end='\r')
        config_file_contents = open(os.path.join(kernel_configs_dir, file), 'r').read()
        compiler_str = read_full_compiler(config_file_contents)
        if compiler_str is None:
            no_compiler += 1
            continue
        kernel_version = get_kernel_version(config_file_contents)
        if kernel_version is None:
            print(f"No kernel version found in {file}, skipping...")
            continue
        #kernel_version_str = kernel_version["major"] + '.' + kernel_version["minor"] + '.' + kernel_version["patch"]
        compiler = parse_compiler_string(compiler_str)
        if kernel_version["major"] not in compiler_mapping:
            compiler_mapping[kernel_version["major"]] = {}
        if kernel_version["minor"] not in compiler_mapping[kernel_version["major"]]:
            compiler_mapping[kernel_version["major"]][kernel_version["minor"]] = {}
        if kernel_version["patch"] not in compiler_mapping[kernel_version["major"]][kernel_version["minor"]]:
            compiler_mapping[kernel_version["major"]][kernel_version["minor"]][kernel_version["patch"]] = set()
        compiler_map_str = f"{compiler['type']} {compiler['major']}"
        compiler_mapping[kernel_version["major"]][kernel_version["minor"]][kernel_version["patch"]].add(compiler_map_str)
    sortedObj = {}
    for major, minor_dict in sorted(compiler_mapping.items()):
        sortedObj[major] = {}
        for minor, patch_dict in sorted(minor_dict.items()):
            sortedObj[major][minor] = {}
            for patch, compilers in sorted(patch_dict.items()):
                sortedObj[major][minor][patch] = list(compilers)
    return sortedObj

"""
Return a suggested compiler version, ex: "clang 11"
kernel version in format 5.10.1
"""
def pick_compiler_version(kernel_version, compiler_mapping: dict) -> str:
    kernel_version_split = kernel_version.split('.')
    major = kernel_version_split[0]
    minor = kernel_version_split[1]
    patch = kernel_version_split[2]
    if major in compiler_mapping:
        if minor in compiler_mapping[major]:
            if patch in compiler_mapping[major][minor]:
                return compiler_mapping[major][minor][patch][0]  # Return the first compiler version found
            else:
                # otherwise return closest patch version
                closest_patch = -1
                diff = float('inf')
                for key in compiler_mapping[major][minor].keys():
                    if abs(int(key) - int(patch)) < diff:
                        diff = abs(int(key) - int(patch))
                        closest_patch = key
                if closest_patch != -1:
                    return compiler_mapping[major][minor][closest_patch][0]  # Return the first compiler version found
        else:
            # otherwise return closest minor version
            closest_minor = -1
            diff = float('inf')
            for key in compiler_mapping[major].keys():
                if abs(int(key) - int(minor)) < diff:
                    diff = abs(int(key) - int(minor))
                    closest_minor = key
            if closest_minor != -1:
                return compiler_mapping[major][closest_minor][list(compiler_mapping[major][closest_minor].keys())[0]][0]
    else:
        # otherwise return closest major version
        closest_major = -1
        diff = float('inf')
        for key in compiler_mapping.keys():
            if abs(int(key) - int(major)) < diff:
                diff = abs(int(key) - int(major))
                closest_major = key
        if closest_major != -1:
            return compiler_mapping[closest_major][list(compiler_mapping[closest_major].keys())[0]][list(compiler_mapping[closest_major][list(compiler_mapping[closest_major].keys())[0]].keys())[0]][0]

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

"""
Wait for job to complete, blocking, return exit code.
"""
def waitForJob(jobid: str) -> int:
    while is_running(jobid):
        time.sleep(4)
    return get_exit_code(jobid)


"""
Start the job.
Returns true if the job was started, false if it was already started and not started again.
"""
def start(jobid: str) -> bool:
    response = requests.post(f'http://localhost:{port}/start', json={'jobid': jobid})
    return response.json()

