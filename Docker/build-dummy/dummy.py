#!/usr/bin/python3
import subprocess
import sys
import os
import hashlib

def main():
    if len(sys.argv) != 3:
        print('Usage: setup.py <commit_hash> <cores>')
        sys.exit(1)

    print('args received', sys.argv)

    commit_hash = sys.argv[1]
    cores = int(sys.argv[2])

    if(len(commit_hash) < 1):
        print('No commit hash provided.')
        sys.exit(1)

    if(int(cores) > os.cpu_count()):
        print('Number of cores specified is greater than the number of cores available.')
        cores = os.cpu_count()
        

    # Change directory to /linux
    os.chdir('/linux')

    # Checkout the specified git hash
    print(f'Checking out {commit_hash}')
    subprocess.run(['git', 'checkout', commit_hash], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # copy config
    print('Copying .config')
    subprocess.run(['cp', '/share/.config', '/linux/.config'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # copy patch if patch exists
    if os.path.exists('/share/.patch'):
        print('Applying patch')
        subprocess.run(['git', 'apply', '/share/.patch'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        print('Not patching (patch not found)')

    # fill defaults
    print('Filling defaults with make olddefconfig')
    subprocess.run(['make', 'olddefconfig'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Run make with the number of processors
    #make_process = subprocess.run(['make', f'-j{os.cpu_count()}'], check=True, stdout=subprocess.PIPE, text=True)
    
    make_output = []
    #with subprocess.Popen(['make', f'-j{cores}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
    #    for line in process.stdout:
    #        print(line.decode('utf8'))
    #        make_output.append(line.decode('utf8'))

    with open('/make.log', 'r') as f:
        make_output = f.readlines()

    # Check the output of the make command
    print('Reading end of output', '\n'.join(make_output[-5:]))
    if 'Kernel: arch/x86/boot/bzImage is ready' not in '\n'.join(make_output[-5:]):
        print('Error: Kernel build did not complete successfully.')
        sys.exit(1)
    print("Kernel build completed successfully")
    # hash config
    print('Hashing config')
    config_hash = ''
    with open('/linux/.config', 'rb', buffering=0) as f:
        config_hash = hashlib.file_digest(f, 'sha256').hexdigest()[:7]

    # Copy the bzImage to the /share directory with the hash in the filename
    bzImage_name = f'/share/bzImage-{commit_hash}-{config_hash}'
    print(f'Copying bzimage to ', bzImage_name)
    subprocess.run(['cp', '/linux/arch/x86/boot/bzImage', bzImage_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print('SUCCESS')
if __name__ == '__main__':
    main()