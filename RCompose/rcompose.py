import requests
import time

port = 7070

"""
Was the job successful.
For building, this is if a bzImage was produced.
For reproducing, this is if the job ran without triggernig a bug.
"""
def isSuccess(jobid: str) -> bool:
    response = requests.get(f'http://localhost:{port}/issuccess?jobid={jobid}')
    return response.json()

# Is the job complete (has the job ran once, successfully or with failure).
def isComplete(jobid: str) -> bool:
    response = requests.get(
        f'http://localhost:{port}/iscomplete?jobid={jobid}')
    return response.json()

# Is the job started (running)
def isStarted(jobid: str) -> bool:
    response = requests.get(f'http://localhost:{port}/isstarted?jobid={jobid}')
    return response.json()

# Get the logs for a job as a string
def getLogs(jobid: str) -> str:
    response = requests.get(f'http://localhost:{port}/getlogs?jobid={jobid}')
    return response.text


"""
kernel_config is the .config file,
git_repo is the git repository,
git_hash is the git commit hash,
patch is the patch to apply, can be an empty string
timeout is the maximum time the job can run in seconds (not implemented for build)
cores is the number of cores to use
metadata is a string that will be stored with the job, can be an empty string although I suggest it be the bug link
""" 
def addBuildJob(kernel_config: str,
                git_repo: str,
                git_hash: str,
                patch: str,
                timeout: int,
                cores: int,
                metadata: str) -> str:
    response = requests.post(f'http://localhost:{port}/addjobbuild', json={
        'kernel_config': kernel_config,
        'git_repo': git_repo,
        'git_hash': git_hash,
        'patch': patch,
        'timeout': timeout,
        'cores': cores,
        'metadata': metadata
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
"""
def addReproduceJob(bzImageJobId: str,
                    memory: int,
                    boot_options: str,
                    reproducer: str,
                    timeout: int,
                    cores: int,
                    metadata: str
                    ) -> str:
    response = requests.post(f'http://localhost:{port}/addjobreproducer', json={
        'bzImageJobId': bzImageJobId,
        'memory': memory,
        'boot_options': boot_options,
        'reproducer': reproducer,
        'timeout': timeout,
        'cores': cores,
        'metadata': metadata
    })
    return response.text

# wait for job to complete, blocking, returns success
def waitForJob(jobid: str) -> bool:
    while not isComplete(jobid):
        time.sleep(4)
    return isSuccess(jobid)


def start(jobid: str):
    response = requests.post(f'http://localhost:{port}/start', json={'jobid': jobid})
    return response.json()

