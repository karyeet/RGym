import express from 'express';

interface route {
  route: string;
  cb: Function;
}

class WebServer {
  private app: express.Application;
  private port: number;
  constructor(port = 3000) {
    this.app = express();
    this.app.use(express.json());
    this.port = port;
  }

  start() {
    this.app.listen(this.port, () => {
      console.log(`Server is running on http://localhost:${this.port}`);
    });
  }

  createRoute(route: string, cb: Function) {
    this.app.post(route, (req, res) => {
      const data = req.body;
      console.log(data);
      res.send(cb(data));
    });
  }
}

export {WebServer};
