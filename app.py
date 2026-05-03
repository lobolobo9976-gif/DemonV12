from flask import Flask, render_template_string, request, send_file, redirect, url_for, session, flash
import yt_dlp, os, json, random, string, threading, time
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'demon_v12_ultra_private_2026'

DB_FILE = "demon_data.json"
download_folder = "downloads"
os.makedirs(download_folder, exist_ok=True)

# --- BASE DE DATOS ---
def load_db():
    default = {
        "users": {"demon": {"password": "123", "is_admin": True, "vip_until": None}}, 
        "keys": {}, 
        "broadcast": "👹 DEMON V12 | SISTEMA ACTIVO", 
        "online_users": {}
    }
    if not os.path.exists(DB_FILE): save_db(default); return default
    try:
        with open(DB_FILE, 'r') as f: return json.load(f)
    except: return default

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

def get_user_status(username):
    db = load_db()
    u_data = db['users'].get(username)
    if not u_data: return "FREE", "text-zinc-500", False
    if u_data.get('is_admin'): return "DUEÑO ABSOLUTO", "text-yellow-500", True
    until = u_data.get('vip_until')
    if not until: return "USUARIO FREE", "text-zinc-400", False
    deadline = datetime.fromisoformat(until)
    if datetime.now() > deadline:
        u_data['vip_until'] = None
        save_db(db)
        return "USUARIO FREE", "text-zinc-400", False
    res = deadline - datetime.now()
    return f"VIP: {res.days}D {res.seconds // 3600}H", "text-pink-500 font-black", True

# --- MOTOR DE DESCARGA ---
def start_download(url, username, mode):
    prefix = f"{username}_"
    ydl_opts = {'outtmpl': f'{download_folder}/{prefix}%(title).40s.%(ext)s','quiet': True,'nocheckcertificate': True}
    if mode == "vip":
        ydl_opts.update({'external_downloader': 'aria2c','external_downloader_args': ['-x', '16', '-s', '16'],'format': 'bestvideo+bestaudio/best'})
    else:
        ydl_opts.update({'format': 'worst[ext=mp4]/best[ext=mp4]'})
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
    except: pass

# --- INTERFAZ MAESTRA ---
UI_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        body { background: #020202; color: #888; font-family: sans-serif; }
        .neon-box { border: 1px solid #ff007f; box-shadow: 0 0 15px #ff007f22; }
        .glass { background: rgba(15, 15, 20, 0.98); border: 1px solid #1a1a20; border-radius: 24px; }
        .tab-active { color: #ff007f !important; border-bottom: 2px solid #ff007f; }
        marquee { background: #ff007f15; color: #ff007f; font-size: 11px; font-weight: 900; padding: 8px; text-transform: uppercase; border-bottom: 1px solid #ff007f33; }
        .hidden { display: none; }
        .guide-text { font-size: 10px; line-height: 1.6; }
        .guide-text b { color: #fff; }
    </style>
</head>
<body>
    <marquee scrollamount="6"><i class="fas fa-skull mr-2"></i> {{msg}} <i class="fas fa-skull ml-2"></i></marquee>

    <div class="p-4 max-w-md mx-auto">
        <header class="glass neon-box p-6 mb-6 flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-black text-white italic tracking-tighter">DEMON<span class="text-pink-600">V12</span></h1>
                <p class="text-[9px] text-zinc-600 font-bold uppercase tracking-widest text-center">Online: {{online}}</p>
            </div>
            <div class="text-right">
                <p class="text-[10px] text-white font-bold opacity-80">{{user}}</p>
                <p class="text-[11px] {{s_color}} italic uppercase font-black tracking-tighter">{{s_text}}</p>
            </div>
        </header>

        <nav class="flex justify-around mb-6 text-[9px] font-black uppercase">
            <button onclick="show('dl')" id="btn-dl" class="tab-active py-2">Descarga</button>
            <button onclick="show('vt')" id="btn-vt" class="py-2">Bóveda</button>
            <button onclick="show('st')" id="btn-st" class="py-2">Ajustes</button>
            <button onclick="show('gui')" id="btn-gui" class="py-2 text-blue-400">Guía</button>
            {% if admin %}<button onclick="show('ad')" id="btn-ad" class="py-2 text-yellow-500">Root</button>{% endif %}
        </nav>

        <div id="dl" class="section glass p-6 space-y-4">
            <form action="/download" method="POST" class="space-y-4">
                <input type="url" name="url" placeholder="TikTok / Youtube / FB Link..." class="w-full bg-black border border-zinc-800 p-4 rounded-2xl text-xs text-white outline-none focus:border-pink-600" required>
                <div class="grid grid-cols-2 gap-3">
                    <button name="mode" value="free" class="bg-zinc-900 text-zinc-400 py-4 rounded-2xl text-[10px] font-black uppercase border border-zinc-800">Modo Free<br><span class="text-[7px] text-white opacity-50">Lento</span></button>
                    {% if is_vip %}
                    <button name="mode" value="vip" class="bg-pink-600 text-white py-4 rounded-2xl text-[10px] font-black uppercase shadow-lg shadow-pink-900/40">Modo VIP Turbo<br><span class="text-[7px] text-pink-200">16x Velocidad</span></button>
                    {% else %}
                    <button type="button" onclick="alert('⚠️ REQUIERES COMPRAR KEY VIP')" class="bg-zinc-800 text-zinc-600 py-4 rounded-2xl text-[10px] font-black uppercase cursor-not-allowed">VIP Bloqueado<br><span class="text-[7px]">Compra Key</span></button>
                    {% endif %}
                </div>
            </form>
        </div>

        <div id="gui" class="section hidden glass p-6 space-y-4">
            <h2 class="text-white font-black text-xs uppercase border-b border-zinc-800 pb-2 italic">Manual Demon V12</h2>
            <div class="guide-text space-y-3">
                <p>👤 <b>Dueño:</b> El administrador principal controla el sistema, genera las llaves VIP y gestiona los anuncios globales.</p>
                <p>⚡ <b>VIP Turbo:</b> Activa la descarga multihilo (16 canales). Descarga videos en máxima calidad a la mayor velocidad posible de tu red.</p>
                <p>📥 <b>Modo Free:</b> Acceso gratuito para todos. Velocidad limitada y calidad estándar.</p>
                <p>🔒 <b>Bóveda:</b> Almacén personal. Los archivos que descargues solo aparecerán en tu cuenta y nadie más podrá verlos.</p>
                <p>🔑 <b>Seguridad:</b> Puedes cambiar tu contraseña en "Ajustes" en cualquier momento para mantener tu cuenta segura.</p>
                <p class="text-blue-500 italic font-black text-center pt-4 uppercase tracking-tighter">Próximamente: Nuevas herramientas</p>
            </div>
        </div>

        <div id="vt" class="section hidden glass p-4 space-y-3 max-h-80 overflow-y-auto">
            {% for f in files %}
            <div class="flex justify-between items-center bg-black/40 p-4 rounded-2xl border border-zinc-900">
                <span class="text-[10px] truncate w-40 text-zinc-400 font-bold uppercase">{{f.split('_', 1)[1]}}</span>
                <a href="/get/{{f}}" class="bg-pink-600/10 text-pink-500 p-2 px-4 rounded-xl text-xs"><i class="fas fa-download"></i></a>
            </div>
            {% endfor %}
        </div>

        <div id="st" class="section hidden glass p-6 space-y-6">
            <form action="/change_pass" method="POST" class="space-y-2">
                <p class="text-[9px] text-white font-black uppercase">Cambiar Mi Clave</p>
                <input type="password" name="new_p" placeholder="Nueva Contraseña" class="w-full bg-black border border-zinc-800 p-4 rounded-2xl text-[10px] text-white outline-none">
                <button class="w-full bg-blue-600 text-white py-3 rounded-2xl text-[10px] font-black uppercase">Actualizar</button>
            </form>
            <form action="/activate_key" method="POST" class="space-y-2 pt-4 border-t border-zinc-900">
                <p class="text-[9px] text-pink-500 font-black uppercase">Activar Key VIP</p>
                <div class="flex gap-2">
                    <input type="text" name="key" placeholder="Pega tu Key..." class="flex-1 bg-black border border-zinc-800 p-4 rounded-2xl text-[10px] text-white">
                    <button class="bg-pink-600 px-6 rounded-2xl text-white font-black text-xs">OK</button>
                </div>
            </form>
            <a href="/logout" class="block text-center text-red-600 text-[9px] font-black py-4 uppercase">Cerrar Sesión</a>
        </div>

        {% if admin %}
        <div id="ad" class="section hidden glass p-6 space-y-4">
            <form action="/set_msg" method="POST" class="space-y-2">
                <input type="text" name="msg" placeholder="Mensaje Global..." class="w-full bg-black border border-zinc-800 p-3 rounded-xl text-xs text-white">
                <button class="w-full bg-yellow-600 text-black font-black py-3 rounded-xl text-[10px] uppercase">Cambiar Anuncio</button>
            </form>
            <form action="/gen_key" method="POST" class="space-y-2 pt-4 border-t border-zinc-800">
                <input type="number" name="days" placeholder="Días VIP" class="w-full bg-black border border-zinc-800 p-3 rounded-xl text-xs text-white">
                <button class="w-full bg-pink-600 text-white font-black py-3 rounded-xl text-[10px] uppercase">Crear Key</button>
            </form>
        </div>
        {% endif %}

        {% with m = get_flashed_messages() %}{% if m %}<p class="text-center text-pink-500 text-[11px] mt-6 font-black uppercase italic">{{m[0]}}</p>{% endif %}{% endwith %}
    </div>

    <script>
        function show(id){
            document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
            document.querySelectorAll('nav button').forEach(b => b.classList.remove('tab-active'));
            document.getElementById(id).classList.remove('hidden');
            document.getElementById('btn-'+id).classList.add('tab-active');
        }
    </script>
</body>
</html>
'''

# --- RUTAS ---
@app.route('/')
def index():
    if 'u' not in session: return redirect('/login')
    db = load_db(); u = session['u']
    db['online_users'][u] = time.time()
    db['online_users'] = {k: v for k, v in db['online_users'].items() if time.time() - v < 300}
    save_db(db)
    st_text, st_color, is_vip = get_user_status(u)
    files = [f for f in os.listdir(download_folder) if f.startswith(f"{u}_")]
    return render_template_string(UI_HTML, user=u, s_text=st_text, s_color=st_color, is_vip=is_vip, admin=db['users'][u]['is_admin'], files=files, msg=db['broadcast'], online=len(db['online_users']))

@app.route('/download', methods=['POST'])
def download():
    mode = request.form.get('mode'); u = session['u']
    _, _, is_vip = get_user_status(u)
    if mode == "vip" and not is_vip: flash("❌ REQUIERES VIP")
    else:
        threading.Thread(target=start_download, args=(request.form.get('url'), u, mode)).start()
        flash(f"🚀 DESCARGA {mode.upper()} INICIADA")
    return redirect('/')

@app.route('/change_pass', methods=['POST'])
def change_pass():
    db = load_db(); db['users'][session['u']]['password'] = request.form.get('new_p'); save_db(db); flash("🔑 CLAVE ACTUALIZADA"); return redirect('/')

@app.route('/set_msg', methods=['POST'])
def set_msg():
    db = load_db(); db['broadcast'] = request.form.get('msg', '').upper(); save_db(db); flash("📢 ANUNCIO ACTUALIZADO"); return redirect('/')

@app.route('/activate_key', methods=['POST'])
def activate_key():
    db = load_db(); k = request.form.get('key','').strip()
    if k in db['keys']:
        d = int(db['keys'][k])
        db['users'][session['u']]['vip_until'] = (datetime.now() + timedelta(days=d)).isoformat()
        del db['keys'][k]; save_db(db); flash("🔥 VIP ACTIVADO")
    else: flash("❌ KEY INVÁLIDA")
    return redirect('/')

@app.route('/gen_key', methods=['POST'])
def gen_key():
    db = load_db(); d = request.form.get('days', '1')
    k = "DEMON-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    db['keys'][k] = d; save_db(db); flash(f"KEY: {k}"); return redirect('/')

@app.route('/get/<f>')
def get_file(f):
    if f.startswith(session['u']): return send_file(os.path.join(download_folder, f), as_attachment=True)
    return "X", 403

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p, act = request.form.get('u'), request.form.get('p'), request.form.get('act')
        db = load_db()
        if act == 'lo' and u in db['users'] and db['users'][u]['password'] == p: session['u'] = u; return redirect('/')
        elif act == 're' and u not in db['users']: db['users'][u] = {"password":p,"is_admin":False,"vip_until":None}; save_db(db); flash("OK")
    return render_template_string('<body style="background:#000;color:white;display:flex;justify-content:center;align-items:center;height:100vh;"><form method="POST" style="text-align:center;border:1px solid #ff007f;padding:40px;border-radius:20px;background:#050505;"><h1>DEMON <span style="color:#ff007f">V12</span></h1><input name="u" placeholder="USUARIO" style="display:block;margin:10px auto;padding:10px;background:#111;color:white;border:1px solid #333;border-radius:10px;"><input name="p" type="password" placeholder="CLAVE" style="display:block;margin:10px auto;padding:10px;background:#111;color:white;border:1px solid #333;border-radius:10px;"><button name="act" value="lo" style="background:#ff007f;color:white;padding:10px;width:100%;border-radius:10px;border:none;font-weight:bold;">ENTRAR</button></form></body>')

@app.route('/logout')
def logout(): session.clear(); return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
