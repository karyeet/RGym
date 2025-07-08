import {Job} from './JobAbstract';
import {JobLoader} from './JobLoader';

class Manager {
  private jobs: Job[] = [];
  private jobid = 0;
  private jobLoader: JobLoader;
  private dataPath: string;

  constructor(dataPath: string) {
    this.jobLoader = new JobLoader();
    this.dataPath = dataPath;
  }

  async loadJobs(): Promise<void> {
    await this.jobLoader.loadJobs(this.dataPath, this);
    // get highest jobid
    for (const job of this.jobs) {
      if (job.jobid > this.jobid) {
        this.jobid = job.jobid;
      }
    }
  }

  getFreeJobId(): number {
    return ++this.jobid; // return jobid+1
  }

  addJob(job: Job): void {
    this.jobs.push(job);
    if (job.jobid > this.jobid) {
      this.jobid = job.jobid; // set jobid to job.jobid
    }
  }

  getJob(jobid: number): Job | undefined {
    return this.jobs.find(job => job.jobid === jobid);
  }

  startJob(jobid: number): void {
    const job = this.jobs.find(job => job.jobid === jobid);
    if (job) {
      job.start();
    } else {
      throw new Error('Job not found');
    }
  }

  getJobLogs(jobid: number): string {
    const job = this.jobs.find(job => job.jobid === jobid);
    if (job) {
      return job.getLogs();
    } else {
      throw new Error('Job not found');
    }
  }

  isJobRunning(jobid: number): boolean {
    const job = this.jobs.find(job => job.jobid === jobid);
    if (job) {
      return job.isRunning();
    } else {
      throw new Error('Job not found');
    }
  }

  getExitCode(jobid: number): number {
    const job = this.jobs.find(job => job.jobid === jobid);
    if (job) {
      return job.getExitCode();
    } else {
      throw new Error('Job not found');
    }
  }
}

export {Manager};
