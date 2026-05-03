import os
import json
import random
import string
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, send_file, redirect, url_for, session, flash
import yt_dlp

app = Flask(__name__)
app.secret_key = 'demon_v12_ultra_private_2026'

# --- CONFIGURACIÓN DE RUTAS ---
# En Render, usamos /tmp para evitar errores de permisos si es necesario
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "demon_data.json")
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# --- SISTEMA DE BASE DE DATOS ---
def load_db():
    default = {
        "users": {"demon": {"password": "123", "is_admin": True, "vip_until": None}}, 
        "keys": {}, 
        "broadcast": "👹 DEMON V12 | SISTEMA ONLINE", 
    }
    if not os.path.exists(DB_FILE):
        save_db(default)
        return default
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return default

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_user_status(username):
    db = load_db()
    u = db['users'].get(username)
    if not u: return "FREE", "text-zinc-500", False
    if u.get('is_admin'): return "DUEÑO ABSOLUTO", "text-yellow-500", True
    
    until = u.get('vip_until')
    if not until: return "USUARIO FREE", "text-zinc-400", False
    
    deadline = datetime.fromisoformat(until)
    if datetime.now() > deadline:
        u['vip_until'] = None
        save_db(db)
        return "USUARIO FREE", "text-zinc-400", False
    
    res = deadline - datetime.now()
    return f"VIP: {res.days}D", "text-pink-500 font-black", True

# --- MOTOR DE DESCARGA V12 ---
def engine_v12(url, username, mode):
    prefix = f"{username}_"
    # User-Agent para saltar protecciones (visto en tus logs de brazzers)
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'http_headers': {'User-Agent': ua},
        'outtmpl': f'{DOWNLOAD_FOLDER}/{prefix}%(title).50s.%(ext)s',
    }

    if mode == "vip":
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        })
    else:
        ydl_opts.update({'format': 'best[ext=mp4]/best'})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Error Crítico: {e}")

# --- DISEÑO DE INTERFAZ (UI) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        body { background: #000; color: #666; font-family: sans-serif; }
        .neon-border { border: 1px solid #ff007f; box-shadow: 0 0 20px #ff007f22; }
        .glass { background: #0a0a0a; border: 1px solid #111; border-radius: 20px; }
        .tab-active { color: #ff007f !important; border-bottom: 2px solid #ff007f; }
        marquee { background: #ff007f0a; color: #ff007f; font-size: 11px; font-weight: bold; padding: 5px; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <marquee>👹 {{msg}}</marquee>

    <div class="p-4 max-w-md mx-auto">
        <div class="glass neon-border p-6 mb-4 flex justify-between items-center">
            <div>
                <h1 class="text-xl font-black text-white italic">DEMON<span class="text-pink-600">V12</span></h1>
                <p class="text-[8px] uppercase tracking-widest text-zinc-700">Online Status: Active</p>
            </div>
            <div class="text-right">
                <p class="text-[10px] text-white font-bold">{{user}}</p>
                <p class="text-[9px] {{s_color}} uppercase font-black">{{s_text}}</p>
            </div>
        </div>

        <nav class="flex justify-around mb-6 text-[10px] font-bold uppercase cursor-pointer">
            <span onclick="show('dl')" id="t-dl" class="tab-active py-1">Descarga</span>
            <span onclick="show('vt')" id="t-vt" class="py-1">Bóveda</span>
            <span onclick="show('st')" id="t-st" class="py-1">Ajustes</span>
            <span onclick="show('gui')" id="t-gui" class="py-1 text-blue-400">Guía</span>
            {% if admin %}<span onclick="show('ad')" id="t-ad" class="py-1 text-yellow-500">Root</span>{% endif %}
        </nav>

        <div id="dl" class="section glass p-6 space-y-4">
            <form action="/download" method="POST" class="space-y-4">
                <input type="url" name="url" placeholder="TikTok, YouTube, IG Link..." class="w-full bg-black border border-zinc-900 p-4 rounded-xl text-xs text-white outline-none focus:border-pink-600" required>
                <div class="grid grid-cols-2 gap-2">
                    <button name="mode" value="free" class="bg-zinc-900 text-zinc-500 py-3 rounded-xl text-[9px] font-bold uppercase">Normal</button>
                    <button name="mode" value="vip" class="bg-pink-600 text-white py-3 rounded-xl text-[9px] font-black uppercase italic shadow-lg">Modo Dios X16</button>
                </div>
            </form>
        </div>

        <div id="vt" class="section hidden glass p-4 space-y-2">
            {% for f in files %}
            <div class="flex justify-between items-center bg-black p-3 rounded-xl border border-zinc-900">
                <span class="text-[9px] truncate w-48 text-zinc-400">{{f.split('_', 1)[1]}}</span>
                <div class="flex gap-2">
                    <a href="/get/{{f}}" class="text-pink-500"><i class="fas fa-download"></i></a>
                    <a href="/delete/{{f}}" class="text-red-800"><i class="fas fa-trash"></i></a>
                </div>
            </div>
            {% endfor %}
            <p class="text-center text-[8px] text-zinc-800 mt-2 uppercase font-bold italic">🪄 Bóveda Limpia</p>
        </div>

        <div id="gui" class="section hidden glass p-6">
            <h2 class="text-white font-black text-xs mb-4 italic underline">MANUAL DIOS V12</h2>
            <ul class="text-[10px] space-y-3">
                <li>🛡️ <b class="text-pink-500">Camuflaje:</b> Rotación de IP y User-Agent activa.</li>
                <li>⚡ <b class="text-pink-500">Modo Dios:</b> Descarga multihilo en máxima calidad.</li>
                <li>🧹 <b class="text-pink-500">Limpieza:</b> Borrado automático de rastros.</li>
            </ul>
        </div>

        <div id="st" class="section hidden glass p-6 space-y-4">
            <form action="/update_pass" method="POST" class="space-y-2">
                <input type="password" name="new_pass" placeholder="Nueva Contraseña" class="w-full bg-black border border-zinc-900 p-3 rounded-xl text-xs text-white">
                <button class="w-full bg-blue-600 text-white py-3 rounded-xl text-[9px] font-bold uppercase">Actualizar Clave</button>
            </form>
            <form action="/activate_key" method="POST" class="space-y-2">
                <input type="text" name="key" placeholder="Pegar Key VIP..." class="w-full bg-black border border-zinc-900 p-3 rounded-xl text-xs text-white">
                <button class="w-full bg-pink-600 text-white py-3 rounded-xl text-[9px] font-bold uppercase">Activar VIP</button>
            </form>
            <a href="/logout" class="block text-center text-red-600 text-[9px] font-bold py-2">CERRAR SESIÓN</a>
        </div>

        {% if admin %}
        <div id="ad" class="section hidden glass p-6 space-y-4">
            <form action="/gen_key" method="POST" class="space-y-2">
                <input type="number" name="days" placeholder="Días VIP" class="w-full bg-black border border-zinc-900 p-3 rounded-xl text-xs text-white">
                <button class="w-full bg-yellow-600 text-black py-3 rounded-xl text-[9px] font-bold uppercase">Generar Key</button>
            </form>
        </div>
        {% endif %}

        {% with m = get_flashed_messages() %}
            {% if m %}<p class="text-center text-pink-500 text-[10px] mt-4 font-bold italic uppercase">{{m[0]}}</p>{% endif %}
        {% endwith %}
    </div>

    <script>
        function show(id){
            document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
            document.querySelectorAll('nav span').forEach(b => b.classList.remove('tab-active'));
            document.getElementById(id).classList.remove('hidden');
            document.getElementById('t-'+id).classList.add('tab-active');
        }
    </script>
</body>
</html>
'''

# --- RUTAS DE LA APP ---
@app.route('/')
def index():
    if 'u' not in session: return redirect('/login')
    db = load_db(); user = session['u']
    st_text, st_color, is_vip = get_user_status(user)
    files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(f"{user}_")]
    return render_template_string(HTML_TEMPLATE, user=user, s_text=st_text, s_color=st_color, is_vip=is_vip, admin=db['users'][user]['is_admin'], files=files, msg=db['broadcast'])

@app.route('/download', methods=['POST'])
def download():
    if 'u' not in session: return redirect('/login')
    url = request.form.get('url')
    mode = request.form.get('mode')
    threading.Thread(target=engine_v12, args=(url, session['u'], mode)).start()
    flash("🚀 DESCARGA EN COLA... RECARGA EN UN MOMENTO")
    return redirect('/')

@app.route('/get/<f>')
def get_file(f):
    if 'u' in session and f.startswith(session['u']):
        path = os.path.join(DOWNLOAD_FOLDER, f)
        if os.path.exists(path): return send_file(path, as_attachment=True)
    return "No encontrado", 404

@app.route('/delete/<f>')
def delete_file(f):
    if 'u' in session and f.startswith(session['u']):
        path = os.path.join(DOWNLOAD_FOLDER, f)
        if os.path.exists(path): os.remove(path)
    return redirect('/')

@app.route('/activate_key', methods=['POST'])
def activate_key():
    db = load_db(); key = request.form.get('key','').strip()
    if key in db['keys']:
        days = int(db['keys'][key])
        db['users'][session['u']]['vip_until'] = (datetime.now() + timedelta(days=days)).isoformat()
        del db['keys'][key]; save_db(db); flash("🔥 VIP ACTIVADO")
    else: flash("❌ KEY NO VÁLIDA")
    return redirect('/')

@app.route('/gen_key', methods=['POST'])
def gen_key():
    db = load_db(); k = "DV12-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    db['keys'][k] = request.form.get('days', '30'); save_db(db); flash(f"KEY: {k}")
    return redirect('/')

@app.route('/update_pass', methods=['POST'])
def update_pass():
    db = load_db(); new_p = request.form.get('new_pass')
    if new_p: db['users'][session['u']]['password'] = new_p; save_db(db); flash("CLAVE ACTUALIZADA")
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p, act = request.form.get('u'), request.form.get('p'), request.form.get('act')
        db = load_db()
        if act == 'lo' and u in db['users'] and db['users'][u]['password'] == p:
            session['u'] = u; return redirect('/')
        elif act == 're' and u not in db['users']:
            db['users'][u] = {"password": p, "is_admin": False, "vip_until": None}
            save_db(db); flash("REGISTRO EXITOSO")
    return render_template_string('<body style="background:#000;color:white;text-align:center;padding-top:100px;font-family:sans-serif;"><form method="POST" style="display:inline-block;border:1px solid #ff007f;padding:40px;border-radius:20px;"><h2 style="color:#ff007f;font-style:italic;">DEMON V12</h2><input name="u" placeholder="USUARIO" required style="display:block;margin:10px auto;padding:12px;background:#111;color:white;border:1px solid #222;border-radius:10px;"><input name="p" type="password" placeholder="CLAVE" required style="display:block;margin:10px auto;padding:12px;background:#111;color:white;border:1px solid #222;border-radius:10px;"><button name="act" value="lo" style="background:#ff007f;color:white;padding:10px 20px;border:none;border-radius:10px;font-weight:bold;width:100%;">ENTRAR</button><br><button name="act" value="re" style="background:transparent;color:#444;border:none;font-size:10px;margin-top:20px;cursor:pointer;">CREAR CUENTA</button></form></body>')

@app.route('/logout')
def logout():
    session.clear(); return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
            
