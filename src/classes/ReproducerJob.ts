import {Job, JobOptions} from './Job';

interface ReproducerOptions extends JobOptions {
  bzImagePath: string;
  rootfsPath: string;
  cores: number;
  memory: number;
  boot_options: string;
}

class ReproducerJob extends Job {
  constructor(jobid: number, options: ReproducerOptions) {
    super(jobid);
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
