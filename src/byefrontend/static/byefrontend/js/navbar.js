document.addEventListener('DOMContentLoaded', function () {
  const navbarContainers = document.querySelectorAll('.navbar-container');

  navbarContainers.forEach(function (container) {
    const navConfig = JSON.parse(container.dataset.navConfig);
    const activePath = deriveActivePath(navConfig);

    // Render the root navbar item
    renderNavbar(container, [navConfig], 0, activePath, 0);
  });

  function deriveActivePath(config, path = []) {
    if (config.selected && !config.title_button) {
      // Add this item's name or text to the path
      path.push(config.name || config.text);
    }

    // If the item has children, traverse them
    if (config.children && config.children.length > 0) {
      for (const child of config.children) {
        deriveActivePath(child, path);
      }
    }
    return path;
  }

  function renderNavbar(container, items, level, activePath, activePathIndex) {
    const nav = document.createElement('nav');
    nav.classList.add('navbar', 'level-' + level);

    const buttons = [];

    // At level 0, handle the title button separately
    if (level === 0 && items.length > 0 && items[0].title_button) {
      const rootItem = items[0];
      const button = document.createElement('button');
      button.textContent = rootItem.text || 'Default Title';
      button.classList.add('navbar-button', 'title-button');

      button.dataset.level = level;
      button.dataset.hasChildren = rootItem.children && rootItem.children.length > 0 ? 'true' : 'false';

      // Handle link if available
      if (rootItem.link) {
        button.addEventListener('click', function (event) {
          window.location.href = rootItem.link;
        });
      }

      nav.appendChild(button);

      // Now set items to rootItem.children
      if (rootItem.children && rootItem.children.length > 0) {
        items = rootItem.children;
      } else {
        items = []; // No more items
      }
    }

    // Now render the items
    items.forEach((item) => {
      const button = document.createElement('button');
      button.textContent = item.text || 'Default Title';

      button.classList.add('navbar-button', 'expanding');

      button.dataset.level = level;
      button.dataset.hasChildren = item.children && item.children.length > 0 ? 'true' : 'false';

      // Handle link if available
      if (item.link) {
        button.addEventListener('click', function (event) {
          if (item.children && item.children.length > 0) {
            event.preventDefault();
          } else {
            window.location.href = item.link;
          }
        });
      }

      // Handle click for buttons with children
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

            renderNavbar(container, item.children, nextLevel, [], 0);
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

    // Activate items based on activePathIndex
    if (activePath && activePath[activePathIndex]) {
      buttons.forEach(({ button, item }) => {
        if (item.name === activePath[activePathIndex] || item.text === activePath[activePathIndex]) {
          button.classList.add('active');
          if (item.children && item.children.length > 0) {
            renderNavbar(container, item.children, level + 1, activePath, activePathIndex + 1);
          }
        }
      });
    }
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
