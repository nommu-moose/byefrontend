// Bye-Frontend tag input field bootstrap

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.bfe-tag-input-wrapper').forEach(wrapper => init(wrapper));

  function init(wrapper) {
    const input = wrapper.querySelector('.bfe-tag-input-field');
    const hidden = wrapper.querySelector('input[type=hidden]');
    const dropdown = wrapper.querySelector('.bfe-tag-suggestions');
    const suggestions = JSON.parse(wrapper.dataset.suggestions || '[]');

    const updateHidden = () => {
      const tags = Array.from(wrapper.querySelectorAll('.bfe-tag'))
                       .map(span => span.dataset.tag);
      hidden.value = tags.join(',');
    };

    const addTag = (text) => {
      text = text.trim();
      if (!text) return;
      const exists = Array.from(wrapper.querySelectorAll('.bfe-tag'))
                          .some(s => s.dataset.tag === text);
      if (exists) { input.value = ''; hideSuggestions(); return; }
      const span = document.createElement('span');
      span.className = 'bfe-tag';
      span.dataset.tag = text;
      span.textContent = text;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'bfe-tag-remove';
      btn.textContent = '\u00d7';
      btn.addEventListener('click', () => { span.remove(); updateHidden(); });
      span.appendChild(btn);
      wrapper.insertBefore(span, input);
      input.value = '';
      hideSuggestions();
      updateHidden();
    };

    const showSuggestions = (val) => {
      dropdown.innerHTML = '';
      if (!val) { dropdown.style.display = 'none'; return; }
      const matches = suggestions.filter(s => s.toLowerCase().includes(val.toLowerCase()));
      if (matches.length === 0) { dropdown.style.display = 'none'; return; }
      matches.forEach(s => {
        const div = document.createElement('div');
        div.className = 'bfe-tag-suggestion';
        div.textContent = s;
        div.addEventListener('mousedown', (e) => { e.preventDefault(); addTag(s); });
        dropdown.appendChild(div);
      });
      dropdown.style.display = 'block';
    };

    const hideSuggestions = () => { dropdown.style.display = 'none'; };

    input.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ',') {
        e.preventDefault();
        addTag(input.value);
      }
    });

    input.addEventListener('input', () => {
      showSuggestions(input.value.trim());
    });

    document.addEventListener('click', (e) => {
      if (!wrapper.contains(e.target)) hideSuggestions();
    });

    // initialise from existing hidden value
    const initial = hidden.value.split(',').map(t => t.trim()).filter(t => t);
    initial.forEach(addTag);
  }
});
