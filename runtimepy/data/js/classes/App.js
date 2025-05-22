class App {
  constructor(config, worker) {
    this.config = config;
    this.worker = worker;

    this.config["worker"] = worker_config(this.config);
  }

  switchTab(newTabName) {
    if (newTabName in tabs && shown_tab != newTabName) {
      tabs[newTabName].tabButton.click();
    }
  }

  async main() {
    /*
     * Run application initialization when the worker thread responds with an
     * expected value.
     */
    worker.addEventListener("message", async (event) => {
      if (event.data == 0) {
        /* Manage settings modal. */
        let _modal = document.getElementById("runtimepy-settings");
        if (_modal) {
          modalManager = new PlotModalManager(_modal);
        }

        /* Run tab initialization. */
        for await (const init of inits) {
          await init();
        }

        /* Prepare worker message handler. */
        this.worker.onmessage = async (event) => {
          /* Check for reload recommendation. */
          if ("reload" in event.data && event.data["reload"]) {
            console.log("Worker thread recommended page reload.");
            window.location.reload();
          }

          for (const key in event.data) {
            /* Handle forwarding messages to individual tabs. */
            if (key in tabs) {
              tabs[key].onmessage(event.data[key]);
            }
          }
        };

        hash.initButtons();

        /* Switch tabs if necessary. */
        if (hash.tab) {
          this.switchTab(hash.tab);
        }

        hash.updateTabFilter(hash.tabFilter);

        /* Handle settings controls. */
        loadSettings();

        /* Handle individual settings. */
        this.handleInitialMinTxPeriod();

        /* Handle channel-table expand button. */
        let _button = document.getElementById("open-channels-button");
        if (_button) {
          _button.onclick = () => {
            /* Ensure channel table is visible. */
            if (!hash.channelsShown && hash.channelsButton) {
              hash.channelsButton.click();
            }

            /* Ensure channel table is at maximum width. */
            if (shown_tab in tabs) {
              let elem = tabs[shown_tab].query(".channel-column");
              if (elem) {
                elem.style.width = window.innerWidth + "px";
                tabs[shown_tab].correctVerticalBarPosition();
                tabs[shown_tab].focus();
              }
            }
          };
        }
        _button = document.getElementById("dedent-channels-button");
        if (_button) {
          _button.onclick = () => {
            if (!hash.channelsShown) {
              return;
            }

            /* Reduce channel table width. */
            if (shown_tab in tabs) {
              let elem = tabs[shown_tab].query(".channel-column");
              if (elem) {
                let newWidth = elem.getBoundingClientRect().width - 50;
                if (newWidth > 0) {
                  elem.style.width = newWidth + "px";
                  tabs[shown_tab].focus();
                } else {
                  hash.channelsButton.click();
                }
              }
            }
          };
        }

        /* Set initial focus. */
        if (hash.tabsShown && tabFilter) {
          tabFilter.input.focus();
        } else if (hash.channelsShown && shown_tab in tabs) {
          tabs[shown_tab].focus();
        }

        startMainLoop();
      }
    }, {once : true});

    /* Start worker. */
    this.worker.postMessage(this.config);

    bootstrap_init();
  }

  handleInitialMinTxPeriod() {
    if ("min-tx-period-ms" in settings) {
      /* Set up event handle. */
      setupCursorContext(settings["min-tx-period-ms"], (elem, down, move,
                                                        up) => {
        setupCursorMove(
            elem, down, move, up,
            (event) => { this.updateMinTxPeriod(Number(event.target.value)); });
      });

      /* Set slider to correct value. */
      settings["min-tx-period-ms"].value = hash.minTxPeriod;
      settings["min-tx-period-ms"].title = hash.minTxPeriod;
    }

    this.updateMinTxPeriod();
  }

  updateMinTxPeriod(value) {
    if (value || value === 0) {
      hash.setMinTxPeriod(value);
      settings["min-tx-period-ms"].title = value;
    }
    this.worker.postMessage(
        {"event" : {"worker" : {"min-tx-period-ms" : hash.minTxPeriod}}});
  }
}

function startMainLoop() {
  let splash = document.getElementById("runtimepy-splash");

  let prevTime = 0;

  /* Main loop. */
  function render(time) {
    let deltaT = time - prevTime;

    /* Fade splash screen out if necessary. */
    if (splash) {
      let curr = window.getComputedStyle(splash).getPropertyValue("opacity");
      if (curr > 0) {
        splash.style.opacity = curr - Math.min(0.05, deltaT / 1000);
      } else {
        splash.style.display = "none";
        splash = undefined;
      }
    }

    /* Poll the currently shown tab. */
    if (shown_tab in tabs) {
      tabs[shown_tab].poll(time);
    }

    prevTime = time;
    requestAnimationFrame(render);
  }
  requestAnimationFrame(render);
}
