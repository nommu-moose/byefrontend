document.addEventListener("DOMContentLoaded", () => {
  /* open popout */
  document.querySelectorAll("[data-popout-open]").forEach(btn => {
    const id = btn.getAttribute("data-popout-open");
    const dialog = document.getElementById(id);
    if (!dialog) return;

    btn.addEventListener("click", () => dialog.showModal());
  });

  /* close popout for all buttons with close attr */
  document.addEventListener("click", evt => {
    if (!evt.target.matches("[data-popout-close]")) return;
    const id = evt.target.getAttribute("data-popout-close");
    const dialog = document.getElementById(id);
    if (dialog) dialog.close();
  });

  /* click backdrop to close */
  document.querySelectorAll("dialog.bfe-popout").forEach(dialog => {
    dialog.addEventListener("click", e => {
      const rect = dialog.getBoundingClientRect();
      const inside =
        rect.top <= e.clientY && e.clientY <= rect.bottom &&
        rect.left <= e.clientX && e.clientX <= rect.right;
      if (!inside) dialog.close();
    });
  });
});
