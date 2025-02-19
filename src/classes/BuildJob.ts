import {Job, JobOptions} from './Job';

interface BuildOptions extends JobOptions {
  kernel_config: string;
  cores: number;
  git_repo: string;
  git_hash: string;
  patch: string;
}

class BuildJob extends Job {
  constructor(jobid: number, options: BuildOptions) {
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
  setOptions(options: BuildOptions): void {
    throw new Error('Method not implemented.');
  }
}

export {BuildJob, BuildOptions};
