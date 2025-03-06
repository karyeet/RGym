import rcompose

config = open('.config').read()
patch = open('.patch').read()
poc = open('poc.c').read()

bjobid = rcompose.addBuildJob(
  timeout=1000,
  kernel_config=config,
  cores=8,
  git_repo='https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git',
  git_hash='fcc79e1714e8',
  patch=patch,
  metadata='https://syzkaller.appspot.com/bug?extid=2d9f5f948c31dcb7745e',
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
  memory=1,
  boot_options=' ',
  reproducer=poc,
  timeout=60*10,
  cores=2,
  metadata='https://syzkaller.appspot.com/bug?extid=2d9f5f948c31dcb7745e',
)

print("rjob id", rjobid)

rst = rcompose.isStarted(rjobid)
rc = rcompose.isComplete(rjobid)
rsu = rcompose.isSuccess(rjobid)
print(f'started={rst}, complete={rc}, success={rsu}')

print("start 1 (true)",rcompose.start(rjobid))
print("start 2 (false)",rcompose.start(rjobid))

print("Build job started")
rst = rcompose.isStarted(rjobid)
rc = rcompose.isComplete(rjobid)
rsu = rcompose.isSuccess(rjobid)
print(f'started={rst}, complete={rc}, success={rsu}')

print("Build job finished with", rcompose.waitForJob(rjobid))
rst = rcompose.isStarted(rjobid)
rc = rcompose.isComplete(rjobid)
rsu = rcompose.isSuccess(rjobidr)
print(f'started={rst}, complete={rc}, success={rsu}')
