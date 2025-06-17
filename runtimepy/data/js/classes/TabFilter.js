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
    // ctrl-l - go to channel table (open if needed) then close tabs

    if (globalKeyEvent(event) || ignoreFilterKeyEvent(event)) {
      return;
    }

    let curr = this.input.value;

    // new features: make '$' either auto-complete (one character per press)
    // to the first non-selected tab currently appearing in filter and presses
    // the nav button when it's the only button left
    //
    // tbd need another button for opening new tab, '@'?
    if (event.key == "Enter") {
      curr = "";
      event.preventDefault();
    } else {
      if (event.key == "Backspace") {
        curr = curr.slice(0, -1);
      } else {
        curr += event.key;
      }
    }

    if (!curr) {
      this.input.value = curr;
    }

    this.updateStyles(curr);

    this.input.focus();
  }
}
