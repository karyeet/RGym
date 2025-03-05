import {Manager} from './Manager';
import {readdirSync} from 'node:fs';
import path from 'node:path';
import {Job, JobState} from './JobAbstract';
import {time} from 'node:console';

interface JobType {
  [key: string]: Function;
}

function getDirectories(path: string): string[] {
  let files = readdirSync(path, {withFileTypes: true});
  files = files.filter(dirent => dirent.isDirectory());
  const dirs: string[] = files.map(dirent => dirent.name);
  return dirs;
}

class JobLoader {
  private jobTypes: JobType = {};
  private readySemaphore = 0;
  constructor(jobTypesPath = path.join(__dirname, 'jobs')) {
    const files = readdirSync(jobTypesPath);
    for (const file of files) {
      if (file.endsWith('.js')) {
        this.readySemaphore++;
        import(path.join(jobTypesPath, file))
          .then(module => {
            const type: string = module.type;
            const proxyConstructor = module.proxyConstructor;
            console.log('new type', type);
            this.jobTypes[type] = proxyConstructor;
            this.readySemaphore--;
          })
          .catch(err => {
            console.log(err);
          });
      }
    }
  }

  async loadJobs(jobsPath: string, manager: Manager): Promise<void> {
    await this.waitForReady();
    // load jobs from disk
    const jobsFolders = getDirectories(jobsPath);
    for (const jobFolder of jobsFolders) {
      const state: JobState = require(
        path.join(jobsPath, jobFolder, 'state.json'),
      );
      if (state.type in this.jobTypes) {
        state.started = false; // jobs cant be loaded as started
        manager.addJob(this.jobTypes[state.type](state));
      } else {
        console.log(`Job type ${state.type} not found`);
      }
    }
  }

  async waitForReady(): Promise<boolean> {
    while (this.readySemaphore > 0) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    return true;
  }
}

export {JobLoader};
