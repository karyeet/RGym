import {Job, JobOptions, JobType} from './Job';
import {BuildJob, BuildOptions} from './BuildJob';
import {ReproducerJob, ReproducerOptions} from './ReproducerJob';

class Manager {
  private jobs: Job[] = [];
  private jobid = 0;

  submitJob(jobType: JobType, options: JobOptions): number {
    let job: Job;
    switch (jobType) {
      case 'build': {
        job = new BuildJob(this.jobid, options as BuildOptions);
        break;
      }
      case 'reproducer': {
        job = new ReproducerJob(this.jobid, options as ReproducerOptions);
        break;
      }
      default:
        throw new Error('Invalid job type');
    }
    this.jobs.push(job);
    this.jobid++;
    return job.jobid;
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

  isJobComplete(jobid: number): boolean {
    const job = this.jobs.find(job => job.jobid === jobid);
    if (job) {
      return job.isComplete();
    } else {
      throw new Error('Job not found');
    }
  }

  isJobSuccess(jobid: number): boolean {
    const job = this.jobs.find(job => job.jobid === jobid);
    if (job) {
      return job.isSuccess();
    } else {
      throw new Error('Job not found');
    }
  }
}

export {Manager};
