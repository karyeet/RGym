import {createWriteStream} from 'fs';
import {Job, JobOptions} from './Job';

interface ReproducerOptions extends JobOptions {
  bzImagePath: string;
  rootfsPath: string;
  memory: number;
  boot_options: string;
}

class ReproducerJob extends Job {
  constructor(jobid: number, options: ReproducerOptions) {
    const logStream = createWriteStream(`./${jobid}/reproducer.log`);
    super(jobid, options, logStream);
    this.setOptions(options);
  }
  getLogs(): string {
    throw new Error('Method not implemented.');
  }
  isSuccess(): boolean {
    throw new Error('Method not implemented.');
  }
  isComplete(): boolean {
    throw new Error('Method not implemented.');
  }
  start(): void {
    throw new Error('Method not implemented.');
  }
  setOptions(options: Object): void {
    throw new Error('Method not implemented.');
  }
}

export {ReproducerJob, ReproducerOptions};
