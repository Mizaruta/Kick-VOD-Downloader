# Kick.com VOD Downloader

Téléchargez facilement les VOD de Kick.com grâce à une application moderne, rapide et intuitive.

---

## 🚀 Installation rapide

1. **Installez Python 3.10+** et [ffmpeg](https://ffmpeg.org/download.html)
2. **Installez les dépendances** :
   ```sh
   pip install -r requirements.txt
   ```
   (Ou cliquez sur le bouton "Copier la commande" si un toast l'affiche au démarrage)
3. **Lancez l’application** :
   ```sh
   python main.py
   ```

---

## 🎯 Fonctionnalités principales
- Téléchargement de VOD Kick.com (pas de live)
- Interface graphique moderne (mode sombre/clair)
- Barre de progression animée avec stats détaillées (taille, vitesse, ETA)
- Drag & drop d’URL natif (aucune configuration requise)
- Historique persistant
- Miniature vidéo automatique
- Notification sonore à la fin
- Détection automatique des dépendances manquantes avec aide interactive
- Compatible Windows, Mac et Linux

---

## 🛠️ Création d’un exécutable Windows

Pour générer un .exe portable :
```sh
pyinstaller --noconfirm --onefile --windowed main.py
```
Le fichier sera dans `dist/`.

---

## 📦 Dépendances
- `playwright`
- `m3u8`
- `Pillow`
- `ffmpeg-python`
- `tkinterdnd2` (drag & drop natif)
- `tkinter` (inclus dans Python standard sous Windows)

---

## 🙋‍♂️ Aide & Support
Pour toute suggestion ou bug, ouvrez une issue sur GitHub !

## 👤 Auteur
- @Mizaruta
