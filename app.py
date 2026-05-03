import os
import json
import random
import string
import threading
import time
import re
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, send_file, redirect, url_for, session, flash
import yt_dlp

app = Flask(__name__)
app.secret_key = 'demon_v12_ultra_private_2026_full_unlocked'

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
        "broadcast": "👹 DEMON V12 | BIENVENIDO DUEÑO ABSOLUTO - @LOBOTIGRE 💀", 
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
    return f"VIP: {res.days}D {res.seconds // 3600}H", "text-pink-500 font-black", True

# --- MOTOR DE DESCARGA V12 (GUERRA TOTAL) ---
def engine_v12(url, username, mode):
    prefix = f"{username}_"
    # Rotación de Identidad (Camuflaje)
    uas = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15',
        'Mozilla/5.0 (Linux; Android 14; SM-S918B) Chrome/124.0.0.0 Mobile Safari/537.36'
    ]
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'http_headers': {'User-Agent': random.choice(uas)},
        # Limpieza de nombre integrada
        'outtmpl': f'{DOWNLOAD_FOLDER}/{prefix}%(title).50s.%(ext)s',
    }

    if mode == "vip":
        # Modo Dios: Máxima potencia y calidad
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'concurrent_fragment_downloads': 16,
        })
    else:
        ydl_opts.update({'format': 'best[ext=mp4]/best'})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        # Modo Espejo (Reintento automático)
        print(f"Error detectado: {e}. Iniciando Modo Espejo...")
        try:
            ydl_opts['force_generic_extractor'] = True
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except: pass

# --- INTERFAZ ÉPICA V12 ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
        body { background: #000; color: #a1a1aa; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        .neon-text { text-shadow: 0 0 10px #ff007f, 0 0 20px #ff007f; }
        .neon-border { border: 1px solid #ff007f; box-shadow: 0 0 20px #ff007f33; }
        .glass { background: rgba(10, 10, 12, 0.98); border: 1px solid #1f1f23; border-radius: 28px; }
        .tab-active { color: #ff007f !important; border-bottom: 3px solid #ff007f; font-weight: 900; }
        marquee { background: #ff007f15; color: #ff007f; font-size: 11px; font-weight: 800; padding: 10px; border-bottom: 1px solid #ff007f44; }
        .btn-god { background: linear-gradient(90deg, #ff007f, #8000ff); transition: 0.3s; }
        .btn-god:hover { box-shadow: 0 0 30px #ff007f88; transform: scale(1.02); }
        .hidden { display: none; }
    </style>
</head>
<body>
    <marquee scrollamount="8"><i class="fas fa-biohazard mr-2"></i> {{msg}} <i class="fas fa-biohazard ml-2"></i></marquee>

    <div class="p-4 max-w-lg mx-auto min-h-screen">
        <div class="glass neon-border p-6 mb-8 flex justify-between items-center relative overflow-hidden">
            <div class="absolute -right-6 -top-6 opacity-10"><i class="fas fa-skull text-7xl"></i></div>
            <div>
                <h1 style="font-family:'Orbitron';" class="text-3xl font-black text-white italic tracking-tighter neon-text">DEMON<span class="text-pink-600">V12</span></h1>
                <p class="text-[9px] text-zinc-500 font-bold uppercase tracking-[0.3em]">System Status: <span class="text-green-500">Online</span></p>
            </div>
            <div class="text-right z-10">
                <p class="text-xs text-white font-bold">{{user}}</p>
                <p class="text-[11px] {{s_color}} italic uppercase font-black tracking-tighter">{{s_text}}</p>
            </div>
        </div>

        <nav class="flex justify-between mb-8 text-[10px] font-black uppercase tracking-widest border-b border-zinc-900">
            <button onclick="show('dl')" id="btn-dl" class="tab-active pb-3 px-2">Ataque</button>
            <button onclick="show('vt')" id="btn-vt" class="pb-3 px-2">Bóveda</button>
            <button onclick="show('gui')" id="btn-gui" class="pb-3 px-2 text-blue-400">Guía Full</button>
            <button onclick="show('st')" id="btn-st" class="pb-3 px-2">Ajustes</button>
            {% if admin %}<button onclick="show('ad')" id="btn-ad" class="pb-3 px-2 text-yellow-500">Dueño</button>{% endif %}
        </nav>

        <div id="dl" class="section glass p-8 space-y-6">
            <form action="/download" method="POST" class="space-y-6">
                <div class="relative">
                    <i class="fas fa-bolt absolute left-4 top-4 text-zinc-600"></i>
                    <input type="url" name="url" placeholder="Pega el link de la víctima..." class="w-full bg-black border border-zinc-800 p-4 pl-12 rounded-2xl text-sm text-white focus:border-pink-600 outline-none transition-all" required>
                </div>
                <div class="grid grid-cols-1 gap-4">
                    <button name="mode" value="vip" class="btn-god text-white py-4 rounded-2xl text-[12px] font-black uppercase italic tracking-widest shadow-lg">
                        <i class="fas fa-skull-crossbones mr-2"></i> MODO DIOS X16
                    </button>
                    <button name="mode" value="free" class="bg-zinc-900 text-zinc-500 py-3 rounded-2xl text-[10px] font-black uppercase border border-zinc-800 hover:bg-zinc-800 transition-all">Descarga Normal</button>
                </div>
            </form>
            <div class="bg-pink-600/5 p-4 rounded-xl border border-pink-600/10 text-center">
                <p class="text-[9px] text-pink-500 font-bold uppercase tracking-widest"><i class="fas fa-shield-halved mr-2"></i> Camuflaje Anti-Baneo Activado</p>
            </div>
        </div>

        <div id="vt" class="section hidden glass p-4 space-y-3">
            <div class="flex justify-between items-center px-2 mb-2">
                <span class="text-[10px] font-black uppercase tracking-tighter text-zinc-500">Archivos Obtenidos</span>
                <a href="/clear_vault" onclick="return confirm('¿Eliminar TODO?')" class="text-[10px] text-red-600 font-black uppercase hover:underline"><i class="fas fa-trash-alt mr-1"></i> Vaciar Todo</a>
            </div>
            <div class="max-h-[400px] overflow-y-auto space-y-3 pr-2">
                {% for f in files %}
                <div class="flex justify-between items-center bg-black/50 p-4 rounded-2xl border border-zinc-900 group hover:border-pink-600/40 transition-all">
                    <div class="flex items-center gap-3">
                        <i class="fas fa-file-video text-pink-600 opacity-50"></i>
                        <span class="text-[11px] truncate w-40 text-zinc-300 font-bold">{{f.split('_', 1)[1]}}</span>
                    </div>
                    <div class="flex gap-3">
                        <a href="/get/{{f}}" class="bg-pink-600/10 text-pink-500 p-2 px-3 rounded-xl text-xs hover:bg-pink-600 hover:text-white transition-all"><i class="fas fa-download"></i></a>
                        <a href="/delete/{{f}}" class="bg-red-600/10 text-red-500 p-2 px-3 rounded-xl text-xs hover:bg-red-600 hover:text-white transition-all"><i class="fas fa-times"></i></a>
                    </div>
                </div>
                {% else %}
                <div class="text-center py-20 opacity-20">
                    <i class="fas fa-folder-open text-5xl mb-4"></i>
                    <p class="text-xs font-black uppercase italic">Bóveda Vacía</p>
                </div>
                {% endfor %}
            </div>
        </div>

        <div id="gui" class="section hidden glass p-8 space-y-6">
            <h2 class="text-white font-black uppercase italic text-sm border-b border-pink-600 pb-4 tracking-widest"><i class="fas fa-book-dead mr-2"></i> Manual del Dios V12</h2>
            <div class="space-y-4 text-[11px] leading-relaxed">
                <div class="bg-zinc-900/50 p-4 rounded-2xl border-l-4 border-pink-600">
                    <p class="text-white font-black mb-1 uppercase tracking-tighter">1. MODO DIOS X16</p>
                    <p class="text-zinc-500">Fragmenta el video en 16 partes. Descarga a la velocidad máxima permitida por tu conexión, saltando límites.</p>
                </div>
                <div class="bg-zinc-900/50 p-4 rounded-2xl border-l-4 border-blue-600">
                    <p class="text-white font-black mb-1 uppercase tracking-tighter">2. CAMUFLAJE TOTAL</p>
                    <p class="text-zinc-500">El sistema finge ser un iPhone o Android real. Los sitios no sabrán que eres un bot de Render.</p>
                </div>
                <div class="bg-zinc-900/50 p-4 rounded-2xl border-l-4 border-green-600">
                    <p class="text-white font-black mb-1 uppercase tracking-tighter">3. LIMPIEZA PROFUNDA</p>
                    <p class="text-zinc-500">Elimina automáticamente espacios, links y símbolos raros del nombre del archivo antes de guardarlo.</p>
                </div>
                <div class="bg-zinc-900/50 p-4 rounded-2xl border-l-4 border-yellow-600">
                    <p class="text-white font-black mb-1 uppercase tracking-tighter">4. RANGO DUEÑO</p>
                    <p class="text-zinc-500">El dueño puede regalar Keys VIP a los fieles. Controla el Marquee y genera llaves de acceso.</p>
                </div>
            </div>
        </div>

        <div id="st" class="section hidden glass p-8 space-y-8">
            <form action="/update_pass" method="POST" class="space-y-3">
                <label class="text-[10px] font-black uppercase text-zinc-600 ml-2">Cambiar Seguridad</label>
                <input type="password" name="new_pass" placeholder="Nueva Contraseña" class="w-full bg-black border border-zinc-900 p-4 rounded-2xl text-xs text-white">
                <button class="w-full bg-blue-600 text-white py-4 rounded-2xl text-[10px] font-black uppercase">Actualizar Clave</button>
            </form>
            <form action="/activate_key" method="POST" class="space-y-3 pt-6 border-t border-zinc-900">
                <label class="text-[10px] font-black uppercase text-pink-600 ml-2">Canjear Key VIP</label>
                <input type="text" name="key" placeholder="Pega tu código aquí..." class="w-full bg-black border border-zinc-900 p-4 rounded-2xl text-xs text-white">
                <button class="w-full btn-god text-white py-4 rounded-2xl text-[10px] font-black uppercase italic">Subir a VIP</button>
            </form>
            <a href="/logout" class="block text-center text-zinc-700 text-[10px] font-black py-4 border border-zinc-900 rounded-2xl hover:text-red-500">CERRAR SESIÓN</a>
        </div>

        {% if admin %}
        <div id="ad" class="section hidden glass p-8 space-y-6">
            <div class="bg-yellow-500/10 border border-yellow-500/30 p-4 rounded-xl text-center">
                <p class="text-yellow-500 text-[11px] font-black uppercase italic">Consola de Control Supremo</p>
            </div>
            <form action="/gen_key" method="POST" class="space-y-3">
                <input type="number" name="days" placeholder="Días de VIP" class="w-full bg-black border border-zinc-900 p-4 rounded-2xl text-xs text-white">
                <button class="w-full bg-yellow-600 text-black font-black py-4 rounded-2xl text-[10px] uppercase">Generar Llave</button>
            </form>
            <form action="/update_broadcast" method="POST" class="space-y-3">
                <input type="text" name="msg" placeholder="Nuevo mensaje global..." class="w-full bg-black border border-zinc-800 p-4 rounded-2xl text-xs text-white">
                <button class="w-full bg-zinc-800 text-white font-black py-4 rounded-2xl text-[10px] uppercase">Actualizar Marquee</button>
            </form>
        </div>
        {% endif %}

        {% with m = get_flashed_messages() %}
            {% if m %}<div class="fixed bottom-10 left-0 w-full px-6 z-50 animate-bounce"><p class="bg-pink-600 text-white text-[11px] py-4 rounded-2xl font-black uppercase italic text-center shadow-2xl">{{m[0]}}</p></div>{% endif %}
        {% endwith %}
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

# --- RUTAS DE OPERACIÓN ---
@app.route('/')
def index():
    if 'u' not in session: return redirect('/login')
    db = load_db(); u = session['u']
    st_text, st_color, is_vip = get_user_status(u)
    files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(f"{u}_")]
    return render_template_string(HTML_TEMPLATE, user=u, s_text=st_text, s_color=st_color, is_vip=is_vip, admin=db['users'][u]['is_admin'], files=files, msg=db['broadcast'])

@app.route('/download', methods=['POST'])
def download():
    if 'u' not in session: return redirect('/login')
    threading.Thread(target=engine_v12, args=(request.form.get('url'), session['u'], request.form.get('mode'))).start()
    flash("🚀 ATAQUE INICIADO... REVISA LA BÓVEDA")
    return redirect('/')

@app.route('/get/<f>')
def get_file(f):
    if 'u' in session and f.startswith(session['u']):
        p = os.path.join(DOWNLOAD_FOLDER, f)
        if os.path.exists(p): return send_file(p, as_attachment=True)
    return "Error", 404

@app.route('/delete/<f>')
def delete_file(f):
    if 'u' in session and f.startswith(session['u']):
        p = os.path.join(DOWNLOAD_FOLDER, f)
        if os.path.exists(p): os.remove(p)
    return redirect('/')

@app.route('/clear_vault')
def clear_vault():
    if 'u' in session:
        for f in os.listdir(DOWNLOAD_FOLDER):
            if f.startswith(f"{session['u']}_"): os.remove(os.path.join(DOWNLOAD_FOLDER, f))
        flash("🧹 BÓVEDA VACIADA")
    return redirect('/')

@app.route('/gen_key', methods=['POST'])
def gen_key():
    db = load_db(); k = "DV12-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    db['keys'][k] = request.form.get('days', '30'); save_db(db); flash(f"KEY: {k}")
    return redirect('/')

@app.route('/update_broadcast', methods=['POST'])
def update_broadcast():
    db = load_db(); db['broadcast'] = request.form.get('msg', '').upper(); save_db(db)
    flash("ANUNCIO ACTUALIZADO"); return redirect('/')

@app.route('/activate_key', methods=['POST'])
def activate_key():
    db = load_db(); k = request.form.get('key','').strip()
    if k in db['keys']:
        days = int(db['keys'][k])
        db['users'][session['u']]['vip_until'] = (datetime.now() + timedelta(days=days)).isoformat()
        del db['keys'][k]; save_db(db); flash("🔥 VIP ACTIVADO - MODO DIOS UNLOCKED")
    else: flash("❌ KEY INVÁLIDA")
    return redirect('/')

@app.route('/update_pass', methods=['POST'])
def update_pass():
    db = load_db(); db['users'][session['u']]['password'] = request.form.get('new_pass'); save_db(db)
    flash("CONTRASENA ACTUALIZADA"); return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p, act = request.form.get('u'), request.form.get('p'), request.form.get('act')
        db = load_db()
        if act == 'lo' and u in db['users'] and db['users'][u]['password'] == p:
            session['u'] = u; return redirect('/')
        elif act == 're' and u not in db['users'] and u.isalnum():
            db['users'][u] = {"password": p, "is_admin": False, "vip_until": None}
            save_db(db); flash("REGISTRO EXITOSO")
    return render_template_string('<body style="background:#000;color:white;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;text-align:center;"><form method="POST" style="border:1px solid #ff007f;padding:50px;border-radius:30px;background:#050505;box-shadow:0 0 30px #ff007f33;"><h2 style="font-style:italic;font-weight:900;font-size:32px;margin-bottom:30px;">DEMON <span style="color:#ff007f">V12</span></h2><input name="u" placeholder="USUARIO" required style="display:block;margin:15px auto;padding:15px;background:#111;color:white;border:1px solid #222;border-radius:15px;width:260px;"><input name="p" type="password" placeholder="CLAVE" required style="display:block;margin:15px auto;padding:15px;background:#111;color:white;border:1px solid #222;border-radius:15px;width:260px;"><button name="act" value="lo" style="background:#ff007f;color:white;padding:15px;border:none;border-radius:15px;font-weight:900;width:100%;cursor:pointer;margin-top:10px;">ENTRAR AL SISTEMA</button><button name="act" value="re" style="background:transparent;color:#555;border:none;margin-top:20px;cursor:pointer;font-size:11px;font-weight:bold;text-transform:uppercase;">Registrarse</button></form></body>')

@app.route('/logout')
def logout(): session.clear(); return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
            
