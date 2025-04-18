import {writeFileSync, WriteStream} from 'node:fs';
import path from 'node:path';
import {mkdirSync, createWriteStream, readFileSync} from 'node:fs';
import EventEmitter from 'node:events';

interface JobOptions {
  timeout: number;
  cores: number;
  metadata: string;
}

interface JobState {
  started: boolean;
  success: boolean;
  complete: boolean;
  options: JobOptions;
  jobPath: string;
  jobid: number;
  type: string;
}

enum JobEvents {
  STARTED = 'started',
  COMPLETE = 'complete',
}

abstract class Job extends EventEmitter {
  protected started = false;
  protected success = false;
  protected complete = false;
  protected options: JobOptions;
  protected logStream: WriteStream;
  protected jobPath: string;
  protected type: string;
  public jobid: number;
  constructor(state: JobState) {
    super();
    this.jobid = state.jobid;
    this.jobPath = state.jobPath;
    this.options = state.options;
    this.started = state.started;
    this.success = state.success;
    this.complete = state.complete;
    this.type = state.type;
    this.jobid = state.jobid;
    this.jobPath = state.jobPath;
    this.options = state.options;
    mkdirSync(this.jobPath, {recursive: true});
    this.logStream = createWriteStream(path.join(this.jobPath, 'job.log'), {
      flags: 'a',
    });
    this.saveState();
  }

  getLogs(): string {
    return readFileSync(path.join(this.jobPath, 'job.log'), 'ascii');
  }

  getState(): JobState {
    return JSON.parse(
      readFileSync(path.join(this.jobPath, 'state.json'), 'ascii'),
    );
  }

  saveState(): void {
    const state: JobState = {
      jobid: this.jobid,
      jobPath: this.jobPath,
      options: this.options,
      started: this.started,
      success: this.success,
      complete: this.complete,
      type: this.type,
    };
    writeFileSync(path.join(this.jobPath, 'state.json'), JSON.stringify(state));
  }
  isSuccess(): boolean {
    return this.success;
  }
  isComplete(): boolean {
    return this.complete;
  }
  isStarted(): boolean {
    return this.started;
  }
  abstract start(): void;
  setMetadata(metadata: string): void {
    this.options.metadata = metadata;
  }
  getMetadata(): string {
    return this.options.metadata;
  }
}

export {Job, JobOptions, JobState, JobEvents};
