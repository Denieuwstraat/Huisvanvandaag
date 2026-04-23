async function loadInclude(targetId, file) {
  const target = document.getElementById(targetId);
  if (!target) return;

  try {
    const response = await fetch(file);
    if (!response.ok) {
      throw new Error(`Kon ${file} niet laden: ${response.status}`);
    }

    target.innerHTML = await response.text();
  } catch (error) {
    console.error(error);
  }
}

function setActiveNavLink() {
  const currentPage = window.location.pathname.split("/").pop() || "index.html";
  const navLinks = document.querySelectorAll(".nav-links a");

  navLinks.forEach((link) => {
    const href = link.getAttribute("href");

    if (href === currentPage) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
}

function initNavToggle() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".nav-links");

  if (!toggle || !nav) return;

  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  await loadInclude("site-header", "header.html");
  await loadInclude("site-footer", "footer.html");

  setActiveNavLink();
  initNavToggle();

  document.dispatchEvent(new Event("includesLoaded"));
});