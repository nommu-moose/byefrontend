/* Bye-Frontend – rich-text editor bootstrap */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".bfe-text-editor-wrapper").forEach(wrapper => {
    const toolbar = wrapper.querySelector(".bfe-text-editor-toolbar");
    const editor  = wrapper.querySelector(".bfe-text-editor-area");
    if (!toolbar || !editor) return;

    /* execCommand buttons */
    toolbar.addEventListener("click", e => {
      const btn = e.target.closest("button");
      if (!btn) return;

      const cmd = btn.dataset.cmd;
      if (cmd) { document.execCommand(cmd,false,null); editor.focus(); return; }

      switch(btn.dataset.special){
        case "checkbox": document.execCommand("insertHTML",false,'<input type="checkbox">&nbsp;'); break;
        case "table": insertTable(); break;
        case "deleteTable": deleteTable(); break;
        case "image": insertImage(); break;
      }
    });

    /* colour pickers */
    toolbar.querySelectorAll("input[type=color]").forEach(inp=>{
      inp.addEventListener("input", ()=>{
        if(inp.dataset.fore) document.execCommand("foreColor",false,inp.value);
        if(inp.dataset.back) document.execCommand("backColor",false,inp.value);
      });
    });

    /* block format select */
    const blockSel = toolbar.querySelector("select[data-block]");
    blockSel && blockSel.addEventListener("change", e=>{
      if(e.target.value) document.execCommand("formatBlock",false,e.target.value);
      editor.focus();
    });

    // helpers – scoped so each instance is isolated
    function insertTable(){
      const rows = parseInt(prompt("Rows?","3"),10) || 3;
      const cols = parseInt(prompt("Columns?","3"),10) || 3;
      let html = "<table><tbody>";
      for(let r=0;r<rows;r++){
        html += "<tr>";
        for(let c=0;c<cols;c++) html += "<td>Cell</td>";
        html += "</tr>";
      }
      html += "</tbody></table><br>";
      document.execCommand("insertHTML",false,html);
    }

    function deleteTable(){
      const sel = window.getSelection();
      if(!sel.rangeCount) return;
      let node = sel.getRangeAt(0).commonAncestorContainer;
      while(node && node.nodeName.toLowerCase() !== "table") node = node.parentNode;
      if(node) node.remove();
    }

    function insertImage(){
      const url = prompt("Image URL","https://via.placeholder.com/150");
      url && document.execCommand("insertImage",false,url);
    }
  });
});
