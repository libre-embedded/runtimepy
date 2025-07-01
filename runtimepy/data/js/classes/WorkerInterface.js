class WorkerInterface {
  constructor(name, _worker) {
    this.name = name;
    this.worker = _worker;
  }

  send(data, param) {
    this.worker.postMessage({name : this.name, event : data}, param);
  }

  command(data) { this.send({kind : "command", value : data}); }

  bus(key, data) { this.worker.postMessage({key : key, bus : data}); }

  toWorker(data, param) { return this.send({"worker" : data}, param); }
}
