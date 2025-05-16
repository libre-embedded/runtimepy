class TabFilter {
  constructor(container) {
    this.container = container;

    /* Find input element. */
    this.input = this.container.querySelector("input");
    this.input.addEventListener("keydown", this.keydown.bind(this));

    /* Create a mapping of tab name to tab element. */
    this.buttons = {};
    for (let button of this.container.querySelectorAll("button")) {
      let name = button.id.split("-")[1];
      this.buttons[name] = button;
    }
  }

  updateStyles(pattern) {
    pattern = pattern.trim();
    hash.setTabFilter(pattern);

    if (!pattern) {
      pattern = ".*";
    }

    let parts = pattern.split(/(\s+)/)
                    .filter((x) => x.trim().length > 0)
                    .map((x) => new RegExp(x));

    for (let [name, elem] of Object.entries(this.buttons)) {
      let found = elem.classList.contains("active");

      if (!found) {
        for (const re of parts) {
          if (re.test(name)) {
            found = true;
            break;
          }
        }
      }

      if (found) {
        for (const child of elem.parentElement.children) {
          child.style.display = "block";
        }
      } else {
        for (const child of elem.parentElement.children) {
          child.style.display = "none";
        }
      }
    }
  }

  keydown(event) {
    if (isModifierKeyEvent(event) || event.key == "Tab") {
      return;
    }

    let curr = this.input.value;

    if (event.key == "Enter") {
      curr = "";
      this.input.value = curr;
    } else {
      if (event.key == "Backspace") {
        curr = curr.slice(0, -1);
      } else {
        curr += event.key;
      }
    }

    this.updateStyles(curr);
  }
}
