import {ChildProcess, exec} from 'node:child_process';

class qemu {
  private pathToQemu: string;
  private qemuProcess: ChildProcess;
  constructor(pathToQemu = '/usr/bin/qemu-system-x86_64') {
    this.pathToQemu = pathToQemu;
  }

  public start(): void {
    
  }
}
