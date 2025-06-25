import rcompose
import os

config = open('.config').read()
patch = open('.patch').read()
poc = open('poc.syz').read()

bjob_compiler_string = rcompose.read_full_compiler(config)
# print(bjob_compiler_string) # Debian clang version 15.0.6
bjob_compiler_info = rcompose.parse_compiler_string(bjob_compiler_string)
# {'type ': 'clang', 'major': 15, 'minor': 0, 'patch': 6}

print(bjob_compiler_info['type'], bjob_compiler_info['major'])

bjobid = rcompose.addBuildJob(
  timeout=1000,
  kernel_config=config,
  cores=8,
  git_repo='https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git',
  git_hash='480e035fc4c714fb5536e64ab9db04fedc89e910',
  patch=patch,
  metadata='https://syzkaller.appspot.com/bug?id=0a1226f75a35b80ef0c7025acb60b71c4cbc0dcd',
  compiler=bjob_compiler_info['type'],
  compilerMajorVersion=bjob_compiler_info['major'],
)

print("bjob id", bjobid)

bst = rcompose.isStarted(bjobid)
bc = rcompose.isComplete(bjobid)
bsu = rcompose.isSuccess(bjobid)
print(f'started={bst}, complete={bc}, success={bsu}')

print("start 1 (true)",rcompose.start(bjobid))
print("start 2 (false)",rcompose.start(bjobid))

print("Build job started")
bst = rcompose.isStarted(bjobid)
bc = rcompose.isComplete(bjobid)
bsu = rcompose.isSuccess(bjobid)
print(f'started={bst}, complete={bc}, success={bsu}')

print("Build job finished with", rcompose.waitForJob(bjobid))
bst = rcompose.isStarted(bjobid)
bc = rcompose.isComplete(bjobid)
bsu = rcompose.isSuccess(bjobid)
print(f'started={bst}, complete={bc}, success={bsu}')

rjobid = rcompose.addReproduceJob(
  bzImageJobId=bjobid,
  memory=2,
  boot_options=' ',
  reproducer=poc,
  timeout=60*10,
  cores=2,
  metadata='https://syzkaller.appspot.com/bug?extid=2d9f5f948c31dcb7745e',
  reproducerType='syz',
)

print("rjob id", rjobid)

rst = rcompose.isStarted(rjobid)
rc = rcompose.isComplete(rjobid)
rsu = rcompose.isSuccess(rjobid)
print(f'started={rst}, complete={rc}, success={rsu}')

print("start 1 (true)",rcompose.start(rjobid))
print("start 2 (false)",rcompose.start(rjobid))

print("Reproducer job started")
rst = rcompose.isStarted(rjobid)
rc = rcompose.isComplete(rjobid)
rsu = rcompose.isSuccess(rjobid)
print(f'started={rst}, complete={rc}, success={rsu}')

print("Reproducer job finished with", rcompose.waitForJob(rjobid))
rst = rcompose.isStarted(rjobid)
rc = rcompose.isComplete(rjobid)
rsu = rcompose.isSuccess(rjobid)
print(f'started={rst}, complete={rc}, success={rsu}')
