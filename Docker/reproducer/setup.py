#!/usr/bin/python3
import subprocess
import sys
import os
import threading



def print(*args, **kwargs):
    return __builtins__.print(*args, flush=True, **kwargs)

def timeout():
    print('Timeout')
    os._exit(0) # timeout is good

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
    if len(sys.argv) != 4:
        print('Usage: setup.py <memory> <cores> <timeout_sec>')
        sys.exit(1)

    memory = sys.argv[1]
    cores = sys.argv[2]
    timeout_sec = int(sys.argv[3])

    if(len(memory) < 1):
        print('No memory provided.')
        sys.exit(1)

    if(len(cores) < 1):
        print('No memory provided.')
        sys.exit(1)

    if(timeout_sec < 1):
        print('No timeout provided.')
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
        f'sockets=1,cores={cores},threads=1',
        '-object',
        f'memory-backend-ram,id=mem0,size={memory}G',
        '-numa',
        f'node,nodeid=0,cpus=0-{cores-1},memdev=mem0',
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
    subprocess.run('scp -P 10021 -o StrictHostKeyChecking=no -i /share/key /root/poc root@localhost:'.split(' '), check=True, stderr=subprocess.STDOUT)
    threading.Timer(timeout_sec, timeout).start()
    qemu_proc.stdin.write(b'./poc\n')
    qemu_proc.stdin.flush()
    while found := waitForText(qemu_proc, ['root@syzkaller:~#', 'BUG: ']):
        if found == 2:
            print('BUG found')
            os._exit(1)
        qemu_proc.stdin.write(b'./poc\n')
        qemu_proc.stdin.flush()


if __name__ == '__main__':
    main()