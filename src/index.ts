import {Manager} from './classes/Manager';
import {WebServer} from './classes/WebServer';
import {
  BuildJSONSchema,
  ReproducerJSONSchema,
  _BuildJSONSchema,
  _ReproducerJSONSchema,
  JobIDSchema,
  _JobIDSchema,
} from './classes/YupTypes';
import {BuildJob, BuildOptions} from './classes/jobs/BuildJob';
import {ReproducerJob, ReproducerOptions} from './classes/jobs/ReproducerJob';

interface _config {
  data_path: string;
  rootfs_path: string;
  sshkey_path: string;
}

// eslint-disable-next-line n/no-unpublished-require
const config: _config = require('../../config.json');

const manager = new Manager(config.data_path);
const webServer = new WebServer();

webServer.createPostRoute(
  '/addjobbuild',
  BuildJSONSchema,
  (data: _BuildJSONSchema) => {
    const job_id = manager.getFreeJobId();
    const options: BuildOptions = {
      kernel_config: data.kernel_config,
      git_repo: data.git_repo,
      git_hash: data.git_hash,
      patch: data.patch,
      cores: data.cores,
      metadata: data.metadata,
      timeout: data.timeout,
      compiler: data.compiler,
      compilerMajorVersion: data.compilerMajorVersion,
    };
    const new_job = BuildJob.newJob(job_id, options, config.data_path);
    manager.addJob(new_job);
    return job_id;
  },
);

webServer.createPostRoute(
  '/addjobreproducer',
  ReproducerJSONSchema,
  (data: _ReproducerJSONSchema) => {
    const job_id = manager.getFreeJobId();
    const options: ReproducerOptions = {
      bzImageJobId: data.bzImageJobId,
      rootfsPath: config.rootfs_path,
      sshkeyPath: config.sshkey_path,
      memory: data.memory,
      boot_options: data.boot_options,
      reproducer: data.reproducer,
      cores: data.cores,
      metadata: data.metadata,
      timeout: data.timeout,
      reproducerType: data.reproducerType,
    };
    const new_job = ReproducerJob.newJob(job_id, options, config.data_path);
    manager.addJob(new_job);
    return job_id;
  },
);

webServer.createPostRoute('/start', JobIDSchema, (data: _JobIDSchema) => {
  const job = manager.getJob(data.jobid);
  if (job) {
    if (!job.isRunning() && job.getStartedTimestamp() < 0) {
      job.start();
      return true;
    } else {
      return false;
    }
  } else {
    return false;
  }
});

webServer.createGetRoute('/getExitCode', JobIDSchema, (param: _JobIDSchema) => {
  const jobid = param.jobid;
  const job = manager.getJob(jobid);
  if (job) {
    return job.getExitCode();
  } else {
    return 'Job not found';
  }
});

webServer.createGetRoute('/isRunning', JobIDSchema, (param: _JobIDSchema) => {
  const jobid = param.jobid;
  const job = manager.getJob(jobid);
  if (job) {
    return job.isRunning();
  } else {
    return 'Job not found';
  }
});

webServer.createGetRoute('/getLogs', JobIDSchema, (param: _JobIDSchema) => {
  const jobid = param.jobid;
  const job = manager.getJob(jobid);
  if (job) {
    return job.getLogs();
  } else {
    return 'Job not found';
  }
});

webServer.createGetRoute('/getState', JobIDSchema, (param: _JobIDSchema) => {
  const jobid = param.jobid;
  const job = manager.getJob(jobid);
  if (job) {
    return JSON.stringify(job.getState());
  } else {
    return 'Job not found';
  }
});

manager
  .loadJobs()
  .then(() => {
    console.log('Jobs loaded');
    webServer.start();
  })
  .catch(e => {
    console.log('Error loading jobs: ', e);
  });
