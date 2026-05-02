from flask import Flask, render_template_string, request, send_file, redirect, url_for, session, flash
import yt_dlp, os, json, random, string, threading, requests

app = Flask(__name__)
app.secret_key = 'demon_v12_empire_2026'

# Carpetas
DB_FILE = "demon_data.json"
download_folder = "downloads"
os.makedirs(download_folder, exist_ok=True)

# --- BASE DE DATOS ---
def load_db():
    default = {"users": {"demon": {"password": "123", "is_admin": True, "is_vip": True, "expiry": "ETERNAL"}}, "keys": {}, "broadcast": "👹 DEMON V12 ONLINE | DUEÑO: @DEMON_MASTER"}
    if not os.path.exists(DB_FILE) or os.stat(DB_FILE).st_size == 0:
        save_db(default); return default
    try:
        with open(DB_FILE, 'r') as f: return json.load(f)
    except: return default

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

# --- MOTOR DE DESCARGA ---
def pro_downloader(url, username, mode="free"):
    prefix = f"{username}_"
    ydl_opts = {'outtmpl': f'{download_folder}/{prefix}%(title).35s.%(ext)s', 'quiet': True}
    if mode == "vip": ydl_opts.update({'external_downloader': 'aria2c', 'external_downloader_args': ['-x', '16', '-k', '1M']})
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url]); return True
    except: return False

# --- INTERFAZ MAESTRA ---
UI_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap" rel="stylesheet">
    <style>
        body { background: #000; color: #aaa; font-family: sans-serif; }
        .orbitron { font-family: 'Orbitron', sans-serif; }
        .neon-border { border: 1px solid #ff007f; box-shadow: 0 0 15px #ff007f33; }
        .glass { background: rgba(10, 10, 15, 0.95); border: 1px solid #1f1f23; border-radius: 25px; }
        .hidden { display: none; }
        .tab-btn.active { color: #ff007f; border-bottom: 2px solid #ff007f; }
    </style>
</head>
<body class="p-4">
    <div class="max-w-md mx-auto">
        <header class="glass neon-border p-6 mb-6 flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-black text-white orbitron">DEMON<span class="text-pink-600">V12</span></h1>
                <p class="text-[8px] tracking-widest text-zinc-500 uppercase">Neural Terminal</p>
            </div>
            <div class="text-right">
                <p class="text-xs font-bold text-white uppercase">{{user}}</p>
                <p class="text-[9px] text-pink-500 font-black italic">{{expiry}}</p>
            </div>
        </header>

        <nav class="flex justify-between mb-6 text-[10px] font-black uppercase border-b border-zinc-900 pb-3">
            <button onclick="show('dl')" class="tab-btn active">Descarga</button>
            <button onclick="show('vault')" class="tab-btn">Bóveda</button>
            <button onclick="show('guia')" class="tab-btn">Guía Full</button>
            <button onclick="show('set')" class="tab-btn">Ajustes</button>
        </nav>

        <div id="dl" class="section glass p-6 text-center">
            <form action="/download" method="POST" class="space-y-4">
                <input type="url" name="url" placeholder="Pega el link aquí..." class="w-full bg-black border border-zinc-800 p-4 rounded-2xl text-white text-xs outline-none" required>
                <div class="grid grid-cols-2 gap-3">
                    <button name="mode" value="free" class="bg-zinc-900 text-white py-4 rounded-2xl text-[10px] font-bold">NORMAL</button>
                    <button name="mode" value="vip" class="bg-pink-600 text-white py-4 rounded-2xl text-[10px] font-bold">VIP TURBO</button>
                </div>
            </form>
        </div>

        <div id="guia" class="section hidden glass p-6 text-[10px] space-y-3">
            <h3 class="text-pink-500 font-bold uppercase orbitron">Manual Full V12</h3>
            <p><b>[VIP TURBO]:</b> Usa 16 hilos de descarga para máxima velocidad y bypass de límites.</p>
            <p><b>[BÓVEDA]:</b> Tus archivos se guardan aquí para descarga directa al móvil.</p>
            <p><b>[KEYS]:</b> El admin genera licencias de Horas/Días/Meses/Años.</p>
        </div>

        <div id="vault" class="section hidden glass p-4 space-y-2">
            {% for f in files %}
            <div class="flex justify-between items-center bg-black/60 p-4 rounded-2xl border border-zinc-900">
                <p class="text-[9px] text-zinc-300 truncate w-40 uppercase">{{f}}</p>
                <a href="/get/{{f}}" class="text-blue-500 bg-blue-500/10 p-2 rounded-lg">Bajar</a>
            </div>
            {% endfor %}
        </div>
        
        <div id="set" class="section hidden glass p-6 text-center">
            <a href="/logout" class="text-red-600 text-xs font-bold uppercase">Cerrar Sesión</a>
        </div>
    </div>

    <script>
        function show(id) {
            document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
            document.getElementById(id).classList.remove('hidden');
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
    udata = db['users'].get(u, {"expiry": "FREE"})
    files = [f for f in os.listdir(download_folder) if f.startswith(u)]
    return render_template_string(UI_HTML, user=u, expiry=udata['expiry'], files=files)

@app.route('/download', methods=['POST'])
def download():
    threading.Thread(target=pro_downloader, args=(request.form.get('url'), session['u'], request.form.get('mode'))).start()
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('u'); p = request.form.get('p')
        db = load_db()
        if u in db['users'] and db['users'][u]['password'] == p:
            session['u'] = u; return redirect('/')
    return '<body><form method="POST">User: <input name="u"><br>Pass: <input name="p" type="password"><br><button>LOGIN</button></form></body>'

@app.route('/logout')
def logout(): session.clear(); return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
                                                                                                     
