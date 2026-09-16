from flask import Flask, request, jsonify, render_template_string

PAGE = """
<!doctype html>
<html><head><meta charset="utf-8"><title>ZERO BOOTSTRAP</title>
<style>
body{font-family:system-ui;max-width:1000px;margin:30px auto;padding:0 18px;background:#101010;color:#eee}
#chat{height:58vh;overflow:auto;background:#181818;border:1px solid #333;padding:16px}
.msg{white-space:pre-wrap;margin:10px 0}
input{width:76%;padding:12px;background:#222;color:#fff;border:1px solid #444}
button{padding:12px 18px}
</style></head>
<body>
<h1>ZERO BOOTSTRAP</h1>
<p>From-scratch local model · no hosted AI dependency · continuous training</p>
<div id="chat"></div><br>
<input id="text" placeholder="Talk to ZERO...">
<button onclick="send()">Send</button>
<button onclick="status()">State</button>
<script>
function add(w,t){
  let d=document.createElement('div'); d.className='msg';
  d.innerHTML='<b>'+w+'</b><br>'+String(t).replaceAll('<','&lt;');
  document.getElementById('chat').appendChild(d); d.scrollIntoView();
}
async function send(){
  let x=document.getElementById('text'), t=x.value.trim(); if(!t)return;
  add('You',t); x.value='';
  let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t})});
  let j=await r.json(); add('ZERO',j.reply||j.error);
}
async function status(){
  let r=await fetch('/api/status'); add('STATE', JSON.stringify(await r.json(),null,2));
}
</script></body></html>
"""

def make_server(engine):
    app = Flask(__name__)

    @app.get("/")
    def home():
        return render_template_string(PAGE)

    @app.post("/api/chat")
    def chat():
        data = request.get_json(force=True)
        text = str(data.get("text", "")).strip()
        if not text:
            return jsonify({"error": "empty message"}), 400
        return jsonify({"reply": engine.chat(text)})

    @app.get("/api/status")
    def status():
        return jsonify(engine.state())

    @app.post("/api/evolve")
    def evolve():
        return jsonify(engine.evolve_once())

    return app
