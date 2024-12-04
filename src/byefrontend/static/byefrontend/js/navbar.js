document.addEventListener('DOMContentLoaded', function () {
  const navbarContainers = document.querySelectorAll('.navbar-container');

  navbarContainers.forEach(function (container) {
    const navConfig = JSON.parse(container.dataset.navConfig);
    renderNavbar(container, navConfig, 0);
  });

  function renderNavbar(container, items, level) {
    const nav = document.createElement('nav');
    nav.classList.add('navbar', 'level-' + level);

    const buttons = [];

    items.forEach((item) => {
      const button = document.createElement('button');
      button.textContent = item.text;
      button.classList.add('navbar-button', 'expanding'); // Start with 'expanding' class

      button.dataset.level = level;
      button.dataset.hasChildren = item.children && item.children.length > 0 ? 'true' : 'false';

      if (item.link) {
        button.addEventListener('click', function (event) {
          if (item.children && item.children.length > 0) {
            event.preventDefault();
          } else {
            window.location.href = item.link;
          }
        });
      }

      if (item.children && item.children.length > 0) {
        button.addEventListener('click', function () {
          const nextLevel = level + 1;
          if (button.classList.contains('active')) {
            removeSubNavbars(container, nextLevel);
            button.classList.remove('active');
          } else {
            removeSubNavbars(container, nextLevel);
            const siblingButtons = button.parentElement.querySelectorAll('.navbar-button.active');
            siblingButtons.forEach((btn) => btn.classList.remove('active'));

            renderNavbar(container, item.children, nextLevel);
            button.classList.add('active');
          }
        });
      }

      nav.appendChild(button);
      buttons.push({ button, item });
    });

    container.appendChild(nav);

    nav.offsetHeight; // Force reflow
    nav.classList.add('open');

    setTimeout(() => {
      const expandingButtons = nav.querySelectorAll('.navbar-button.expanding');
      expandingButtons.forEach((button) => {
        button.classList.remove('expanding');
      });
    }, 300); // Match with CSS transition duration

    buttons.forEach(({ button, item }) => {
      if (item.selected && item.children && item.children.length > 0) {
        button.classList.add('active');
        renderNavbar(container, item.children, level + 1);
      }
    });
  }

  function removeSubNavbars(container, level) {
    const subNavbars = container.querySelectorAll(`.navbar.level-${level}, .navbar.level-${level} ~ .navbar`);
    subNavbars.forEach((nav) => {
      const buttons = nav.querySelectorAll('.navbar-button');
      buttons.forEach((button) => {
        button.classList.add('collapsing');
      });

      nav.classList.remove('open');

      const transitionDuration = 300;

      setTimeout(() => {
        if (nav.parentElement === container) {
          container.removeChild(nav);
        }
      }, transitionDuration);
    });

    const activeButtons = container.querySelectorAll(`.navbar.level-${level - 1} .navbar-button.active`);
    activeButtons.forEach((button) => {
      button.classList.remove('active');
    });
  }
});
