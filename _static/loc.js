function locMain() {
  // hide hidden fields from screen reader
  const matches = document.querySelectorAll(
    "input.sidebar-toggle, label.overlay",
  );
  matches.forEach((el) => {
    el.setAttribute("aria-hidden", "true");
  });

  // get header/footer contents
  const locFooter = document.querySelector("footer.loc-footer");
  const footerContent = locFooter ? locFooter.innerHTML : "";
  const locHeader = document.querySelector("header.loc-header");
  const headerContent = locHeader ? locHeader.innerHTML : "";

  // remove redundant footer
  const redundantFooter = document.querySelector("footer.bd-footer-content");
  if (redundantFooter) redundantFooter.remove();

  // change prev-next footer to a div
  const prevNextFooter = document.querySelector("footer.prev-next-footer");
  if (prevNextFooter) {
    const prevNextDiv = document.createElement("div");
    prevNextDiv.classList.add("prev-next-footer");
    prevNextDiv.innerHTML = prevNextFooter.innerHTML;
    prevNextFooter.replaceWith(prevNextDiv);
  }

  // put footer contents into main footer
  const mainFooter = document.querySelector("footer.bd-footer");
  if (mainFooter) {
    mainFooter.classList.add("loc-footer");
    mainFooter.innerHTML = footerContent;
  } else {
    const newFooter = document.createElement("footer");
    newFooter.classList.add("loc-footer");
    newFooter.innerHTML = footerContent;
    document.body.appendChild(newFooter);
  }

  // put header contents into header
  const newHeader = document.createElement("header");
  newHeader.classList.add("loc-header");
  newHeader.innerHTML = headerContent;
  document.body.prepend(newHeader);

  // update "Skip To" link
  const articleMain = document.querySelector('article[role="main"]');
  const skipLink = document.querySelector("a.skip-link");
  if (articleMain && skipLink) {
    articleMain.setAttribute("id", "article-main");
    const articleSections = articleMain.getElementsByTagName("section");
    if (articleSections.length > 0 && articleSections[0].hasAttribute("id")) {
      skipLink.setAttribute(
        "href",
        `#${articleSections[0].getAttribute("id")}`,
      );
    } else {
      skipLink.setAttribute("href", "#article-main");
    }
  }

  // remove redundant main
  const mains = document.querySelectorAll('article[role="main"]');
  if (mains) {
    mains.forEach((main) => {
      main.removeAttribute("role");
    });
  }

  // Make primary navigate accessible
  const labelMains = document.querySelectorAll('nav[aria-label="Main"]');
  if (labelMains) {
    labelMains.forEach((lmain) => {
      lmain.setAttribute("aria-label", "Primary");
      const navLists = lmain.querySelectorAll("ul");
      if (navLists) {
        const listCount = navLists.length;
        navLists.forEach(function (navList, i) {
          navList.setAttribute("role", "presentation");
          //   navList.setAttribute(
          //     "aria-label",
          //     `Navigation list ${i + 1} of ${listCount}`,
          //   );
        });
      }
    });
  }

  // inject alt text for generated images if captions are available
  // HACK: captions are <p> elements with <em> text inside of it. They should immediately follow the output cell that contains an image
  const images = document.querySelectorAll("#article-main .cell_output img");
  if (images) {
    images.forEach((image) => {
      const cell = image.closest(".cell");
      // check to see if the next sibling is a paragraph tag
      const { nextElementSibling } = cell;
      const { nodeName } = nextElementSibling;
      if (nodeName === "P") {
        // check to see if there is an emphasis inside of it
        const em = nextElementSibling.getElementsByTagName("em");
        if (em && em.length > 0) {
          const { innerText } = em[0];
          // set the alt text of the image with the emphasized text
          image.setAttribute("alt", innerText);
          // remove the source element
          nextElementSibling.remove();
        }
      }
    });
  }

  // Make sidebar toggle retain focus and notify user of collapse/expanse
  const primaryToggle = document.getElementById("pst-primary-sidebar-checkbox");
  primaryToggle.checked = false;

  const sidebarToggle = document.querySelector("button.sidebar-toggle");
  let toggleHadFocus = false;

  if (sidebarToggle) {
    sidebarToggle.setAttribute("aria-controls", "sidebar");
    sidebarToggle.setAttribute("aria-expanded", true);
    // Check if the toggle was in focus before keystroke
    sidebarToggle.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        toggleHadFocus = document.activeElement === sidebarToggle;
      }
    });
    sidebarToggle.addEventListener("click", () => {
      console.log(sidebarToggle.checked);
      const expanded = sidebarToggle.getAttribute("aria-expanded") === "true";
      sidebarToggle.setAttribute("aria-expanded", String(!expanded));
      // The baked-in pydata-sphinx-theme.js attempts to put the focus on the first menu
      // item when the menu is un-collapsed, but there's a bug where this fires instead
      // when the menu is collapsed. It fires after 100ms. Here, we're stealing the
      // focus back afterwards. Currently doesn't work if NVDA is on.
      if (toggleHadFocus) {
        setTimeout(() => {
          sidebarToggle.focus();
        }, 140); // slightly longer than 100ms
      }

      toggleHadFocus = false;
    });
  }

  // Make tables accessible
  const tables = document.querySelectorAll("table");
  if (tables) {
    tables.forEach((table) => {
      const ths = table.querySelectorAll("thead th");
      ths.forEach((th) => {
        // Set heading scope
        th.setAttribute("scope", "col");
      });
    });
  }

  // Make Jupyter notebook Python DataFrame tables accessible
  const dataTables = document.querySelectorAll("table.dataframe");
  if (dataTables) {
    dataTables.forEach((table) => {
      const ths = table.querySelectorAll("thead th");
      ths.forEach((th) => {
        const text = th.innerText.trim();
        // Put content in empty table heading
        if (text.length === 0) {
          th.innerText = "#";
        }
        // Set heading scope
        th.setAttribute("scope", "col");
      });

      // Attempt to add title to table based on the first element in the section (should be a heading)
      const section = table.closest("section");
      const sectionId = section.getAttribute("id");
      if (sectionId && sectionId !== "") {
        const headingId = `${sectionId}-heading`;
        const sectionHeading = section.querySelector("h1, h2, h3, h4, h5, h6");
        sectionHeading.setAttribute("id", headingId);
        table.setAttribute("aria-describedby", headingId);
      }
    });
  }

  // Make Plotly visualization controls announce changes
  const plotly_buttons = document.querySelectorAll("button.modebar-btn");
  let label = "";
  if (plotly_buttons) {
    plotly_buttons.forEach((plotly_button) => {
      plotly_button.addEventListener("click", () => {
        label = plotly_button.getAttribute("aria-label");
        sr_announce("Completed: " + label);
      });
    });
  }

  // Don't move the keyboard focus when Jupyter code cells are copied
  let lastFocusedElement = null;
  document.addEventListener(
    "mousedown",
    () => {
      lastFocusedElement = document.activeElement;
    },
    true,
  );
  document.addEventListener(
    "keydown",
    (e) => {
      if (e.key === " " || e.key === "Enter") {
        lastFocusedElement = document.activeElement;
      }
    },
    true,
  );
  const copybtns = document.querySelectorAll(".copybtn");
  copybtns.forEach((copybtn) => {
    copybtn.addEventListener("click", () => {
      setTimeout(() => {
        if (lastFocusedElement && document.contains(lastFocusedElement)) {
          lastFocusedElement.focus();
        }
      }, 150);
    });
  });
}

function sr_announce(message) {
  const announcer = document.getElementById("sr-announcer");
  announcer.textContent = "";
  setTimeout(() => {
    announcer.textContent = message;
  }, 100);
}

function alter_code_button() {
  const editButton = document.querySelector(".btn-source-edit-button");
  if (editButton) {
    const currentHref = editButton.getAttribute("href");
    if (currentHref && currentHref.includes("/edit/")) {
      const newHref = currentHref.replace("/edit/", "/blob/");
      editButton.setAttribute("href", newHref);
    }
  }
}

function alter_repo_href() {
  // Fix urls like "https://github.com/LibraryOfCongress//btp-dataset"
  const repoButton = document.querySelector(".btn-source-repository-button");
  if (repoButton) {
    const currentHref = repoButton.getAttribute("href");
    if (currentHref && currentHref.includes("//")) {
      const newHref = currentHref.replace(/(https?:\/\/.*)\/\/(.*)/, "$1/$2");
      repoButton.setAttribute("href", newHref);
    }
  }
}

// // Don't allow Sphinx to steal the focus from the toggle button
// function prevent_theft() {
//   const toggle = document.querySelector(".primary-toggle");
//   console.log("****** TOGGLE CONTROLER STARTED ********");
//   console.log("toggle found: " + toggle);
//   if (!toggle) return;

//   // Force correct initial state
//   console.log("before forcing, toggle checked: " + toggle.checked);
//   toggle.checked = true;
//   console.log("after forcing, toggle checked: " + toggle.checked);

//   // Prevent future resets
//   Object.defineProperty(toggle, "checked", {
//     configurable: true,
//     get() {
//       console.log("checked GET theft started! !!!!!!");
//       return this._checked !== false;
//     },
//     set(value) {
//       console.log("checked SET theft started! !!!!!!");
//       this._checked = true;
//     },
//   });

//   toggle._checked = true;
// }

document.addEventListener("DOMContentLoaded", (event) => {
  console.log("DOM loaded");
  locMain();
  alter_code_button();
  alter_repo_href();
  //   prevent_theft();
});

// // === Catch all focus attempts ===

// // 1. Patch HTMLElement.prototype.focus
// const originalElementFocus = HTMLElement.prototype.focus;
// HTMLElement.prototype.focus = function (...args) {
//   console.trace("Element.focus() called on:", this);
//   return originalElementFocus.apply(this, args);
// };

// // 2. Patch window.focus
// const originalWindowFocus = window.focus;
// window.focus = function (...args) {
//   console.trace("window.focus() called");
//   return originalWindowFocus.apply(this, args);
// };

// // 3. Listen for all focus events (capture phase)
// document.addEventListener(
//   "focus",
//   (e) => {
//     console.trace("Focus event on:", e.target);
//   },
//   true,
// );
