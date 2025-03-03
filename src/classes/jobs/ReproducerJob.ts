import {createWriteStream} from 'fs';
import {Job, JobOptions, JobState} from '../JobAbstract';
import path from 'path';
import {existsSync, writeFileSync, mkdirSync} from 'fs';
import {spawn} from 'child_process';
interface ReproducerOptions extends JobOptions {
  bzImagePath: string;
  rootfsPath: string;
  memory: number;
  boot_options: string;
  reproducer: string;
}

const type = 'REPRODUCER';

class ReproducerJob extends Job {
  private logBuffer = '';
  constructor(state: JobState) {
    super(state);
  }
  // new job should be used for new jobs, loading jobs can be done direcrly from constructor
  static newJob(jobid: number, options: ReproducerOptions, dataPath: string) {
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
    writeFileSync(path.join(new_state.jobPath, 'poc.c'), options.reproducer);
    return new ReproducerJob(new_state);
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
    //--device=/dev/kvm
    const options = this.options as ReproducerOptions;
    //qemu-system-x86_64 -m 2G -smp 2,sockets=2,cores=1 -drive file=$DISK_IMAGE,format=raw -net nic,model=e1000 -net user,host=10.0.2.10,hostfwd=tcp::10022-:22 -enable-kvm -nographic -snapshot -machine pc-q35-7.1
    const command_options = [
      '-m',
      `${options.memory}G`,
      '-smp',
      `${options.cores},sockets=1,cores=1`,
      '-drive',
      `file=${options.rootfsPath},format=raw`,
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
      `${options.bzImagePath}`,
    ];
    console.log(
      'spawning new reproducer with options',
      command_options.join(' '),
    );
    const process = spawn('qemu-system-x86_64', command_options);

    process.stdout.on('data', data => {
      this.logBuffer += data;
      this.logStream.write(data);
      //console.log(data.toString());
    });
    process.stderr.on('data', data => {
      this.logBuffer += data;
      this.logStream.write(data);
      //console.log(data.toString());
    });

    //process.stdout.pipe(this.logStream, {end: false});
    //process.stderr.pipe(this.logStream, {end: false});

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
  return new ReproducerJob(state);
}

export {ReproducerJob, type, ReproducerOptions, proxyConstructor};
