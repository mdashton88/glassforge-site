// Glassforge Games — Development Access Gate
// Remove this file and all <script src="auth-gate.js"> lines when ready to launch
(function(){
  var KEY = 'glassforge_auth';
  var PASS = 'tributary';
  if(sessionStorage.getItem(KEY) === 'true') return;
  document.documentElement.style.visibility = 'hidden';
  window.addEventListener('DOMContentLoaded', function(){
    document.body.style.visibility = 'hidden';
    var d = document.createElement('div');
    d.innerHTML = '<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:#0a0a0a;z-index:999999;display:flex;align-items:center;justify-content:center;font-family:Georgia,serif;">' +
      '<div style="text-align:center;color:#c9a94e;max-width:380px;padding:20px;">' +
      '<h1 style="font-size:22px;font-variant:small-caps;letter-spacing:3px;margin-bottom:6px;">Glassforge Games</h1>' +
      '<p style="color:#666;font-size:13px;margin-bottom:28px;font-style:italic;">Development preview — not yet public</p>' +
      '<input id="gf-pass" type="password" placeholder="Access code" style="width:100%;padding:12px 16px;background:#141414;border:1px solid #333;color:#c9a94e;font-size:15px;font-family:Georgia,serif;text-align:center;outline:none;box-sizing:border-box;letter-spacing:1px;" />' +
      '<p id="gf-err" style="color:#833;font-size:12px;margin-top:10px;min-height:18px;"></p>' +
      '</div></div>';
    document.body.appendChild(d);
    var inp = document.getElementById('gf-pass');
    inp.focus();
    inp.addEventListener('keydown', function(e){
      if(e.key==='Enter'){
        if(inp.value===PASS){
          sessionStorage.setItem(KEY,'true');
          d.remove();
          document.documentElement.style.visibility='';
          document.body.style.visibility='';
        } else {
          document.getElementById('gf-err').textContent='Incorrect access code.';
          inp.value='';
        }
      }
    });
  });
})();
