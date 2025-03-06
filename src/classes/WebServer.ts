import express from 'express';
import {schema} from './YupTypes';

class WebServer {
  private app: express.Application;
  private port: number;
  constructor(port = 7070) {
    this.app = express();
    this.app.use(express.json({limit: '5mb'}));
    this.port = port;
  }

  start() {
    this.app.listen(this.port, () => {
      console.log(`Server is running on http://localhost:${this.port}`);
    });
  }

  createPostRoute(route: string, validator: schema, cb: Function) {
    console.log('Adding POST', route);
    this.app.post(route, async (req, res) => {
      const data = req.body;
      console.log(data);
      let validatedData;
      try {
        validatedData = await validator.validate(data);
      } catch (e) {
        console.log(e);
        res.status(400).send('Invalid data');
        return;
      }
      res.send(String(cb(validatedData)));
    });
  }

  createGetRoute(route: string, validator: schema, cb: Function) {
    console.log('Adding GET', route);
    this.app.get(route, async (req, res) => {
      const data = req.query;
      console.log(data);
      let validatedData;
      try {
        validatedData = await validator.validate(data);
      } catch (e) {
        console.log(e);
        res.status(400).send('Invalid data');
        return;
      }
      res.send(String(cb(validatedData)));
    });
  }
}

export {WebServer};
