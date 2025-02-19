class container {
  constructor() {
    this.containerId = null;
  }

  async createContainer(imageName) {
    const docker = new Docker();
    const container = await docker.createContainer({
      Image: imageName,
    });
    this.containerId = container.id;
  }
}