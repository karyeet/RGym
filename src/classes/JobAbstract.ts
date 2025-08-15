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
  exitCode: number;
  running: boolean;
  started_at: number;
  options: JobOptions;
  jobPath: string;
  jobid: number;
  type: string;
}

enum JobEvents {
  STARTED = 'started',
  EXITED = 'exited',
}

abstract class Job extends EventEmitter {
  protected exitCode = -1;
  protected running = false;
  protected started_at = -1;
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
    this.exitCode = state.exitCode;
    this.running = state.running;
    this.started_at = state.started_at;
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
    return readFileSync(path.join(this.jobPath, 'job.log'), 'utf8');
  }

  getState(): JobState {
    try {
      const state: JobState = JSON.parse(
        readFileSync(path.join(this.jobPath, 'state.json'), 'utf8'),
      );
      return state;
    } catch (error) {
      throw new Error(
        'Error reading job state from ' + this.jobPath + ' : ' + error,
      );
    }
  }

  saveState(): void {
    const state: JobState = {
      jobid: this.jobid,
      jobPath: this.jobPath,
      options: this.options,
      exitCode: this.exitCode,
      running: this.running,
      started_at: this.started_at,
      type: this.type,
    };
    writeFileSync(path.join(this.jobPath, 'state.json'), JSON.stringify(state));
  }
  getExitCode(): number {
    return this.exitCode;
  }
  isRunning(): boolean {
    return this.running;
  }
  getStartedTimestamp(): number {
    return this.started_at;
  }

  _start(): void {
    this.started_at = Date.now();
    this.running = true;
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
