#!/usr/bin/python3
import subprocess
import sys
import os
import hashlib
import time

def print(*args, **kwargs):
    return __builtins__.print(*args, flush=True, **kwargs)

def main():
    print('args received', sys.argv)
    if len(sys.argv) != 4:
        print('Usage: setup.py <memory> <cores>')
        sys.exit(1)

    memory = sys.argv[1]
    cores = sys.argv[2]

    if(len(memory) < 1):
        print('No memory provided.')
        sys.exit(1)

    if(len(cores) < 1):
        print('No memory provided.')
        sys.exit(1)


    print('qemu_command:', qemu_command)

    print(f'Copying POC from /share')
    subprocess.run(['cp', '/share/poc.c', '/root/poc.c'], check=True, stderr=subprocess.STDOUT)

    os.chdir('/root')

    print(f'Building POC')
    subprocess.run(['gcc', '-pthread', '/root/poc.c', '-o', '/root/poc'], check=True, stderr=subprocess.STDOUT)
    
    print(f'chmod +x poc')
    subprocess.run(['chmod', '+x', '/root/poc'], check=True, stderr=subprocess.STDOUT)

    qemu_command =[
        "qemu-system-x86_64",
        '-m',
        f'{memory}G',
        '-smp',
        f'{cores},sockets=1,cores=1',
        '-drive',
        'file=/share/rootfs,format=raw',
        '-append',
        '"console=ttyS0 root=/dev/sda earlyprintk=serial net.ifnames=0 nokaslr"',
        '-net',
        'nic,model=e1000',
        '-enable-kvm',
        '-nographic',
        '-snapshot',
        '-machine',
        'pc-q35-7.1',
        '-kernel',
        '/share/bzImage',
    ]

    vm_state_txt = ["syzkaller login:"]
    vm_state_cmd = ["root\n"]
    vm_state_i = 0
    vm_state_max = len(vm_state_txt)

    qemu_output = []
    with subprocess.Popen(qemu_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
        for line in process.stdout:
            decoded_line = line.decode('ascii')
            print(decoded_line, end='')
            qemu_output.append(decoded_line)
            if vm_state_txt[vm_state_i] in decoded_line:
                process.stdin.write(vm_state_cmd[vm_state_i])
                process.stdin.flush()
                if(vm_state_i < vm_state_max):
                    vm_state_i += 1

    