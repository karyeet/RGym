#!/usr/bin/python3
import subprocess
import sys
import os
import hashlib

def print(*args, **kwargs):
    return __builtins__.print(*args, flush=True, **kwargs)

def main():
    print('args received', sys.argv)
    if len(sys.argv) != 4:
        print('Usage: setup.py <commit_hash> <repository> <cores> ')
        sys.exit(1)

    commit_hash = sys.argv[1]
    repository = sys.argv[2]
    cores = int(sys.argv[3])

    if(len(commit_hash) < 1):
        print('No commit hash provided.')
        sys.exit(1)

    if(len(repository) < 1):
        print('No repository provided.')
        sys.exit(1)

    if(int(cores) > os.cpu_count()):
        print('Number of cores specified is greater than the number of cores available.')
        cores = os.cpu_count()
    

    print(f'Cloning {repository}')
    subprocess.run(['git', 'clone', '--progress', repository], check=True, stderr=subprocess.STDOUT)

    # Change directory to /linux
    os.chdir('/linux')
   
    # Checkout the specified git hash
    print(f'Checking out {commit_hash}')
    subprocess.run(['git', 'checkout', commit_hash], check=True, stderr=subprocess.STDOUT)

    # copy config
    print('Copying .config')
    subprocess.run(['cp', '/share/.config', '/linux/.config'], check=True, stderr=subprocess.STDOUT)

    # copy patch if patch exists
    if os.path.exists('/share/.patch'):
        print('Applying patch')
        subprocess.run(['git', 'apply', '/share/.patch'], check=True, stderr=subprocess.STDOUT)
    else:
        print('Not patching (patch not found)')

    # fill defaults
    print('Filling defaults with make olddefconfig')
    subprocess.run(['make', 'olddefconfig'], check=True, stderr=subprocess.STDOUT)

    # Run make with the number of processors
    #make_process = subprocess.run(['make', f'-j{os.cpu_count()}'], check=True, stdout=subprocess.PIPE, text=True)
    
    make_output = []
    with subprocess.Popen(['make', f'-j{cores}'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
        for line in process.stdout:
            print(line.decode('ascii'), end='')
            make_output.append(line.decode('utf8'))

    # Check the output of the make command
    print('Reading end of output', '\n'.join(make_output[-5:]))
    if 'Kernel: arch/x86/boot/bzImage is ready' not in '\n'.join(make_output[-5:]):
        print('Error: Kernel build did not complete successfully.')
        sys.exit(1)

    # hash config
    print('Hashing config')
    config_hash = ''
    with open('/linux/.config', 'rb', buffering=0) as f:
        config_hash = hashlib.file_digest(f, 'sha256').hexdigest()[:7]

    # Copy the bzImage to the /share directory with the hash in the filename
    bzImage_name = f'/share/bzImage-{commit_hash}-{config_hash}'
    print(f'Copying bzimage to ', bzImage_name)
    subprocess.run(['cp', '/linux/arch/x86/boot/bzImage', bzImage_name], check=True, stderr=subprocess.STDOUT)

    print('SUCCESS')
if __name__ == '__main__':
    main()