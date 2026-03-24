class DataConnection extends JsonConnection {
  init() {
    this.environment_ids = {};
    this.environment_channels = {};
    this.environment_types = {};

    // need prim channel types

    for (const key in this.environments) {
      let env = this.environments[key];
      let env_id = env["names"]["id"];
      this.environment_ids[env_id] = key;

      let channels = {};
      let types = {};
      for (const name in env["names"]["channels"]) {
        let chan_id = env["names"]["channels"][name];
        channels[chan_id] = name;
        if (name in env["channels"]) {
          types[chan_id] = env["channels"][name]["type"];
        }
      }
      this.environment_channels[env_id] = channels;
      this.environment_types[env_id] = types;
    }
  }

  handle_payload(buffer) {
    let env, chan, env_id, env_name, chan_id, chan_name, timestamp, value;
    let data = {};

    let view = new DataView(buffer);
    let offset = 0;
    while (offset < buffer.byteLength) {
      env_id = view.getUint16(offset);
      offset += 2;
      chan_id = view.getUint16(offset);
      offset += 2;
      timestamp = Number(view.getBigUint64(offset));
      offset += 8;

      env_name = this.environment_ids[env_id];
      if (!(env_name in data)) {
        data[env_name] = {"points" : {}};
      }
      let points = data[env_name]["points"];

      chan_name = this.environment_channels[env_id][chan_id];
      if (!(chan_name in points)) {
        points[chan_name] = [];
      }
      points = points[chan_name];

      // parse value
      switch (this.environment_types[env_id][chan_id]) {
      case "uint8":
        value = view.getUint8(offset);
        offset += 1;
        break;
      case "uint16":
        value = view.getUint16(offset);
        offset += 2;
        break;
      case "uint32":
        value = view.getUint32(offset);
        offset += 4;
        break;
      case "uint64":
        value = Number(view.getBigUint64(offset));
        offset += 8;
        break;
      case "int8":
        value = view.getInt8(offset);
        offset += 1;
        break;
      case "int16":
        value = view.getInt16(offset);
        offset += 2;
        break;
      case "int32":
        value = view.getInt32(offset);
        offset += 4;
        break;
      case "int64":
        value = Number(view.getBigInt64(offset));
        offset += 8;
        break;
      case "float":
        value = view.getFloat32(offset);
        offset += 4;
        break;
      case "double":
        value = view.getFloat64(offset);
        offset += 8;
        break;
      case "bool":
        value = view.getUint8(offset);
        offset += 1;
        break;
      }

      points.push([ value, timestamp ]);
    }

    this.message_handlers["ui"](data);
  }
}
