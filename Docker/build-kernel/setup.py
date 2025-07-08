#!/usr/bin/python3
import subprocess
import sys
import os
import hashlib
import enum

def print(*args, **kwargs):
    return __builtins__.print(*args, flush=True, **kwargs)

class exit_codes(enum.Enum):
    BUILD_SUCCESS = 0
    BUILD_FAILURE = 1
    INVALID_ARG = 2
    PATCH_NO_APPLY = 3
    SETUP_ERROR = 4

def main():
    print('args received', sys.argv)
    if len(sys.argv) != 5:
        print('Usage: setup.py <commit_hash> <repository> <cores> <compiler>')
        sys.exit(exit_codes.INVALID_ARG.value)

    commit_hash = sys.argv[1]
    repository = sys.argv[2]
    cores = int(sys.argv[3])
    compiler = sys.argv[4]

    if(len(commit_hash) < 1):
        print('No commit hash provided.')
        sys.exit(exit_codes.INVALID_ARG.value)

    if(len(repository) < 1):
        print('No repository provided.')
        sys.exit(exit_codes.INVALID_ARG.value)

    if(int(cores) > os.cpu_count()):
        print('Number of cores specified is greater than the number of cores available.')
        cores = os.cpu_count()

    if(len(compiler) < 1):
        print('No compiler provided.')
        sys.exit(exit_codes.INVALID_ARG.value)
    if(compiler != 'gcc' and compiler != 'clang'):
        print('Invalid compiler provided.')
        sys.exit(exit_codes.INVALID_ARG.value)

    print(f'Cloning {repository}')
    clone_proc = subprocess.run(['git', 'clone', '--progress', repository, 'linux'], stderr=subprocess.STDOUT)
    if clone_proc.returncode != 0:
        print('Error: Failed to clone the repository.')
        sys.exit(exit_codes.SETUP_ERROR.value)
    # Change directory to /linux
    os.chdir('/linux')
   
    # Checkout the specified git hash
    print(f'Checking out {commit_hash}')
    checkout_proc = subprocess.run(['git', 'checkout', commit_hash], stderr=subprocess.STDOUT)
    if checkout_proc.returncode != 0:
        print('Error: Failed to checkout the specified commit hash.')
        sys.exit(exit_codes.SETUP_ERROR.value)
    
    # copy config
    print('Copying .config')
    cp_proc = subprocess.run(['cp', '/share/.config', '/linux/.config'], stderr=subprocess.STDOUT)
    if cp_proc.returncode != 0:
        print('Error: Failed to copy the .config file.')
        sys.exit(exit_codes.SETUP_ERROR.value)

    # copy patch if patch exists
    if os.path.exists('/share/.patch'):
        print('Applying patch')
        patch_proc = subprocess.run(['git', 'apply', '/share/.patch', '--ignore-space-change', '--ignore-whitespace'], stderr=subprocess.STDOUT)
        if patch_proc.returncode != 0:
            print('Error: Failed to apply the patch.')
            sys.exit(exit_codes.PATCH_NO_APPLY.value)
    else:
        print('Not patching (patch not found)')

    # fill defaults
    print('Filling defaults with make olddefconfig')
    config_proc = subprocess.run(['make', 'olddefconfig'], stderr=subprocess.STDOUT)
    if config_proc.returncode != 0:
        print('Error: Failed to fill defaults with make olddefconfig.')
        sys.exit(exit_codes.SETUP_ERROR.value)

    # Run make with the number of processors
    #make_process = subprocess.run(['make', f'-j{os.cpu_count()}'], check=True, stdout=subprocess.PIPE, text=True)
    
    make_output = []
    with subprocess.Popen(['make',f'CC={compiler}',f'HOSTCC={compiler}', f'-j{cores}'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
        for line in process.stdout:
            print(line.decode('utf-8'), end='')
            make_output.append(line.decode('utf-8'))

    # Check the output of the make command
    print('Reading end of output\n', '\n'.join(make_output[-5:]))
    if 'Kernel: arch/x86/boot/bzImage is ready' not in '\n'.join(make_output[-5:]):
        print('Error: Kernel build did not complete successfully.')
        sys.exit(exit_codes.BUILD_FAILURE.value)

    # hash config
    #print('Hashing config')
    #config_hash = ''
    #with open('/linux/.config', 'rb', buffering=0) as f:
    #    config_hash = hashlib.file_digest(f, 'sha256').hexdigest()[:7]

    # Copy the bzImage to the /share directory with the hash in the filename
    bzImage_name = f'/share/bzImage' #-{commit_hash}-{config_hash}'
    print(f'Copying bzimage to ', bzImage_name)
    cp_proc = subprocess.run(['cp', '/linux/arch/x86/boot/bzImage', bzImage_name], stderr=subprocess.STDOUT)
    if cp_proc.returncode != 0:
        print('Error: Failed to copy the bzImage file.')
        sys.exit(exit_codes.BUILD_FAILURE.value)

    print('SUCCESS')
    sys.exit(exit_codes.BUILD_SUCCESS.value)
if __name__ == '__main__':
    main()