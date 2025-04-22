import sys
import time

# Détection dynamique des dépendances manquantes
missing = []
try:
    import tkinter
except ImportError:
    missing.append('tkinter')
try:
    import playwright
except ImportError:
    missing.append('playwright')
try:
    import m3u8
except ImportError:
    missing.append('m3u8')
try:
    from PIL import Image, ImageTk
except ImportError:
    missing.append('Pillow')
try:
    import ffmpeg
except ImportError:
    missing.append('ffmpeg-python')

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import subprocess
import threading
import os
import time
from playwright.sync_api import sync_playwright
import json
import sys
import m3u8
import re
import io
from PIL import Image, ImageTk
import winsound
from urllib.request import urlopen
import platform
import venv

# === Thèmes ===
DARK_BG = "#181a20"
DARK_CARD = "#23272e"
DARK_ACCENT = "#4094f7"
DARK_TEXT = "#f5f6fa"
DARK_SUBTLE = "#bdbdbd"
DARK_SUCCESS = "#00e676"
DARK_ERROR = "#ff5252"
DARK_PROGRESS = "#1976d2"
DARK_SHADOW = "#12151a"

LIGHT_BG = "#f3f6fc"
LIGHT_CARD = "#fff"
LIGHT_ACCENT = "#4094f7"
LIGHT_TEXT = "#222"
LIGHT_SUBTLE = "#888"
LIGHT_SUCCESS = "#4caf50"
LIGHT_ERROR = "#b71c1c"
LIGHT_PROGRESS = "#4094f7"

dossier_sortie = os.path.join(os.getcwd(), "Téléchargements")
if not os.path.exists(dossier_sortie):
    try:
        os.makedirs(dossier_sortie)
    except Exception as e:
        tk.messagebox.showerror("Erreur", f"Impossible de créer le dossier de sortie : {e}")
        exit(1)

# --- Drag & drop cross-platform avec fallback si tkinterdnd2 non dispo ---
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

if DND_AVAILABLE:
    fenetre = TkinterDnD.Tk()
else:
    fenetre = tk.Tk()

fenetre.title("Kick.com VOD Downloader")
fenetre.geometry('650x570')
fenetre.configure(bg=DARK_BG)

def show_missing_deps_toast():
    msg = (
        "Dépendances manquantes : " + ', '.join(missing) +
        "\nOuvre un terminal dans ce dossier et lance :\n"
        "pip install -r requirements.txt"
    )
    # Détection automatique d'un venv
    venv_found = False
    venv_path = None
    for d in os.listdir(os.getcwd()):
        if os.path.isdir(d) and (os.path.exists(os.path.join(d, 'Scripts', 'activate')) or os.path.exists(os.path.join(d, 'bin', 'activate'))):
            venv_found = True
            venv_path = d
            break
    if venv_found:
        msg += f"\n(Venv détecté : {venv_path})"
    toast = tk.Toplevel(fenetre)
    toast.overrideredirect(True)
    toast.geometry(f"400x170+{fenetre.winfo_x()+60}+{fenetre.winfo_y()+60}")
    toast.configure(bg="#23272e")
    toast.attributes('-topmost', True)
    label = tk.Label(
        toast, text=msg, bg="#23272e", fg="#fff",
        font=("Segoe UI", 10, "bold"), wraplength=380, justify="left"
    )
    label.pack(fill='both', expand=True, padx=16, pady=(14,2))
    def copy_cmd():
        fenetre.clipboard_clear()
        fenetre.clipboard_append('pip install -r requirements.txt')
        btn_copier.config(text="✅ Copié !")
        toast.after(1500, lambda: btn_copier.config(text="Copier la commande"))
    def open_terminal():
        sys_plat = platform.system()
        try:
            if sys_plat == "Windows":
                subprocess.Popen(["start", "cmd"], shell=True)
            elif sys_plat == "Darwin":
                subprocess.Popen(["open", "-a", "Terminal", "."])
            elif sys_plat == "Linux":
                subprocess.Popen(["x-terminal-emulator"], cwd=os.getcwd())
        except Exception:
            pass
    def install_auto():
        try:
            pip_exe = sys.executable.replace('python.exe','Scripts\\pip.exe') if sys.platform.startswith('win') else sys.executable.replace('python','pip')
            subprocess.Popen([pip_exe, 'install', '-r', 'requirements.txt'])
            btn_install.config(text="✅ Installation lancée !")
            toast.after(2000, lambda: btn_install.config(text="Installer automatiquement"))
        except Exception:
            btn_install.config(text="Erreur installation")
    btn_copier = ttk.Button(toast, text="Copier la commande", command=copy_cmd)
    btn_copier.pack(pady=(0,2))
    btn_terminal = ttk.Button(toast, text="Ouvrir un terminal", command=open_terminal)
    btn_terminal.pack(pady=(0,2))
    btn_install = ttk.Button(toast, text="Installer automatiquement", command=install_auto)
    btn_install.pack(pady=(0,10))
    # Fade in
    for i in range(0, 11):
        toast.attributes('-alpha', 0.75 + 0.025*i)
        toast.update()
        time.sleep(0.01)
    toast.after(9000, toast.destroy)

if missing:
    # Affiche le toast après l'initialisation de la fenêtre principale
    fenetre.after(500, show_missing_deps_toast)

header = tk.Frame(fenetre, bg=DARK_ACCENT, highlightthickness=0)
header.pack(fill='x', pady=(0, 0))
logo = tk.Label(header, text='🎬', font=("Segoe UI Emoji", 22), bg=DARK_ACCENT)
logo.pack(side='left', padx=(18, 0), pady=13)
tk.Label(header, text='Kick.com VOD Downloader', font=("Segoe UI", 19, "bold"), bg=DARK_ACCENT, fg=DARK_TEXT).pack(side='left', padx=8, pady=13)

current_theme = "dark"
def switch_theme():
    global current_theme
    if current_theme == "dark":
        apply_light_theme()
        current_theme = "light"
    else:
        apply_dark_theme()
        current_theme = "dark"

def apply_dark_theme():
    fenetre.configure(bg=DARK_BG)
    header.configure(bg=DARK_ACCENT)
    logo.configure(bg=DARK_ACCENT)
    for w in [body, row1, row2, row3, row4, row5, row6, hist_card, footer]:
        w.configure(bg=DARK_BG if w!=hist_card else DARK_CARD)
    for l in [label_dossier, label_cookies, label_statut]:
        l.configure(bg=DARK_BG, fg=DARK_SUBTLE if l!=label_statut else DARK_ACCENT)
    style.theme_use("clam")
    style.configure("TLabel", background=DARK_BG, foreground=DARK_TEXT)
    style.configure("TButton", background=DARK_CARD, foreground=DARK_TEXT)
    style.map("TButton",
        background=[('active', DARK_ACCENT), ('!active', DARK_CARD)],
        foreground=[('active', '#fff'), ('!active', DARK_TEXT)]
    )
    style.configure("TEntry", fieldbackground=DARK_CARD, foreground=DARK_TEXT, insertcolor=DARK_ACCENT)
    style.configure("TProgressbar", troughcolor=DARK_CARD, background=DARK_PROGRESS)
    text_historique.configure(bg=DARK_BG, fg=DARK_TEXT, insertbackground=DARK_ACCENT)
    scroll.configure(bg=DARK_CARD, troughcolor=DARK_BG)
    hist_card.configure(bg=DARK_CARD)
    footer.configure(bg=DARK_BG)

def apply_light_theme():
    fenetre.configure(bg=LIGHT_BG)
    header.configure(bg=LIGHT_ACCENT)
    logo.configure(bg=LIGHT_ACCENT)
    for w in [body, row1, row2, row3, row4, row5, row6, hist_card, footer]:
        w.configure(bg=LIGHT_BG if w!=hist_card else LIGHT_CARD)
    for l in [label_dossier, label_cookies, label_statut]:
        l.configure(bg=LIGHT_BG, fg=LIGHT_SUBTLE if l!=label_statut else LIGHT_ACCENT)
    style.theme_use("clam")
    style.configure("TLabel", background=LIGHT_BG, foreground=LIGHT_TEXT)
    style.configure("TButton", background=LIGHT_CARD, foreground=LIGHT_TEXT)
    style.map("TButton",
        background=[('active', LIGHT_ACCENT), ('!active', LIGHT_CARD)],
        foreground=[('active', '#fff'), ('!active', LIGHT_TEXT)]
    )
    style.configure("TEntry", fieldbackground=LIGHT_CARD, foreground=LIGHT_TEXT, insertcolor=LIGHT_ACCENT)
    style.configure("TProgressbar", troughcolor=LIGHT_CARD, background=LIGHT_PROGRESS)
    text_historique.configure(bg=LIGHT_BG, fg=LIGHT_TEXT, insertbackground=LIGHT_ACCENT)
    scroll.configure(bg=LIGHT_CARD, troughcolor=LIGHT_BG)
    hist_card.configure(bg=LIGHT_CARD)
    footer.configure(bg=LIGHT_BG)

bouton_theme = ttk.Button(header, text="☀️/🌙", command=switch_theme)
bouton_theme.pack(side='right', padx=15, pady=10)

body = tk.Frame(fenetre, bg=DARK_BG)
body.pack(fill='both', expand=True, padx=22, pady=8)

row1 = tk.Frame(body, bg=DARK_BG)
row1.pack(fill='x', pady=7)
tk.Label(row1, text='URL Kick.com VOD :', bg=DARK_BG, fg=DARK_TEXT, anchor='w', font=("Segoe UI", 11)).pack(side='left', padx=(0,12))
entry_url = ttk.Entry(row1, width=54)
entry_url.pack(side='left')

row2 = tk.Frame(body, bg=DARK_BG)
row2.pack(fill='x', pady=7)
tk.Label(row2, text='Nom du fichier :', bg=DARK_BG, fg=DARK_TEXT, anchor='w', font=("Segoe UI", 11)).pack(side='left', padx=(0,12))
entry_nom = ttk.Entry(row2, width=34)
entry_nom.insert(0, "video_kick")
entry_nom.pack(side='left')

row3 = tk.Frame(body, bg=DARK_BG)
row3.pack(fill='x', pady=7)
label_dossier = tk.Label(row3, text=f"Dossier de sortie : {dossier_sortie}", bg=DARK_BG, fg=DARK_SUBTLE, font=("Segoe UI", 10))
label_dossier.pack(side='left')

row4 = tk.Frame(body, bg=DARK_BG)
row4.pack(fill='x', pady=7)
bouton_cookies = ttk.Button(row4, text="Sélectionner un cookies.txt (optionnel)", command=lambda: choisir_cookies())
bouton_cookies.pack(side='left', padx=(0,8))
label_cookies = tk.Label(row4, text="Aucun cookie sélectionné", bg=DARK_BG, fg=DARK_SUBTLE, font=("Segoe UI", 10))
label_cookies.pack(side='left')

row5 = tk.Frame(body, bg=DARK_BG)
row5.pack(fill='x', pady=7)
progress_var = tk.DoubleVar()
progress = ttk.Progressbar(row5, variable=progress_var, maximum=100, length=350, mode="determinate")
progress.pack(side='left', padx=(0,15))
statut = tk.StringVar()
statut.set("En attente...")
label_statut = tk.Label(row5, textvariable=statut, font=("Segoe UI", 10), bg=DARK_BG, fg=DARK_ACCENT)
label_statut.pack(side='left')

row6 = tk.Frame(body, bg=DARK_BG)
row6.pack(fill='x', pady=7)

class RippleButton(ttk.Button):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.bind("<Button-1>", self.ripple)
    def ripple(self, event):
        x, y = event.x, event.y
        circle = tk.Canvas(self, width=0, height=0, bg='', highlightthickness=0)
        circle.place(x=x, y=y, anchor="center")
        for r in range(0, 30, 2):
            circle.config(width=r*2, height=r*2)
            circle.create_oval(0, 0, r*2, r*2, outline=DARK_ACCENT, width=2)
            self.update()
            self.after(6)
        circle.destroy()

bouton_dl_pw = RippleButton(row6, text="Télécharger la VOD", command=lambda: telecharger_playwright())
bouton_dl_pw.pack(side='left', padx=7)
bouton_ouvrir = RippleButton(row6, text="Ouvrir dossier", command=lambda: ouvrir_dossier())
bouton_ouvrir.pack(side='left', padx=7)
bouton_effacer = RippleButton(row6, text="Effacer historique", command=lambda: effacer_historique())
bouton_effacer.pack(side='left', padx=7)
bouton_copier = RippleButton(row6, text="Copier m3u8", command=lambda: copier_m3u8())
bouton_copier.pack(side='left', padx=7)

# Historique dans une card sombre
hist_card = tk.Frame(body, bg=DARK_CARD, bd=0, highlightthickness=2, highlightbackground='#23272e')
hist_card.pack(fill='both', expand=True, pady=(12,0))
tk.Label(hist_card, text="🧾 Historique des téléchargements", bg=DARK_CARD, fg=DARK_ACCENT, font=("Segoe UI", 11, "bold")).pack(anchor='w', padx=8, pady=(8,0))

# Scrollbar custom
scroll = tk.Scrollbar(hist_card, bg=DARK_CARD, troughcolor=DARK_BG, highlightthickness=0, relief='flat')
text_historique = tk.Text(hist_card, height=8, width=70, bg=DARK_BG, fg=DARK_TEXT, font=("Consolas", 10), borderwidth=0, relief="flat", yscrollcommand=scroll.set, insertbackground=DARK_ACCENT)
text_historique.pack(padx=12, pady=10, fill='both', expand=True, side='left')
scroll.pack(side='right', fill='y')
text_historique.config(state="disabled")
scroll.config(command=text_historique.yview)

footer = tk.Frame(fenetre, bg=DARK_BG)
footer.pack(fill='x', pady=(0,10))
tk.Label(footer, text="Kick.com VOD Downloader • Modern UI", bg=DARK_BG, fg=DARK_SUBTLE, font=("Segoe UI", 9)).pack()

# --- Style ttk sombre ---
style = ttk.Style()
fenetre.tk_setPalette(background=DARK_BG, foreground=DARK_TEXT, activeBackground=DARK_CARD)
style.theme_use("clam")
style.configure("TLabel", background=DARK_BG, foreground=DARK_TEXT, font=("Segoe UI", 11))
style.configure("TButton", background=DARK_CARD, foreground=DARK_TEXT, font=("Segoe UI", 11, "bold"), borderwidth=0, focusthickness=2, focuscolor=DARK_ACCENT, relief="flat", padding=8)
style.map("TButton",
    background=[('active', DARK_ACCENT), ('!active', DARK_CARD)],
    foreground=[('active', '#fff'), ('!active', DARK_TEXT)]
)
style.configure("TEntry", fieldbackground=DARK_CARD, foreground=DARK_TEXT, borderwidth=2, relief="flat", font=("Segoe UI", 11), padding=6, insertcolor=DARK_ACCENT)
style.configure("TProgressbar", troughcolor=DARK_CARD, background=DARK_PROGRESS, bordercolor=DARK_BG, lightcolor=DARK_PROGRESS, darkcolor=DARK_CARD, thickness=16)

# --- Détection et blocage du mode live ---
def is_live_vod(url, m3u8_urls):
    # On considère qu'un flux live a 'live' dans son url ou que le m3u8 contient 'live' ou 'chunked'
    if 'live' in url.lower():
        return True
    for u in m3u8_urls:
        if 'live' in u.lower() or 'chunked' in u.lower():
            return True
    return False

# --- Pop-up de progression animée et détaillée ---
def show_progress_popup():
    popup = tk.Toplevel(fenetre)
    popup.title("Téléchargement en cours")
    popup.geometry("460x250")
    popup.resizable(False, False)
    popup.configure(bg=DARK_CARD if current_theme=="dark" else "#fff")
    popup.attributes('-topmost', True)
    popup.attributes('-alpha', 0.93)
    popup.lift()
    tk.Label(popup, text="Téléchargement en cours...", font=("Segoe UI", 14, "bold"), bg=popup['bg'], fg=DARK_ACCENT if current_theme=="dark" else "#4094f7").pack(pady=(18,7))
    bar = ttk.Progressbar(popup, length=340, mode="determinate")
    bar.pack(pady=6)
    percent = tk.Label(popup, text="0%", font=("Segoe UI", 12, "bold"), bg=popup['bg'], fg=DARK_TEXT if current_theme=="dark" else "#222")
    percent.pack()
    details = tk.Label(popup, text="Préparation...", font=("Segoe UI", 10), bg=popup['bg'], fg=DARK_SUBTLE if current_theme=="dark" else "#888")
    details.pack(pady=(8,0))
    stats = tk.Label(popup, text="", font=("Segoe UI", 10), bg=popup['bg'], fg=DARK_TEXT if current_theme=="dark" else "#222")
    stats.pack(pady=(4,0))
    btn_cancel = RippleButton(popup, text="Annuler", command=popup.destroy)
    btn_cancel.pack(pady=(11,0))
    # Animation d'apparition
    for i in range(0, 11):
        popup.attributes('-alpha', 0.83 + 0.01*i)
        popup.update()
        fenetre.after(8)
    # Effet pulse sur la barre
    def pulse():
        c = 0
        while True:
            color = f"#{int(64+32*abs((c%20-10)/10)):02x}94f7"
            style.configure("TProgressbar", background=color)
            bar.update()
            c += 1
            if not popup.winfo_exists(): break
            popup.after(50)
    threading.Thread(target=pulse, daemon=True).start()
    return popup, bar, percent, details, stats, btn_cancel

# --- Progressbar indeterminate lors de la recherche ---
def show_searching_progress():
    searching_popup = tk.Toplevel(fenetre)
    searching_popup.title("Recherche du flux vidéo")
    searching_popup.geometry("340x110")
    searching_popup.resizable(False, False)
    searching_popup.configure(bg=DARK_CARD if current_theme=="dark" else "#fff")
    searching_popup.attributes('-topmost', True)
    searching_popup.attributes('-alpha', 0.93)
    searching_popup.lift()
    tk.Label(searching_popup, text="Recherche du flux vidéo...", font=("Segoe UI", 12, "bold"), bg=searching_popup['bg'], fg=DARK_ACCENT if current_theme=="dark" else "#4094f7").pack(pady=(18,7))
    bar = ttk.Progressbar(searching_popup, length=250, mode="indeterminate")
    bar.pack(pady=10)
    bar.start(12)
    return searching_popup, bar

# --- Toast animé ---
def show_toast(msg, color=DARK_ACCENT, duration=2500):
    toast = tk.Toplevel(fenetre)
    toast.overrideredirect(True)
    toast.configure(bg=color)
    toast.attributes('-topmost', True)
    toast.geometry(f"320x44+{fenetre.winfo_x()+fenetre.winfo_width()//2-160}+{fenetre.winfo_y()+30}")
    toast.lift()
    label = tk.Label(toast, text=msg, font=("Segoe UI", 11, "bold"), bg=color, fg="#fff", padx=12, pady=8)
    label.pack(expand=True, fill="both")
    # Animation slide-in
    for y in range(30, 0, -2):
        toast.geometry(f"320x44+{fenetre.winfo_x()+fenetre.winfo_width()//2-160}+{fenetre.winfo_y()+y}")
        toast.update()
        fenetre.after(6)
    toast.after(duration, lambda: toast.destroy())

# --- Highlight historique ---
def ajouter_historique(texte):
    text_historique.config(state="normal")
    text_historique.insert("end", texte + "\n")
    text_historique.see("end")
    text_historique.tag_remove("highlight", 1.0, "end")
    text_historique.tag_add("highlight", "end-2l", "end-1l")
    text_historique.tag_config("highlight", background="#23272e", foreground=DARK_SUCCESS if current_theme=="dark" else LIGHT_SUCCESS)
    text_historique.config(state="disabled")
    save_history()

# --- Historique persistant ---
HIST_FILE = os.path.join(os.getcwd(), "historique.json")
def save_history():
    with open(HIST_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(text_historique.get(1.0, tk.END)))
def load_history():
    if os.path.exists(HIST_FILE):
        with open(HIST_FILE, "r", encoding="utf-8") as f:
            txt = json.loads(f.read())
            text_historique.config(state="normal")
            text_historique.delete(1.0, tk.END)
            text_historique.insert(1.0, txt)
            text_historique.config(state="disabled")
fenetre.after(200, load_history)

# --- Drag & drop URL ---
def drop_url(event):
    url = event.data.strip()
    if url.startswith("http"):
        entry_url.delete(0, tk.END)
        entry_url.insert(0, url)

if DND_AVAILABLE:
    fenetre.drop_target_register(DND_FILES)
    fenetre.dnd_bind('<<Drop>>', drop_url)
else:
    def show_dnd_warning():
        toast = tk.Toplevel(fenetre)
        toast.overrideredirect(True)
        toast.geometry(f"340x60+{fenetre.winfo_x()+60}+{fenetre.winfo_y()+60}")
        toast.configure(bg="#23272e")
        toast.attributes('-topmost', True)
        label = tk.Label(
            toast, text="Le drag & drop nécessite le module tkinterdnd2\n(pip install tkinterdnd2)",
            bg="#23272e", fg="#fff", font=("Segoe UI", 10, "bold"), wraplength=320, justify="left"
        )
        label.pack(fill='both', expand=True, padx=16, pady=14)
        for i in range(0, 11):
            toast.attributes('-alpha', 0.75 + 0.025*i)
            toast.update()
            time.sleep(0.01)
        toast.after(6000, toast.destroy)
    fenetre.after(1200, show_dnd_warning)

# --- Progression avancée avec stats, temps restant, vitesse moyenne ---
# ... Dans la boucle de progression du téléchargement ...
start_time = time.time()
last_size = 0
speeds = []
def update_progress_ffmpeg():
    global last_size, speeds
    while True:
        # Lire la taille du fichier temporaire
        if os.path.exists(sortie):
            size = os.path.getsize(sortie)
            elapsed = time.time() - start_time
            speed = (size - last_size) / 2 / 1024 / 1024  # Mo/s
            last_size = size
            speeds.append(speed)
            avg_speed = sum(speeds)/len(speeds) if speeds else 0
            percent_val = min(int(size / taille_totale * 100), 100) if taille_totale else 0
            bar['value'] = percent_val
            percent.config(text=f"{percent_val}%")
            if avg_speed > 0 and taille_totale:
                eta = int((taille_totale - size) / (avg_speed*1024*1024))
                stats.config(text=f"{size//1024//1024} Mo / {taille_totale//1024//1024} Mo  |  {speed:.2f} Mo/s (moy: {avg_speed:.2f})  |  ETA: {eta}s")
            else:
                stats.config(text=f"{size//1024//1024} Mo / {taille_totale//1024//1024} Mo  |  {speed:.2f} Mo/s")
            details.config(text="Téléchargement en cours...")
            popup.update_idletasks()
            if percent_val >= 100:
                break
        time.sleep(2)

# --- Notification sonore à la fin ---
def notify_done(success=True):
    if success:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    else:
        winsound.MessageBeep(winsound.MB_ICONHAND)

# --- Fonctions ---
def choisir_cookies():
    global cookies_path
    path = filedialog.askopenfilename(title="Sélectionner un fichier cookies.txt", filetypes=[("Cookies.txt", "*.txt"), ("Tous les fichiers", "*.*")])
    if path:
        cookies_path = path
        label_cookies.config(text=f"Cookie sélectionné : {os.path.basename(path)}")
        show_toast("Fichier cookies.txt sélectionné !", color="#1976d2")
    else:
        cookies_path = None
        label_cookies.config(text="Aucun cookie sélectionné")

def ouvrir_dossier():
    import webbrowser
    webbrowser.open(os.path.abspath(dossier_sortie))

def effacer_historique():
    text_historique.config(state="normal")
    text_historique.delete(1.0, tk.END)
    text_historique.config(state="disabled")
    show_toast("Historique effacé", color="#4caf50")

def copier_m3u8():
    if hasattr(fenetre, "last_m3u8") and fenetre.last_m3u8:
        fenetre.clipboard_clear()
        fenetre.clipboard_append(fenetre.last_m3u8)
        show_toast("Lien m3u8 copié !", color="#1976d2")
    else:
        show_toast("Aucun flux m3u8 à copier", color="#b71c1c")

def telecharger_playwright():
    url = entry_url.get().strip()
    nom = entry_nom.get().strip() or "video_kick"
    sortie = os.path.join(dossier_sortie, nom + ".mp4")
    if not url:
        show_toast("Erreur : URL manquante.", color="#b71c1c")
        return
    if not url.startswith("https://kick.com/"):
        show_toast("Erreur : L'URL n'est pas valide ou ne provient pas de Kick.com.", color="#b71c1c")
        return
    def run():
        bouton_dl_pw.config(state="disabled")
        modes = [(True, "headless+stealth"), (False, "VISIBLE+stealth")]
        found = False
        best_ua = None
        best_video_url = None
        best_all_urls = []
        best_m3u8_urls = []
        mode_utilise = None
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81"
        ]
        stealth_js = '''
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr', 'en'] });
window.chrome = { runtime: {} };
Object.defineProperty(window, 'screen', { get: () => ({ width:1280, height:720 }) });
'''
        for headless, mode_desc in modes:
            statut.set(f"Test UA (mode {mode_desc})...")
            ajouter_historique(f"Playwright (profil Zen, UA auto, {mode_desc}) → {url}")
            try:
                from playwright.sync_api import sync_playwright
                firefox_user_dir = r'C:\Users\Administrator\AppData\Roaming\zen\Profiles\70p3ihed.Default'
                for user_agent in user_agents:
                    statut.set(f"Test UA: {user_agent[:40]}... ({mode_desc})")
                    ajouter_historique(f"Test User-Agent: {user_agent}")
                    with sync_playwright() as p:
                        context = p.firefox.launch_persistent_context(
                            firefox_user_dir,
                            headless=headless,
                            user_agent=user_agent,
                            viewport={"width": 1280, "height": 720},
                            device_scale_factor=1.0
                        )
                        if cookies_path:
                            try:
                                with open(cookies_path, "r", encoding="utf-8") as f:
                                    cookies_txt = f.read()
                                # Conversion cookies.txt en liste de dicts Playwright
                                cookies = []
                                for line in cookies_txt.splitlines():
                                    if not line or line.startswith("#"): continue
                                    parts = line.split('\t')
                                    if len(parts) >= 7:
                                        cookies.append({
                                            "name": parts[5],
                                            "value": parts[6],
                                            "domain": parts[0],
                                            "path": parts[2],
                                            "expires": int(parts[4]) if parts[4].isdigit() else -1,
                                            "httpOnly": False,
                                            "secure": parts[3] == "TRUE"
                                        })
                                context.add_cookies(cookies)
                                ajouter_historique(f"Cookies injectés depuis {os.path.basename(cookies_path)} (prioritaire)")
                            except Exception as e:
                                ajouter_historique(f"Erreur injection cookies.txt : {e}")
                        page = context.new_page()
                        page.add_init_script(stealth_js)
                        m3u8_urls = []
                        all_urls = []
                        def handle_request(request):
                            all_urls.append(request.url)
                            if ".m3u8" in request.url:
                                m3u8_urls.append(request.url)
                        page.on("request", handle_request)
                        page.goto(url)
                        # --- Clic auto sur cookies ---
                        try:
                            page.wait_for_timeout(800)  # plus rapide
                            selectors = [
                                'button:has-text("Accepter")',
                                'button:has-text("Accept")',
                                'button[mode="primary"]',
                                '.cookie-accept',
                                '[data-testid="cookie-accept-all"]'
                            ]
                            clicked = False
                            for sel in selectors:
                                btn = page.query_selector(sel)
                                if btn:
                                    btn.click()
                                    ajouter_historique(f"→ Clic auto sur cookies avec sélecteur : {sel}")
                                    clicked = True
                                    break
                            if not clicked:
                                ajouter_historique("→ Aucun bouton cookies trouvé.")
                        except Exception as e:
                            ajouter_historique(f"Erreur clic cookies : {e}")
                        # --- Extraction automatique des cookies ---
                        try:
                            cookies = context.cookies()
                            ajouter_historique(f"→ Cookies extraits : {json.dumps(cookies, ensure_ascii=False)[:300]}...")
                        except Exception as e:
                            ajouter_historique(f"Erreur extraction cookies : {e}")
                        try:
                            page.wait_for_selector('video', timeout=8000)  # moins long
                        except Exception:
                            pass
                        try:
                            # 2 tentatives de clic/play max
                            for _ in range(2):
                                box = page.query_selector('video').bounding_box()
                                if box:
                                    page.mouse.move(box['x'] + box['width']//2, box['y'] + box['height']//2)
                                    page.mouse.click(box['x'] + box['width']//2, box['y'] + box['height']//2)
                                page.evaluate("document.querySelector('video').play()")
                                time.sleep(1)  # plus court
                        except Exception:
                            pass
                        time.sleep(4)  # attente réduite
                        context.close()
                        if m3u8_urls:
                            found = True
                            best_ua = user_agent
                            best_m3u8_urls = m3u8_urls
                            best_all_urls = all_urls
                            mode_utilise = mode_desc
                            break
                    if found:
                        break
            except Exception as e:
                ajouter_historique(f"Erreur Playwright ({mode_desc}): {e}")
        ajouter_historique("--- URLs réseau capturées ---")
        for u in best_all_urls:
            ajouter_historique(u)
        ajouter_historique("----------------------------")
        if not found:
            statut.set("❌ Flux vidéo introuvable avec tous les User-Agent et modes (headless/visible).")
            ajouter_historique("❌ Playwright : flux .m3u8 introuvable avec tous les UA et modes.")
            show_toast("Impossible de trouver le flux vidéo (.m3u8) avec tous les User-Agent testés en modes headless et visible. La vidéo est peut-être protégée ou le site a changé.", color="#b71c1c")
            bouton_dl_pw.config(state="normal")
            return
        if is_live_vod(url, best_m3u8_urls):
            statut.set("Erreur : Ce lien correspond à un live. Seules les VOD sont supportées.")
            ajouter_historique("Erreur : tentative de téléchargement d'un live, refusé.")
            bouton_dl_pw.config(state="normal")
            return
        # --- Choix de la qualité ---
        choix_url = None
        if len(best_m3u8_urls) == 1:
            choix_url = best_m3u8_urls[0]
        else:
            def extract_quality(u):
                m = re.search(r'(\d{3,4}p)', u)
                return m.group(1) if m else u[-30:]
            options = [f"{i+1}. {extract_quality(u)}" for i, u in enumerate(best_m3u8_urls)]
            choix = ask_quality_choice("Plusieurs flux trouvés. Entrez le numéro de la qualité désirée :", options)
            try:
                idx = int(choix.strip()) - 1
                choix_url = best_m3u8_urls[idx]
            except:
                statut.set("Annulé ou choix invalide.")
                bouton_dl_pw.config(state="normal")
                return
        try:
            playlist = m3u8.load(choix_url)
            if playlist.is_variant:
                qualities = []
                for i, pl in enumerate(playlist.playlists):
                    stream_info = pl.stream_info
                    res = f"{stream_info.resolution[1]}p" if stream_info.resolution else "?p"
                    bandwidth = stream_info.bandwidth
                    qualities.append(f"{i+1}. {res} ({bandwidth//1000}kbps)")
                choix = ask_quality_choice("Playlist master détectée. Entrez le numéro de la qualité :", qualities)
                try:
                    idx = int(choix.strip()) - 1
                    choix_url = playlist.playlists[idx].absolute_uri
                except:
                    statut.set("Annulé ou choix invalide.")
                    bouton_dl_pw.config(state="normal")
                    return
        except Exception as e:
            pass
        searching_popup, indet_bar = show_searching_progress()
        popup, bar, percent, details, stats, btn_cancel = show_progress_popup()
        statut.set(f"Téléchargement via ffmpeg... (UA choisi: {best_ua[:40]}..., mode {mode_utilise})")
        ajouter_historique(f"ffmpeg → {choix_url}")
        cmd = ["ffmpeg", "-y", "-i", choix_url, "-c", "copy", sortie]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        threading.Thread(target=update_progress_ffmpeg, daemon=True).start()
        for line in proc.stdout:
            if "out_time_ms=" in line:
                try:
                    percent_val = int(int(line.strip().split('=')[1]) / 60000000 * 100)
                    progress_var.set(min(percent_val, 100))
                except:
                    pass
        proc.wait()
        indet_bar.stop()
        searching_popup.destroy()
        popup.destroy()
        if proc.returncode == 0:
            statut.set(f"Téléchargement terminé ✅ (Playwright, mode {mode_utilise})")
            show_toast(f"Téléchargement terminé avec succès via Playwright ! (mode {mode_utilise})", color="#4caf50")
        else:
            statut.set(f"❌ Erreur ffmpeg (Playwright, mode {mode_utilise})")
            show_toast(f"Erreur lors du téléchargement avec ffmpeg (Playwright, mode {mode_utilise})", color="#b71c1c")
        bouton_dl_pw.config(state="normal")
        notify_done(proc.returncode == 0)
        show_thumbnail(choix_url)
    threading.Thread(target=run).start()

def ask_quality_choice(prompt, options):
    result = {}
    def ask():
        result['value'] = simpledialog.askstring("Qualité", prompt + "\n" + "\n".join(options), parent=fenetre)
    fenetre.after(0, ask)
    while 'value' not in result:
        fenetre.update()
        time.sleep(0.05)
    return result['value']

cookies_path = None

fenetre.mainloop()
