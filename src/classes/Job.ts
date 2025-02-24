import {WriteStream} from 'node:fs';

interface JobOptions {
  timeout: number;
  matchTerminations: string[]; // regex
  cores: number;
}

abstract class Job {
  protected started = false;
  protected success = false;
  protected complete = false;
  protected options: JobOptions;
  protected logStream: WriteStream;
  public jobid: number;
  constructor(jobid: number, jobOptions: JobOptions, logStream: WriteStream) {
    this.jobid = jobid;
    this.options = jobOptions;
    this.logStream = logStream;
  }
  abstract getLogs(): string;
  abstract isSuccess(): boolean;
  abstract isComplete(): boolean;
  abstract start(): void;
}

enum JobType {
  BUILD = 'build',
  REPRODUCE = 'reproducer',
}

export {Job, JobOptions, JobType};
