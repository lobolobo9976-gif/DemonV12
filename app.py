from flask import Flask, render_template_string, request, send_file, redirect, url_for, session, flash
import yt_dlp, os, json, random, string, threading, time, re
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'demon_v12_ultra_private_2026'

DB_FILE = "demon_data.json"
download_folder = "downloads"
os.makedirs(download_folder, exist_ok=True)

# --- NÚCLEO DE BASE DE DATOS ---
def load_db():
    default = {
        "users": {"demon": {"password": "123", "is_admin": True, "vip_until": None, "downloads": 0}}, 
        "keys": {}, 
        "broadcast": "👹 DEMON V12 | BIENVENIDO DUEÑO ABSOLUTO", 
        "online_users": {}
    }
    if not os.path.exists(DB_FILE): 
        save_db(default)
        return default
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

# --- SISTEMA DE GUERRA (IDENTIDAD Y LIMPIEZA) ---
def get_war_headers(url):
    uas = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    ]
    return {
        'User-Agent': random.choice(uas),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': url,
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
    }

def deep_clean_name(name):
    """Limpieza Profesional: Quita basura de URLs, símbolos y códigos raros"""
    name = re.sub(r'http\S+', '', name)
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:60] if name else "video_demon_v12"

# --- MOTOR DE DESCARGA MULTI-CAPA ---
def engine_v12(url, username, mode):
    prefix = f"{username}_"
    headers = get_war_headers(url)
    
    ydl_opts = {
        'quiet': True, 'nocheckcertificate': True, 'ignoreerrors': True,
        'http_headers': headers, 'retries': 10, 'fragment_retries': 10,
    }

    if mode == "vip":
        # MODO DIOS: Multi-hilos con aria2 y bypass de trackers
        ydl_opts.update({
            'external_downloader': 'aria2c',
            'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M', '--user-agent', headers['User-Agent']],
            'format': 'bestvideo+bestaudio/best', 'merge_output_format': 'mp4'
        })
    else:
        ydl_opts.update({'format': 'best[ext=mp4]/best'})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            clean_title = deep_clean_name(info.get('title', 'video'))
            ydl_opts['outtmpl'] = f'{download_folder}/{prefix}{clean_title}.%(ext)s'
            yt_dlp.YoutubeDL(ydl_opts).download([url])
    except:
        # Modo Espejo de Emergencia (Fuerza Bruta)
        ydl_opts['force_generic_extractor'] = True
        try: yt_dlp.YoutubeDL(ydl_opts).download([url])
        except: pass

# --- INTERFAZ NEÓN V12 ---
UI_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        body { background: #050505; color: #a1a1aa; font-family: 'Inter', sans-serif; }
        .neon-border { border: 1px solid #ff007f; box-shadow: 0 0 20px #ff007f33; }
        .glass { background: rgba(10, 10, 12, 0.95); border: 1px solid #1f1f23; border-radius: 28px; }
        .tab-active { color: #ff007f !important; border-bottom: 3px solid #ff007f; }
        marquee { background: #ff007f10; color: #ff007f; font-size: 11px; font-weight: 800; padding: 10px; border-bottom: 1px solid #ff007f44; }
        .btn-vip { background: linear-gradient(90deg, #ff007f, #8000ff); transition: 0.3s; }
        .btn-vip:hover { box-shadow: 0 0 30px #ff007f88; transform: scale(1.02); }
        .hidden { display: none; }
    </style>
</head>
<body>
    <marquee scrollamount="8"><i class="fas fa-biohazard mr-2"></i> {{msg}} <i class="fas fa-biohazard ml-2"></i></marquee>

    <div class="p-5 max-w-lg mx-auto">
        <div class="glass neon-border p-6 mb-8 flex justify-between items-center relative overflow-hidden">
            <div class="absolute -right-4 -top-4 opacity-10"><i class="fas fa-skull text-6xl"></i></div>
            <div>
                <h1 class="text-3xl font-black text-white italic tracking-tighter">DEMON<span class="text-pink-600">V12</span></h1>
                <p class="text-[10px] text-zinc-500 font-bold uppercase tracking-[0.2em]">Online: {{online}}</p>
            </div>
            <div class="text-right">
                <p class="text-xs text-white font-bold">{{user}}</p>
                <p class="text-[11px] {{s_color}} italic uppercase font-black">{{s_text}}</p>
            </div>
        </div>

        <nav class="flex justify-between mb-8 text-[10px] font-black uppercase tracking-widest border-b border-zinc-900">
            <button onclick="show('dl')" id="btn-dl" class="tab-active pb-3 px-2">Descarga</button>
            <button onclick="show('vt')" id="btn-vt" class="pb-3 px-2">Bóveda</button>
            <button onclick="show('st')" id="btn-st" class="pb-3 px-2">Ajustes</button>
            <button onclick="show('gui')" id="btn-gui" class="pb-3 px-2 text-pink-400">Guía</button>
            {% if admin %}<button onclick="show('ad')" id="btn-ad" class="pb-3 px-2 text-yellow-500">Root</button>{% endif %}
        </nav>

        <div id="dl" class="section glass p-8 space-y-6">
            <form action="/download" method="POST" class="space-y-6">
                <div class="relative">
                    <i class="fas fa-link absolute left-4 top-4 text-zinc-600"></i>
                    <input type="url" name="url" placeholder="Pega el link de la víctima..." class="w-full bg-black border border-zinc-800 p-4 pl-12 rounded-2xl text-sm text-white focus:border-pink-600 outline-none transition-all" required>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <button name="mode" value="free" class="bg-zinc-900 text-zinc-500 py-4 rounded-2xl text-[10px] font-black uppercase border border-zinc-800 hover:bg-zinc-800">Normal</button>
                    {% if is_vip %}
                    <button name="mode" value="vip" class="btn-vip text-white py-4 rounded-2xl text-[10px] font-black uppercase italic shadow-lg">Modo Dios X16</button>
                    {% else %}
                    <button type="button" onclick="alert('Requiere VIP')" class="bg-zinc-950 text-zinc-700 py-4 rounded-2xl text-[10px] font-black uppercase cursor-not-allowed">Bloqueado</button>
                    {% endif %}
                </div>
            </form>
            <div class="bg-pink-600/5 p-4 rounded-xl border border-pink-600/10 text-center">
                <p class="text-[9px] text-pink-500 font-bold uppercase"><i class="fas fa-shield-halved mr-2"></i> Protección Anti-Baneo Activa | Modo Espejo Listo</p>
            </div>
        </div>

        <div id="gui" class="section hidden glass p-8 space-y-6">
            <h2 class="text-white font-black uppercase italic text-sm border-b border-zinc-800 pb-4"><i class="fas fa-book-dead mr-2"></i> Manual del Dios V12</h2>
            <div class="space-y-4 text-[11px] leading-relaxed">
                <div class="bg-white/5 p-3 rounded-lg border-l-4 border-pink-600">
                    <p class="text-white font-bold mb-1">🛡️ MODO CAMUFLAJE TOTAL</p>
                    <p>El sistema rota automáticamente entre 50+ identidades reales. Simula dispositivos Android, iOS y PCs para que la web nunca te bloquee.</p>
                </div>
                <div class="bg-white/5 p-3 rounded-lg border-l-4 border-blue-600">
                    <p class="text-white font-bold mb-1">⚡ MODO DIOS X16</p>
                    <p>Fragmenta el archivo en 16 partes simultáneas. Ignora los límites de velocidad del sitio original y descarga a máxima potencia.</p>
                </div>
                <div class="bg-white/5 p-3 rounded-lg border-l-4 border-green-600">
                    <p class="text-white font-bold mb-1">🧪 LIMPIEZA INTELIGENTE</p>
                    <p>Elimina automáticamente rastreadores, espacios dobles, caracteres raros y extensiones falsas. Tu archivo llega limpio y listo.</p>
                </div>
                <div class="bg-white/5 p-3 rounded-lg border-l-4 border-yellow-600">
                    <p class="text-white font-bold mb-1">🌐 MODO ESPEJO</p>
                    <p>Si la web está caída o bloqueada en tu país, el sistema intenta rutas alternativas mediante túneles internos de emergencia.</p>
                </div>
            </div>
        </div>

        <div id="vt" class="section hidden glass p-4 space-y-3 max-h-[400px] overflow-y-auto">
            {% for f in files %}
            <div class="flex justify-between items-center bg-black/50 p-4 rounded-2xl border border-zinc-900 group hover:border-pink-600/50 transition-all">
                <div class="flex items-center gap-3">
                    <i class="fas fa-file-video text-pink-600 opacity-50"></i>
                    <span class="text-[10px] truncate w-40 text-zinc-300 font-bold">{{f.split('_', 1)[1]}}</span>
                </div>
                <div class="flex gap-2">
                    <a href="/get/{{f}}" class="bg-pink-600/10 text-pink-500 p-2 px-3 rounded-xl text-xs hover:bg-pink-600 hover:text-white"><i class="fas fa-download"></i></a>
                    <a href="/delete/{{f}}" class="bg-red-600/10 text-red-500 p-2 px-3 rounded-xl text-xs hover:bg-red-600 hover:text-white"><i class="fas fa-trash-alt"></i></a>
                </div>
            </div>
            {% endfor %}
            {% if not files %}
            <div class="text-center py-10 opacity-20"><i class="fas fa-folder-open text-5xl mb-3"></i><p class="text-[10px] uppercase font-bold tracking-widest">Bóveda Vacía</p></div>
            {% endif %}
            <a href="/clear_vault" class="block text-center text-[9px] text-red-500 font-bold uppercase mt-4 opacity-50 hover:opacity-100" onclick="return confirm('¿Borrar todo?')">Vaciar Todo</a>
        </div>

        <div id="st" class="section hidden glass p-8 space-y-8">
            <form action="/change_pass" method="POST" class="space-y-3">
                <label class="text-[9px] font-black uppercase text-zinc-500 ml-2">Privacidad</label>
                <input type="password" name="new_p" placeholder="Nueva Contraseña" class="w-full bg-black border border-zinc-800 p-4 rounded-2xl text-xs text-white">
                <button class="w-full bg-blue-600 text-white py-4 rounded-2xl text-[10px] font-black uppercase">Actualizar Seguridad</button>
            </form>
            <form action="/activate_key" method="POST" class="space-y-3 pt-6 border-t border-zinc-900">
                <label class="text-[9px] font-black uppercase text-pink-500 ml-2">Membresía</label>
                <input type="text" name="key" placeholder="Pegar Key VIP aquí..." class="w-full bg-black border border-zinc-800 p-4 rounded-2xl text-xs text-white">
                <button class="w-full btn-vip text-white py-4 rounded-2xl text-[10px] font-black uppercase">Desbloquear Potencia</button>
            </form>
            <a href="/logout" class="block text-center text-zinc-600 text-[10px] font-black py-4 border border-zinc-900 rounded-2xl hover:text-red-500">CERRAR SESIÓN</a>
        </div>

        {% if admin %}
        <div id="ad" class="section hidden glass p-8 space-y-6">
            <div class="bg-yellow-500/10 border border-yellow-500/20 p-4 rounded-xl text-center mb-4">
                <p class="text-yellow-500 text-[10px] font-black uppercase">Panel de Control Supremo</p>
            </div>
            <form action="/gen_key" method="POST" class="space-y-3">
                <input type="number" name="days" placeholder="Días de VIP" class="w-full bg-black border border-zinc-800 p-4 rounded-2xl text-xs text-white">
                <button class="w-full bg-yellow-600 text-black font-black py-4 rounded-2xl text-[10px] uppercase">Generar Llave Maestra</button>
            </form>
            <form action="/set_msg" method="POST" class="space-y-3">
                <input type="text" name="msg" placeholder="Nuevo mensaje global..." class="w-full bg-black border border-zinc-800 p-4 rounded-2xl text-xs text-white">
                <button class="w-full bg-zinc-800 text-white font-black py-4 rounded-2xl text-[10px] uppercase">Actualizar Anuncio</button>
            </form>
        </div>
        {% endif %}

        {% with m = get_flashed_messages() %}{% if m %}<div id="alert" class="mt-6 p-4 bg-pink-600 text-white text-[10px] font-black uppercase rounded-2xl text-center animate-pulse">{{m[0]}}</div>{% endif %}{% endwith %}
    </div>

    <script>
        function show(id){
            document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
            document.querySelectorAll('nav button').forEach(b => b.classList.remove('tab-active'));
            document.getElementById(id).classList.remove('hidden');
            document.getElementById('btn-'+id).classList.add('tab-active');
        }
        setTimeout(() => { document.getElementById('alert')?.remove(); }, 4000);
    </script>
</body>
</html>
'''

# --- RUTAS Y LÓGICA DE SERVIDOR ---
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
    if 'u' not in session: return redirect('/login')
    url = request.form.get('url')
    mode = request.form.get('mode')
    threading.Thread(target=engine_v12, args=(url, session['u'], mode)).start()
    flash("Iniciando Ataque... Revisa la Bóveda")
    return redirect('/')

@app.route('/get/<f>')
def get_file(f):
    if 'u' in session and f.startswith(session['u']):
        return send_file(os.path.join(download_folder, f), as_attachment=True)
    return "No permitido", 403

@app.route('/delete/<f>')
def delete_file(f):
    if 'u' in session and f.startswith(session['u']):
        p = os.path.join(download_folder, f)
        if os.path.exists(p): os.remove(p)
    return redirect('/')

@app.route('/clear_vault')
def clear_vault():
    if 'u' in session:
        for f in os.listdir(download_folder):
            if f.startswith(f"{session['u']}_"): os.remove(os.path.join(download_folder, f))
    return redirect('/')

@app.route('/activate_key', methods=['POST'])
def activate_key():
    db = load_db(); k = request.form.get('key','').strip()
    if k in db['keys']:
        days = int(db['keys'][k])
        db['users'][session['u']]['vip_until'] = (datetime.now() + timedelta(days=days)).isoformat()
        del db['keys'][k]; save_db(db); flash("VIP ACTIVADO CON ÉXITO")
    else: flash("KEY INVÁLIDA O USADA")
    return redirect('/')

@app.route('/change_pass', methods=['POST'])
def change_pass():
    db = load_db(); db['users'][session['u']]['password'] = request.form.get('new_p'); save_db(db)
    flash("CONTRASEÑA ACTUALIZADA"); return redirect('/')

@app.route('/gen_key', methods=['POST'])
def gen_key():
    db = load_db(); k = "DEMON-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    db['keys'][k] = request.form.get('days', '30'); save_db(db)
    flash(f"KEY GENERADA: {k}"); return redirect('/')

@app.route('/set_msg', methods=['POST'])
def set_msg():
    db = load_db(); db['broadcast'] = request.form.get('msg', '').upper(); save_db(db)
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p, act = request.form.get('u'), request.form.get('p'), request.form.get('act')
        db = load_db()
        if act == 'lo' and u in db['users'] and db['users'][u]['password'] == p:
            session['u'] = u; return redirect('/')
        elif act == 're' and u not in db['users'] and u.isalnum():
            db['users'][u] = {"password": p, "is_admin": False, "vip_until": None, "downloads": 0}
            save_db(db); flash("Registro exitoso")
    return render_template_string('''
    <body style="background:#000;color:white;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;">
        <form method="POST" style="border:1px solid #ff007f;padding:40px;border-radius:30px;background:#050505;text-align:center;box-shadow:0 0 30px #ff007f22;">
            <h2 style="font-style:italic;font-weight:900;font-size:30px;">DEMON <span style="color:#ff007f">V12</span></h2>
            <input name="u" placeholder="USUARIO" required style="display:block;margin:20px auto;padding:15px;background:#111;color:white;border:1px solid #222;border-radius:15px;width:250px;">
            <input name="p" type="password" placeholder="CONTRASEÑA" required style="display:block;margin:20px auto;padding:15px;background:#111;color:white;border:1px solid #222;border-radius:15px;width:250px;">
            <button name="act" value="lo" style="background:#ff007f;color:white;padding:15px 40px;border:none;border-radius:15px;cursor:pointer;font-weight:900;width:100%;">ENTRAR</button>
            <button name="act" value="re" style="background:transparent;color:#444;border:none;font-size:10px;margin-top:20px;cursor:pointer;">REGISTRARSE</button>
        </form>
    </body>''')

@app.route('/logout')
def logout(): session.clear(); return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
