/*  src/byefrontend/static/byefrontend/js/navbar.js  */

document.addEventListener('DOMContentLoaded', () => {
  /* boostrap every <nav class="navbar-container"> on the page */
  const navbarContainers = document.querySelectorAll('.navbar-container');

  navbarContainers.forEach(container => {
    const navConfig = JSON.parse(container.dataset.navConfig);
    const selectedId = navConfig.selected_id || null;

    /* Build an array of names from the *root* down to the selected
       item, then drop the root entry so our level-counter (which
       starts at the children of the root) lines up.                 */
    const fullPath = selectedId ? findPathById(navConfig, selectedId) : [];
    const activePath = fullPath.length > 0 ? fullPath.slice(1) : [];

    /* Kick off the first level.  We pass the root config as a single
       element array because renderNavbar expects an *array* of items
       for each level.                                               */
    renderNavbar(container, [navConfig], 0, activePath, 0);
  });

  /* ──────────────────────────────────────────────────────────────
     Depth-first search that returns the chain of `name`s leading
     to `targetId`.  If not found, an empty array is returned.
     ────────────────────────────────────────────────────────────── */
  function findPathById(node, targetId, trail = []) {
    const currentName = node.name || null;
    const newTrail = currentName ? [...trail, currentName] : trail;

    if (currentName === targetId) {
      return newTrail;
    }
    if (node.children && node.children.length > 0) {
      for (const child of node.children) {
        const path = findPathById(child, targetId, newTrail);
        if (path.length > 0) {
          return path;
        }
      }
    }
    return [];
  }

  /* ──────────────────────────────────────────────────────────────
     Recursive renderer – unchanged except for the active-path logic
     ────────────────────────────────────────────────────────────── */
  function renderNavbar(container, items, level, activePath, activePathIndex) {
    const nav = document.createElement('nav');
    nav.classList.add('navbar', 'level-' + level);

    const buttons = [];

    /* Special handling for the root “title button” */
    if (level === 0 && items.length > 0 && items[0].title_button) {
      const rootItem = items[0];
      const button = document.createElement('button');
      button.textContent = rootItem.text || 'Default Title';
      button.classList.add('navbar-button', 'title-button');
      button.dataset.level = level;

      if (rootItem.link) {
        button.addEventListener('click', () => { window.location.href = rootItem.link; });
      }
      nav.appendChild(button);

      /* Render the actual first level using the root’s children  */
      items = rootItem.children && rootItem.children.length > 0 ? rootItem.children : [];
    }

    items.forEach(item => {
      const button = document.createElement('button');
      button.textContent = item.text || 'Default Title';
      button.classList.add('navbar-button', 'expanding');
      button.dataset.level = level;
      button.dataset.hasChildren = item.children && item.children.length > 0 ? 'true' : 'false';

      /* Navigate – hyperlinks vs. dropdown parents                      */
      if (item.link) {
        button.addEventListener('click', event => {
          if (item.children && item.children.length > 0) {
            event.preventDefault();          // keep dropdowns clickable
          } else {
            window.location.href = item.link;
          }
        });
      }

      if (item.children && item.children.length > 0) {
        button.addEventListener('click', () => {
          const nextLevel = level + 1;
          if (button.classList.contains('active')) {
            removeSubNavbars(container, nextLevel);
            button.classList.remove('active');
          } else {
            removeSubNavbars(container, nextLevel);
            /* Collapse any other active sibling first                  */
            button.parentElement
                  .querySelectorAll('.navbar-button.active')
                  .forEach(btn => btn.classList.remove('active'));

            renderNavbar(container, item.children, nextLevel,
                         activePath, activePathIndex + 1);
            button.classList.add('active');
          }
        });
      }

      nav.appendChild(button);
      buttons.push({ button, item });
    });

    container.appendChild(nav);

    /* Animate the dropdown opening                                     */
    nav.offsetHeight;                       // force reflow
    nav.classList.add('open');
    setTimeout(() => {
      nav.querySelectorAll('.navbar-button.expanding')
         .forEach(btn => btn.classList.remove('expanding'));
    }, 300);                                // match CSS transition

    /* ---------------------------------------------------------------- */
    /*  Open the path towards the item whose `name` == selected_id       */
    /* ---------------------------------------------------------------- */
    if (activePath && activePath[activePathIndex]) {
      buttons.forEach(({ button, item }) => {
        if (item.name === activePath[activePathIndex] ||
            item.text === activePath[activePathIndex]) {

          button.classList.add('active');

          if (item.children && item.children.length > 0) {
            renderNavbar(container, item.children, level + 1,
                         activePath, activePathIndex + 1);
          }
        }
      });
    }
  }

  /* ──────────────────────────────────────────────────────────────
     Utility: collapse (and eventually remove) all navbars *below*
     the given level so the menu never shows multiple open trails.
     ────────────────────────────────────────────────────────────── */
  function removeSubNavbars(container, level) {
    const subNavbars = container.querySelectorAll(
      `.navbar.level-${level}, .navbar.level-${level} ~ .navbar`
    );
    subNavbars.forEach(nav => {
      nav.querySelectorAll('.navbar-button').forEach(btn => btn.classList.add('collapsing'));
      nav.classList.remove('open');

      setTimeout(() => { if (nav.parentElement === container) container.removeChild(nav); },
                 300);   // same as the CSS transition
    });

    /* Also clear *.active* from the level above, so the current trail
       is the only one expanded.                                        */
    container.querySelectorAll(`.navbar.level-${level - 1} .navbar-button.active`)
             .forEach(btn => btn.classList.remove('active'));
  }
});
