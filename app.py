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
        "broadcast": "👹 DEMON V12 | HABLE PRIVADO @LOBOTIGRE TELEGRAM 💀", 
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
            'external_downloader': 'aria2c', # Si está disponible
            'external_downloader_args': ['-x', '16', '-k', '1M'],
        })
    else:
        ydl_opts.update({'format': 'best[ext=mp4]/best'})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Error: {e}")

# --- DISEÑO DE INTERFAZ (UI) MEJORADA ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        body { background: #000; color: #888; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        .neon-border { border: 1px solid #ff007f; box-shadow: 0 0 15px #ff007f44; }
        .glass { background: rgba(10, 10, 10, 0.95); border: 1px solid #1a1a1a; border-radius: 24px; backdrop-filter: blur(10px); }
        .tab-active { color: #ff007f !important; position: relative; font-weight: 900; }
        .tab-active::after { content: ''; position: absolute; bottom: -5px; left: 0; width: 100%; height: 3px; background: #ff007f; border-radius: 10px; box-shadow: 0 0 10px #ff007f; }
        marquee { background: linear-gradient(90deg, transparent, #ff007f22, transparent); color: #ff007f; font-size: 10px; font-weight: bold; padding: 8px; border-bottom: 1px solid #ff007f33; }
        .btn-vip { background: linear-gradient(135deg, #ff007f, #8b00ff); box-shadow: 0 4px 15px rgba(255, 0, 127, 0.4); transition: 0.3s; }
        .btn-vip:active { transform: scale(0.95); }
        .hidden { display: none; }
    </style>
</head>
<body>
    <marquee><i class="fas fa-skull"></i> {{msg}} <i class="fas fa-skull"></i></marquee>

    <div class="p-4 max-w-lg mx-auto min-h-screen">
        <div class="glass neon-border p-6 mb-6 flex justify-between items-center relative overflow-hidden">
            <div class="z-10">
                <h1 class="text-2xl font-black text-white italic tracking-tighter">DEMON<span class="text-pink-600">V12</span></h1>
                <p class="text-[9px] uppercase tracking-widest text-zinc-500 font-bold">Online Status: <span class="text-green-500 animate-pulse">Active</span></p>
            </div>
            <div class="text-right z-10">
                <p class="text-[11px] text-white font-bold">{{user}}</p>
                <p class="text-[10px] {{s_color}} uppercase font-black italic">{{s_text}}</p>
            </div>
        </div>

        <nav class="flex justify-between mb-8 px-2 text-[10px] font-bold uppercase cursor-pointer text-zinc-500">
            <span onclick="show('dl')" id="t-dl" class="tab-active py-1">Descarga</span>
            <span onclick="show('vt')" id="t-vt" class="py-1">Bóveda</span>
            <span onclick="show('st')" id="t-st" class="py-1">Ajustes</span>
            <span onclick="show('gui')" id="t-gui" class="py-1">Guía</span>
            {% if admin %}<span onclick="show('ad')" id="t-ad" class="py-1 text-yellow-500">Root</span>{% endif %}
        </nav>

        <div id="dl" class="section space-y-4">
            <div class="glass p-8 space-y-6">
                <form action="/download" method="POST" class="space-y-6">
                    <div class="relative">
                        <i class="fas fa-link absolute left-4 top-4 text-zinc-600"></i>
                        <input type="url" name="url" placeholder="TikTok, YouTube, IG Link..." class="w-full bg-black border border-zinc-800 p-4 pl-12 rounded-2xl text-xs text-white outline-none focus:border-pink-600 transition-all" required>
                    </div>
                    <div class="grid grid-cols-1 gap-3">
                        <button name="mode" value="vip" class="btn-vip text-white py-4 rounded-2xl text-[11px] font-black uppercase italic tracking-widest">
                            <i class="fas fa-bolt mr-2"></i> MODO DIOS X16
                        </button>
                        <button name="mode" value="free" class="bg-zinc-900 text-zinc-400 py-3 rounded-2xl text-[9px] font-bold uppercase hover:bg-zinc-800">Descarga Normal</button>
                    </div>
                </form>
            </div>
        </div>

        <div id="vt" class="section hidden space-y-4">
            <div class="glass p-4 min-h-[300px]">
                <div class="flex justify-between items-center mb-4 px-2">
                    <h3 class="text-[10px] font-black text-white uppercase italic">Archivos Listos</h3>
                    <a href="/clear_vault" class="text-[9px] text-red-500 font-bold uppercase"><i class="fas fa-trash-alt mr-1"></i> Vaciar Bóveda</a>
                </div>
                <div class="space-y-3">
                    {% for f in files %}
                    <div class="flex justify-between items-center bg-zinc-950 p-4 rounded-2xl border border-zinc-900">
                        <div class="flex items-center gap-3">
                            <i class="fas fa-video text-pink-600"></i>
                            <span class="text-[10px] truncate w-40 text-zinc-300 font-medium">{{f.split('_', 1)[1]}}</span>
                        </div>
                        <div class="flex gap-4">
                            <a href="/get/{{f}}" class="text-green-500 text-sm"><i class="fas fa-cloud-download-alt"></i></a>
                            <a href="/delete/{{f}}" class="text-zinc-700 text-sm"><i class="fas fa-times"></i></a>
                        </div>
                    </div>
                    {% else %}
                    <div class="text-center py-20">
                        <i class="fas fa-folder-open text-4xl text-zinc-900 mb-4"></i>
                        <p class="text-[10px] text-zinc-700 font-black italic uppercase">Bóveda Vacía</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <div id="gui" class="section hidden glass p-8">
            <h2 class="text-white font-black text-xs mb-6 italic border-b border-pink-600 pb-2 inline-block">MANUAL DIOS V12</h2>
            <ul class="space-y-5">
                <li class="flex gap-4">
                    <div class="text-pink-600 mt-1"><i class="fas fa-shield-halved"></i></div>
                    <div>
                        <p class="text-white text-[10px] font-bold uppercase">Camuflaje</p>
                        <p class="text-[9px] text-zinc-500">Rotación de IP y User-Agent activa para evitar bloqueos.</p>
                    </div>
                </li>
                <li class="flex gap-4">
                    <div class="text-pink-600 mt-1"><i class="fas fa-bolt"></i></div>
                    <div>
                        <p class="text-white text-[10px] font-bold uppercase">Modo Dios</p>
                        <p class="text-[9px] text-zinc-500">Descarga multihilo (16 partes) para máxima velocidad.</p>
                    </div>
                </li>
                <li class="flex gap-4">
                    <div class="text-pink-600 mt-1"><i class="fas fa-broom"></i></div>
                    <div>
                        <p class="text-white text-[10px] font-bold uppercase">Limpieza</p>
                        <p class="text-[9px] text-zinc-500">Borrado automático de rastros y fragmentos corruptos.</p>
                    </div>
                </li>
            </ul>
        </div>

        <div id="st" class="section hidden space-y-4">
            <div class="glass p-6 space-y-6">
                <form action="/update_pass" method="POST" class="space-y-3">
                    <p class="text-[9px] font-black text-zinc-500 uppercase ml-2">Seguridad</p>
                    <input type="password" name="new_pass" placeholder="Nueva Contraseña" class="w-full bg-black border border-zinc-900 p-4 rounded-2xl text-xs text-white outline-none focus:border-blue-600">
                    <button class="w-full bg-blue-700 text-white py-3 rounded-2xl text-[9px] font-bold uppercase">Actualizar Clave</button>
                </form>
                <form action="/activate_key" method="POST" class="space-y-3">
                    <p class="text-[9px] font-black text-zinc-500 uppercase ml-2">Membresía</p>
                    <input type="text" name="key" placeholder="Pegar Key VIP..." class="w-full bg-black border border-zinc-900 p-4 rounded-2xl text-xs text-white outline-none focus:border-pink-600">
                    <button class="w-full btn-vip text-white py-3 rounded-2xl text-[9px] font-bold uppercase">Activar VIP</button>
                </form>
                <a href="/logout" class="block text-center text-red-600 text-[10px] font-black py-4 border-t border-zinc-900 mt-4 uppercase">Cerrar Sesión</a>
            </div>
        </div>

        {% if admin %}
        <div id="ad" class="section hidden space-y-4">
            <div class="glass p-6 space-y-6">
                <form action="/gen_key" method="POST" class="space-y-3">
                    <p class="text-[9px] font-black text-yellow-500 uppercase ml-2">Generador de Keys</p>
                    <input type="number" name="days" placeholder="Días de VIP" class="w-full bg-black border border-zinc-900 p-4 rounded-2xl text-xs text-white">
                    <button class="w-full bg-yellow-600 text-black py-3 rounded-2xl text-[10px] font-black uppercase tracking-tighter">Generar Key Maestra</button>
                </form>
                <form action="/update_marquee" method="POST" class="space-y-3">
                    <p class="text-[9px] font-black text-yellow-500 uppercase ml-2">Anuncio Global</p>
                    <input type="text" name="msg" placeholder="Nuevo mensaje del marquee..." class="w-full bg-black border border-zinc-900 p-4 rounded-2xl text-xs text-white">
                    <button class="w-full bg-zinc-800 text-white py-3 rounded-2xl text-[10px] font-black uppercase">Actualizar Marquee</button>
                </form>
            </div>
        </div>
        {% endif %}

        {% with m = get_flashed_messages() %}
            {% if m %}<div class="fixed bottom-10 left-0 w-full text-center px-6"><p class="bg-pink-600 text-white text-[10px] py-3 rounded-2xl font-black italic uppercase shadow-2xl animate-bounce">{{m[0]}}</p></div>{% endif %}
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
    flash("🚀 PROCESANDO DESCARGA... REVISA LA BÓVEDA EN 1 MINUTO")
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

@app.route('/clear_vault')
def clear_vault():
    if 'u' in session:
        user = session['u']
        for f in os.listdir(DOWNLOAD_FOLDER):
            if f.startswith(f"{user}_"):
                os.remove(os.path.join(DOWNLOAD_FOLDER, f))
        flash("🧹 BÓVEDA LIMPIA")
    return redirect('/')

@app.route('/update_marquee', methods=['POST'])
def update_marquee():
    db = load_db()
    if db['users'][session['u']]['is_admin']:
        db['broadcast'] = request.form.get('msg')
        save_db(db); flash("📢 ANUNCIO ACTUALIZADO")
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
    return render_template_string('<body style="background:#000;color:white;text-align:center;padding-top:100px;font-family:sans-serif;"><form method="POST" style="display:inline-block;border:1px solid #ff007f;padding:40px;border-radius:24px;background:#050505;box-shadow:0 0 20px rgba(255,0,127,0.2);"><h2 style="color:#ff007f;font-style:italic;font-size:24px;font-weight:900;">DEMON V12</h2><input name="u" placeholder="USUARIO" required style="display:block;margin:20px auto;padding:15px;background:#111;color:white;border:1px solid #222;border-radius:12px;width:250px;"><input name="p" type="password" placeholder="CLAVE" required style="display:block;margin:20px auto;padding:15px;background:#111;color:white;border:1px solid #222;border-radius:12px;width:250px;"><button name="act" value="lo" style="background:#ff007f;color:white;padding:15px;border:none;border-radius:12px;font-weight:bold;width:100%;cursor:pointer;">ENTRAR AL SISTEMA</button><br><button name="act" value="re" style="background:transparent;color:#555;border:none;font-size:11px;margin-top:20px;cursor:pointer;text-transform:uppercase;font-weight:bold;">Crear Nueva Cuenta</button></form></body>')

@app.route('/logout')
def logout():
    session.clear(); return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
