#!/usr/bin/python3
import subprocess
import sys
import os
import threading
import json


def print(*args, **kwargs):
    return __builtins__.print(*args, flush=True, **kwargs)

def timeout(code=0):
    print('Timeout')
    os._exit(code)

def waitForText(process, strings): # these arguments were supposed to be temporary but the bug doesnt trigger when i change them (?_?)
    while exit_code := process.poll() is None:
        line = process.stdout.readline().decode('utf-8')
        print(line, end='')
        for text in strings:
            if text in line:
                return strings.index(text)+1
    # qemu process is dead
    print(f'QEMU exited with {exit_code}')
    os._exit(1)

def main():
    print('args received', sys.argv)
    if len(sys.argv) != 5:
        print('Usage: setup.py <memory> <cores> <timeout_sec> <reproducer_type>')
        sys.exit(1)

    memory = sys.argv[1]
    cores = sys.argv[2]
    timeout_sec = int(sys.argv[3])
    reproducer_type = sys.argv[4]

    if(len(memory) < 1):
        print('No memory provided.')
        sys.exit(1)

    if(len(cores) < 1):
        print('No memory provided.')
        sys.exit(1)

    if(timeout_sec < 1):
        print('No timeout provided.')
        sys.exit(1)

    if(reproducer_type != 'c' and reproducer_type != 'syz'):
        print('Invalid reproducer type.')
        sys.exit(1)

    print(f'Copying POC from /share')
    subprocess.run(['cp', '/share/poc', '/root/poc'], check=True, stderr=subprocess.STDOUT)

    print(f'Copying syz progs from /syzprogs')
    ret = os.system('cp /syzprogs/* /root/')
    if(ret != 0):
        print('Failed to copy syzprogs')
        os._exit(1)
    #subprocess.run(['cp', '/syzprogs/*', '/root/'], check=True, stderr=subprocess.STDOUT)

    exec_cmd = './poc.o'
    os.chdir('/root')
    if reproducer_type == 'c':
        print(f'Building POC')
        subprocess.run(['mv', '/root/poc', '/root/poc.c'], check=True, stderr=subprocess.STDOUT)
        subprocess.run(['gcc', '-pthread', '-static', '/root/poc.c', '-o', '/root/poc.o'], check=True, stderr=subprocess.STDOUT)
        
        print(f'chmod +x poc.o')
        subprocess.run(['chmod', '+x', '/root/poc.o'], check=True, stderr=subprocess.STDOUT)
    elif reproducer_type == 'syz':
        # check for header
        exec_cmd = ['./syz-execprog']
        with open('/root/poc', 'r') as f:
            rep = f.readlines()
            if '#{"' not in rep[2]:
                print('Could not find syzkaller header in poc')
                os._exit(1)
            args = json.loads(rep[2][1:]) # parse args json, skip comment #
            # process features
            features =   ['binfmt_misc',  'cgroups',  'close_fds',  'devlink_pci',  'ieee802154',  'net_dev',
                                   'net_reset',  'nic_vf',  'swap',  'sysctl',  'tun',  'usb',  'vhci',  'wifi', 'segv']
            enabled_features = []
            for feature in features:
                if(args.get(feature) is True):
                    print(f'Enable {feature}')
                    enabled_features.append(feature)
            if(args.get('resetnet') is True):
                print('Enable resetnet')
                enabled_features.append('net_reset')
            if(args.get('netdev') is True):
                print('Enable netdev')
                enabled_features.append('net_dev')
            exec_cmd.append('-enable=' + ','.join(enabled_features))
            # process repeat
            if(args.get('repeat') is True):
                print('Enable repeat')
                exec_cmd.append('-repeat=0')
            # process other args 
            other_args = ['threaded', 'procs', 'slowdown', 'sandbox', 'sandbox_arg', 'collide', 'fault', 'fault_call', 'fault_nth', ]
            for arg in other_args:
                if(args.get(arg) is not None):
                    if(args.get(arg) is True):
                        print(f'Enable {arg}')
                        exec_cmd.append(f'-{arg}=true')
                    else:
                        print(f'Enable {arg} with value {args.get(arg)}')
                        exec_cmd.append(f'-{arg}={args.get(arg)}')
            exec_cmd.append('/root/poc')
            exec_cmd = ' '.join(exec_cmd)
            


    qemu_command =[
        "qemu-system-x86_64",
        '-m',
        f'{memory}G',
        '-smp',
        f'sockets=1,cores={cores},threads=1',
        '-object',
        f'memory-backend-ram,id=mem0,size={memory}G',
        '-numa',
        f'node,nodeid=0,cpus=0-{int(cores)-1},memdev=mem0',
        '-drive',
        'file=/share/rootfs,format=raw',
        '-append',
        '"console=ttyS0 root=/dev/sda earlyprintk=serial net.ifnames=0 nokaslr"',
        '-net',
        'nic,model=e1000',
        '-net',
        'user,host=10.0.2.10,hostfwd=tcp:127.0.0.1:10021-:22',
        '-enable-kvm',
        '-nographic',
        '-snapshot',
        '-machine',
        'pc-q35-7.1',
        '-kernel',
        '/share/bzImage',
    ]
    print('Running QEMU with command: ' + ' '.join(qemu_command))
    boot_timeout = threading.Timer(120, timeout, [1])
    boot_timeout.start() # boot timer
    qemu_proc = subprocess.Popen(qemu_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    waitForText(qemu_proc, ['syzkaller ttyS0'])
    qemu_proc.stdin.write(b'\n')
    qemu_proc.stdin.flush()
    waitForText(qemu_proc, ['syzkaller login:'])
    qemu_proc.stdin.write(b'root\n')
    qemu_proc.stdin.flush()
    waitForText(qemu_proc, ['permitted by applicable law.'])
    qemu_proc.stdin.write(b'\n')
    qemu_proc.stdin.flush()
    waitForText(qemu_proc, ['root@syzkaller:~#'])
    subprocess.run('scp -r -P 10021 -o StrictHostKeyChecking=no -i /share/key /root/ root@localhost:/'.split(' '), check=True, stderr=subprocess.STDOUT)
    qemu_proc.stdin.write(b'ls\n')
    qemu_proc.stdin.flush()
    boot_timeout.cancel() # stop boot timer
    threading.Timer(timeout_sec, timeout).start() # start poc timer
    qemu_proc.stdin.write(f'{exec_cmd}\n'.encode('utf-8'))
    qemu_proc.stdin.flush()
    while found := waitForText(qemu_proc, ['root@syzkaller:~#', 'BUG: ']):
        if found == 2:
            print('BUG found')
            os._exit(1)
        qemu_proc.stdin.write(f'{exec_cmd}\n'.encode('utf-8'))
        qemu_proc.stdin.flush()


if __name__ == '__main__':
    main()