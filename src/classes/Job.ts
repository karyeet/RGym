interface JobOptions {
  timeout: number;
  matchTerminations: string[]; // regex
}

abstract class Job {
  public jobid: number;
  constructor(jobid: number) {
    this.jobid = jobid;
  }
  abstract getLogs(): string;
  abstract isSuccess(): boolean;
  abstract isComplete(): boolean;
  abstract start(): void;
  abstract setOptions(options: Object): void;
}

enum JobType {
  BUILD = 'build',
  REPRODUCE = 'reproducer',
}

export {Job, JobOptions, JobType};
