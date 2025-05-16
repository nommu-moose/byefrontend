/* Bye-Frontend – live syntax highlighter for CodeBoxWidget
   -------------------------------------------------------- */
(function () {
  /* ---------- helper utilities ---------- */
  function escapeHtml(str) {
    return str.replace(/[&<"']/g, m => ({
      "&": "&amp;", "<": "&lt;", '"': "&quot;", "'": "&#039;"
    }[m]));
  }

  function applySyntaxHighlighting(text) {
    const escaped = escapeHtml(text);
    const re = /(\\optional:)|(\$[A-Za-z0-9_]+)|(\{[^}]*\})|(\n)/g;

    let tokens = [], last = 0, m, optionalLine = false;
    while ((m = re.exec(escaped)) !== null) {
      if (m.index > last)
        tokens.push({text: escaped.slice(last, m.index),
                     cls: optionalLine ? "colour5" : "colour0"});

      const tok = m[0];
      if (m[1]) {                // \optional:
        tokens.push({text: tok, cls: "colour2"}); optionalLine = true;
      } else if (m[2]) {         // $VAR
        tokens.push({text: tok, cls: "colour1"});
      } else if (m[3]) {         // {var}
        tokens.push({text: "{", cls: "colour3"});
        tokens.push({text: tok.slice(1, -1), cls: "colour4"});
        tokens.push({text: "}", cls: "colour3"});
      } else if (m[4]) {         // newline
        tokens.push({text: "\n", cls: ""}); optionalLine = false;
      }
      last = re.lastIndex;
    }
    if (last < escaped.length)
      tokens.push({text: escaped.slice(last),
                   cls: optionalLine ? "colour5" : "colour0"});

    return tokens.map(t =>
      t.cls ? `<span class="${t.cls}">${t.text}</span>` : t.text
    ).join("").replace(/\n/g, "<br>");
  }

  function setCaretPosition(el, offset) {
    const rng = document.createRange(), sel = window.getSelection();
    let charIndex = 0, nodeStack = [el], node, found = false;

    while (!found && (node = nodeStack.pop())) {
      if (node.nodeType === 3) {
        const next = charIndex + node.length;
        if (offset >= charIndex && offset <= next) {
          rng.setStart(node, offset - charIndex); rng.collapse(true);
          found = true;
        }
        charIndex = next;
      } else if (node.nodeType === 1) {
        let i = node.childNodes.length;
        while (i--) nodeStack.push(node.childNodes[i]);
      }
    }
    sel.removeAllRanges(); sel.addRange(rng);
  }

  function initWidget(ctx) {
    const editor = document.getElementById(ctx.editorId);
    const hidden = document.getElementById(ctx.hiddenId);
    const pickers = ctx.pickerIds.map(id => document.getElementById(id));

    /* colour pickers → CSS custom properties */
    pickers.forEach((p, i) => {
      p.addEventListener("input", e =>
        document.documentElement
                .style.setProperty(`--colour${i}`, e.target.value));
    });

    /* live highlighting + caret preservation */
    function refresh() {
      const sel = window.getSelection();
      if (!sel.rangeCount) return;
      const rng = sel.getRangeAt(0);
      const pre = rng.cloneRange();
      pre.selectNodeContents(editor);
      pre.setEnd(rng.endContainer, rng.endOffset);
      const caret = pre.toString().length;

      editor.innerHTML = applySyntaxHighlighting(editor.innerText);
      setCaretPosition(editor, caret);
      hidden.value = editor.innerText;
    }

    editor.addEventListener("input", refresh);
  }

  /* bootstrap after DOM ready */
  document.addEventListener("DOMContentLoaded", () => {
    (window.BFE_CODE_BOX_INIT || []).forEach(initWidget);
  });
})();
