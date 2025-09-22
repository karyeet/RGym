import {Job, JobOptions, JobState, JobEvents} from '../JobAbstract';
import path from 'path';
import {existsSync, writeFileSync, mkdirSync} from 'fs';
import {spawn} from 'child_process';
interface ReproducerOptions extends JobOptions {
  bzImageJobId: string;
  rootfsPath: string;
  memory: number;
  boot_options: string;
  reproducer: string;
  reproducerType: ReproducerType;
  sshkeyPath: string;
  docker_image: string;
}

enum ReproducerType {
  SYZ = 'syz',
  C = 'c',
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
      started_at: -1,
      running: false,
      exitCode: -1,
      type: type,
    };
    if (!existsSync(new_state.jobPath)) {
      mkdirSync(new_state.jobPath);
    }
    writeFileSync(path.join(new_state.jobPath, 'poc'), options.reproducer);
    return new ReproducerJob(new_state);
  }

  start(): boolean {
    if (this.running) {
      return false;
    }
    super._start();
    //--device=/dev/kvm
    const options = this.options as ReproducerOptions;
    //qemu-system-x86_64 -m 2G -smp 2,sockets=2,cores=1 -drive file=$DISK_IMAGE,format=raw -net nic,model=e1000 -net user,host=10.0.2.10,hostfwd=tcp::10022-:22 -enable-kvm -nographic -snapshot -machine pc-q35-7.1
    const command_options = [
      'run',
      '--rm',
      '--device=/dev/kvm',
      '-v',
      `${path.join(this.jobPath, 'poc')}:/share/poc:ro`,
      '-v',
      `${options.rootfsPath}:/share/rootfs:ro`,
      '-v',
      `${options.sshkeyPath}:/share/key:ro`,
      '-v',
      `${path.join(this.jobPath, '..', options.bzImageJobId, 'bzImage')}:/share/bzImage:ro`,
      options.docker_image,
      String(options.memory), // memory
      String(options.cores), // cores
      String(options.timeout), // timeout
      options.reproducerType, // reproducer type
    ];
    console.log(
      'spawning new reproducer with options',
      command_options.join(' '),
    );
    const process = spawn('docker', command_options);
    this.emit(JobEvents.STARTED);
    //process.stdout.on('data', data => {
    //  this.logBuffer += data;
    //  this.logStream.write(data);
    //  //console.log(data.toString());
    //});
    //process.stderr.on('data', data => {
    //  this.logBuffer += data;
    //  this.logStream.write(data);
    //  //console.log(data.toString());
    //});

    process.stdout.pipe(this.logStream, {end: false});
    process.stderr.pipe(this.logStream, {end: false});

    this.saveState();

    process.on('exit', (code: number) => {
      this.running = false;
      this.exitCode = code;
      this.logStream.end();
      this.saveState();
      console.log('Reproducer exited with code', code);
      this.emit(JobEvents.EXITED);
    });
    return true;
  }
}

function proxyConstructor(state: JobState) {
  return new ReproducerJob(state);
}

export {
  ReproducerJob,
  type,
  ReproducerOptions,
  proxyConstructor,
  ReproducerType,
};
