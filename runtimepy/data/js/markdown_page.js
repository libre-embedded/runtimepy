/* Dark is hard-coded initial state (in HTML). */
let lightMode = false;

function lightDarkClick(event) {
  lightMode = !lightMode;

  document.getElementById("runtimepy")
      .setAttribute("data-bs-theme", lightMode ? "light" : "dark");

  window.location.hash = lightMode ? "#light-mode" : "";
}

window.onload = () => {
  let lightDarkButton = document.getElementById("theme-button");
  if (lightDarkButton) {
    lightDarkButton.addEventListener("click", lightDarkClick);
  }

  if (window.location.hash) {
    let parts = window.location.hash.slice(1).split(",");

    if (parts.includes("light-mode")) {
      lightDarkButton.click();
    }
  }

  bootstrap_init();

  /* Hide button column for print mode. */
  const params = new URLSearchParams(window.location.search);
  if (params.get("print") == "true") {
    const elem = document.getElementById("button-column");
    if (elem) {
      elem.classList.remove("d-flex");
      elem.style.display = "none";
    }
  }
};
