#!/usr/bin/python3
import subprocess
import sys
import os
import threading



def print(*args, **kwargs):
    return __builtins__.print(*args, flush=True, **kwargs)

def timeout():
    print('Timeout')
    sys.exit(0) # timeout is good

def waitForText(process, text, text2=None):
    while True:
        line = process.stdout.readline().decode('utf-8')
        print(line, end='')
        if text in line:
            return 1
        if text2 and text2 in line:
            return 2

def main():
    print('args received', sys.argv)
    if len(sys.argv) != 3:
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

    print(f'Copying POC from /share')
    subprocess.run(['cp', '/share/poc.c', '/root/poc.c'], check=True, stderr=subprocess.STDOUT)

    os.chdir('/root')

    print(f'Building POC')
    subprocess.run(['gcc', '-pthread', '-static', '/root/poc.c', '-o', '/root/poc'], check=True, stderr=subprocess.STDOUT)
    
    print(f'chmod +x poc')
    subprocess.run(['chmod', '+x', '/root/poc'], check=True, stderr=subprocess.STDOUT)

    qemu_command =[
        "qemu-system-x86_64",
        '-m',
        f'{memory}G',
        '-smp',
        f'{cores},sockets=1,cores=2',
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

                            # login prompt,         copy poc                                                            run poc
    vm_state_txt =          ['syzkaller ttyS0', 'syzkaller login:', 'permitted by applicable law.', 'root@syzkaller:~#',                                                 'root@syzkaller:~#']
    vm_state_internal_cmd = ['\n',              'root\n',            '\n',                            '\n',                                                             './poc\n'         ]
    vm_state_external_cmd = [False,             False,               False,                         'scp -P 10021 -i /share/bullseye.id_rsa /root/poc root@localhost:',  False            ]
    vm_state_i = 0
    vm_state_max = len(vm_state_txt)

    qemu_output = []
    qemu_proc = subprocess.Popen(qemu_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    waitForText(qemu_proc, 'syzkaller ttyS0')
    qemu_proc.stdin.write(b'\n')
    qemu_proc.stdin.flush()
    waitForText(qemu_proc, 'syzkaller login:')
    qemu_proc.stdin.write(b'root\n')
    qemu_proc.stdin.flush()
    waitForText(qemu_proc, 'permitted by applicable law.')
    qemu_proc.stdin.write(b'\n')
    qemu_proc.stdin.flush()
    waitForText(qemu_proc, 'root@syzkaller:~#')
    subprocess.run('scp -P 10021 -o StrictHostKeyChecking=no -i /share/key /root/poc root@localhost:'.split(' '), check=True, stderr=subprocess.STDOUT)
    threading.Timer(60 * 10, timeout).start()
    qemu_proc.stdin.write(b'./poc\n')
    qemu_proc.stdin.flush()
    while found := waitForText(qemu_proc, 'root@syzkaller:~#', 'BUG: '):
        if found == 2:
            print('BUG found')
            os.kill( qemu_proc.pid, 9)
            qemu_proc.wait()
            os._exit(1)
        qemu_proc.stdin.write(b'./poc\n')
        qemu_proc.stdin.flush()
        # for line in process.stdout:
        #     decoded_line = line.decode('ascii', 'ignore')
        #     print(decoded_line, end='')
        #     qemu_output.append(decoded_line)
        #     if (vm_state_txt[vm_state_i] in decoded_line):
        #         print(f'VM state {vm_state_i} reached')
        #         if(vm_state_external_cmd[vm_state_i]):
        #             print(f'Running external command {vm_state_external_cmd[vm_state_i]}')
        #             subprocess.run(vm_state_external_cmd[vm_state_i].split(' '), check=True, stderr=subprocess.STDOUT)
        #             print(f'Ran external command {vm_state_external_cmd[vm_state_i]}')
        #         if(vm_state_internal_cmd[vm_state_i]):
        #             print(f'Writing to stdin: {vm_state_internal_cmd[vm_state_i]}')
        #             process.stdin.write(vm_state_internal_cmd[vm_state_i].encode('utf-8'))
        #             print(f'Wrote internal command {vm_state_internal_cmd[vm_state_i]}')
        #         process.stdin.flush()
        #         if(vm_state_i < vm_state_max - 1): # loop last step
        #             vm_state_i += 1


if __name__ == '__main__':
    main()