import {createWriteStream, mkdirSync} from 'fs';
import {spawn} from 'child_process';
import {writeFileSync} from 'fs';
//import {createHash} from 'crypto';

import {Job, JobOptions} from './Job';

interface BuildOptions extends JobOptions {
  kernel_config: string;
  git_repo: string;
  git_hash: string;
  patch: string | false;
}

class BuildJob extends Job {
  //private process: ChildProcessWithoutNullStreams;
  private logs = '';
  constructor(jobid: number, options: BuildOptions) {
    mkdirSync(`./${jobid}`);
    const logStream = createWriteStream(`./${jobid}/build.log`);
    writeFileSync(`./${jobid}/.config`, options.kernel_config);
    super(jobid, options, logStream);
    if (options.patch) {
      writeFileSync(`./${jobid}/.patch`, options.patch);
    }
  }
  getLogs(): string {
    return this.logs;
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
    const command_options = [
      'run',
      '--rm',
      '-v',
      `./${this.jobid}:/share`,
      'build-kernel',
      (this.options as BuildOptions).git_hash,
      (this.options as BuildOptions).git_repo,
      String((this.options as BuildOptions).cores),
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

    process.on('exit', (code, _) => {
      this.complete = true;
      this.success = code === 0;
      this.logStream.end();
      console.log('build exited with code', code);
    });
    return true;
  }
}

export {BuildJob, BuildOptions};
