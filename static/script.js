document.addEventListener("DOMContentLoaded", function () {
  const loader = document.getElementById("resume-loader");
  const form = document.getElementById("resume-form");
  if (form && loader) {
    form.addEventListener("submit", function () {
      loader.style.display = "flex";
    });
  }
});

function resetResumeParser() {
  // Reloads the page to reset everything (form & results).
  window.location = window.location.pathname;
}

document.addEventListener("DOMContentLoaded", function () {
  // Loader logic as before...
  const loader = document.getElementById("resume-loader");
  const form = document.getElementById("resume-form");
  if (form && loader) {
    form.addEventListener("submit", function () {
      loader.style.display = "flex";
    });
  }

  // Show chosen filename
  const input = document.querySelector('input[type="file"][name="resume"]');
  const fileNameSpan = document.getElementById("chosen-file");
  if (input && fileNameSpan) {
    input.addEventListener("change", function () {
      if (this.files && this.files.length > 0) {
        fileNameSpan.textContent = this.files[0].name;
      } else {
        fileNameSpan.textContent = "";
      }
    });
  }
});


document.addEventListener("DOMContentLoaded", function () {
  // Loader logic
  const loader = document.getElementById("resume-loader");
  const form = document.getElementById("resume-form");
  if (form && loader) {
    form.addEventListener("submit", function () {
      loader.style.display = "flex";
    });
  }

  // Show chosen filename
  const input = document.querySelector('input[type="file"][name="resume"]');
  const fileNameSpan = document.getElementById("chosen-file");
  const parseBtn = document.getElementById("parse-btn");
  if (input && fileNameSpan) {
    input.addEventListener("change", function () {
      if (this.files && this.files.length > 0) {
        fileNameSpan.textContent = this.files[0].name;
        if(parseBtn) parseBtn.innerHTML = `<i class="fas fa-play"></i> Process`;
      } else {
        fileNameSpan.textContent = "";
        if(parseBtn) parseBtn.innerHTML = `<i class="fas fa-upload"></i> Upload & Parse`;
      }
    });
  }
});