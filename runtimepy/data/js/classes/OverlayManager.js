const defaultPadTo = "                        ";

function padStringTo(data, padTo = defaultPadTo, front = true) {
  let delta = padTo.length - data.length;

  /* Should check if the string was too long. */
  if (delta > 0) {
    let padding = padTo.slice(0, delta);
    data = front ? padding + data : data + padding;
  }

  return data;
}

class OverlayManager {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = this.canvas.getContext("2d");
    this.ctx.globalAlpha = 0.7;

    /* Runtime state. */
    this.visible = true;
    this.bufferDepth = Math.min(512, this.canvas.width);
    this.minTimestamp = null;
    this.maxTimestamp = null;
    this.textLines = [];
    this.upperLeftEntries = [];
    this.bottomLeftEntries = [];
    this.maxLen = 0;

    /* Make this controllable at some point. */
    this.fontSize = 22;
    this.padding = this.fontSize / 4;
  }

  writeLn(data) {
    let padded = padStringTo(data);
    this.maxLen = Math.max(this.maxLen, padded.length);
    this.textLines.push(padded);
  }

  writeCornerLines(data, x, y) {
    for (const line of data) {
      this.ctx.fillStyle = line[0];
      this.ctx.fillText(line[1], x, y);
      y += this.fontSize;
    }
  }

  upperLeftText() {
    // this.ctx.fillRect(0, 0, size, size);
    this.writeCornerLines(this.upperLeftEntries, this.padding * 2,
                          this.padding + this.fontSize);
  }

  bottomLeftText() {
    // ctx.fillRect(0, canvas.height - size, size, size);
    this.writeCornerLines(this.bottomLeftEntries, this.padding * 2,
                          this.canvas.height -
                              (this.fontSize * this.bottomLeftEntries.length) +
                              this.padding);
  }

  update(time) {
    let canvas = this.canvas;
    let ctx = this.ctx;

    ctx.font = this.fontSize + "px monospace";

    /* Clear before drawing. */
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    this.upperLeftText();
    this.bottomLeftText();

    // let size = this.fontSize * 2;
    // ctx.fillRect(canvas.width - size, 0, size, size);
    // ctx.fillRect(canvas.width - size, canvas.height - size, size, size);
    // let time_str = String((time / 1000).toFixed(3));
    // this.writeLn(time_str + " s (frame time )");

    ctx.fillStyle = "#cce2e6";

    if (this.visible) {
      /* Height and width. */
      this.writeLn(String(canvas.width) + "       (width      )");
      this.writeLn(String(canvas.height) + "       (height     )");
      this.writeLn(String(this.bufferDepth) + "       (max samples)");

      /* Show amount of time captured. */
      if (this.minTimestamp != null && this.maxTimestamp) {
        let nanos = nanosString(this.maxTimestamp - this.minTimestamp);
        this.writeLn(nanos[0] + nanos[1] + "s (x-axis     )");
      }
    }
    this.writeLines(canvas.width - (this.maxLen * (this.fontSize * 0.55)));
  }

  writeLines(x) {
    let y = this.padding + this.fontSize;
    x -= this.padding;

    /* Draw lines. */
    for (const line of this.textLines) {
      if (line) {
        this.ctx.fillText(line, x, y);
      }
      y += this.fontSize;
    }

    /* Reset state. */
    this.textLines = [];
    this.maxLen = 0;
  }

  updateSize(width, height) {
    this.canvas.width = width;
    this.canvas.height = height;
  }

  handleMessage(data) {
    if ("type" in data && data["type"] == "click") {
      this.visible = !this.visible;
    } else {
      console.log("Overlay message not handled:");
      console.log(data);
    }
  }

  bumpCapacity(bumpUp) {
    /*
     * need persistent settings for scroll behavior? (configurable?)
     */
    let scale_factor = 1.05;
    let newCapacity = Math.max(16, bumpUp ? this.bufferDepth * scale_factor
                                          : this.bufferDepth / scale_factor);
    this.bufferDepth = Math.round(newCapacity);
    return this.bufferDepth;
  }
}
