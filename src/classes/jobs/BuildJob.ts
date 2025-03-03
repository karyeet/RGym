import {spawn} from 'child_process';
import {mkdirSync, writeFileSync, existsSync} from 'fs';
//import {createHash} from 'crypto';
import path from 'path';

import {Job, JobOptions, JobState} from '../JobAbstract';

const type = 'BUILD';

interface BuildOptions extends JobOptions {
  kernel_config: string;
  git_repo: string;
  git_hash: string;
  patch: string | false;
}

class BuildJob extends Job {
  constructor(state: JobState) {
    super(state);
  }
  // new job should be used for new jobs, loading jobs can be done direcrly from constructor
  static newJob(jobid: number, options: BuildOptions, dataPath: string) {
    // overload 1
    const new_state: JobState = {
      jobid,
      jobPath: path.join(dataPath, String(jobid)),
      options,
      started: false,
      success: false,
      complete: false,
      type: type,
    };
    if (!existsSync(new_state.jobPath)) {
      mkdirSync(new_state.jobPath);
    }
    writeFileSync(
      path.join(new_state.jobPath, '.config'),
      options.kernel_config,
    );
    if (options.patch) {
      writeFileSync(path.join(new_state.jobPath, '.patch'), options.patch);
    }
    return new BuildJob(new_state);
  }

  isSuccess(): boolean {
    return this.success;
  }
  isComplete(): boolean {
    return this.complete;
  }
  start(): boolean {
    if (this.started) {
      return false;
    }
    const options = this.options as BuildOptions;
    const command_options = [
      'run',
      '--rm',
      '-v',
      `${this.jobPath}:/share`,
      'build-kernel',
      options.git_hash, // git hash
      options.git_repo, // git repo
      String(options.cores), // cores
    ];
    console.log('spawning new build with options', command_options.join(' '));
    const process = spawn('docker', command_options);

    //process.stdout.on('data', data => {
    //  this.logs += data;
    //  this.logStream.write(data);
    //  console.log(data.toString());
    //});
    process.stdout.pipe(this.logStream, {end: false});
    process.stderr.pipe(this.logStream, {end: false});

    this.started = true;
    this.saveState();

    process.on('exit', (code, _) => {
      this.complete = true;
      this.success = code === 0;
      this.logStream.end();
      this.saveState();
      console.log('Build exited with code', code);
    });
    return true;
  }
}

function proxyConstructor(state: JobState) {
  return new BuildJob(state);
}

export {BuildJob, type, BuildOptions, proxyConstructor};
