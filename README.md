# Kick.com VOD Downloader

Application moderne pour télécharger les VOD de Kick.com avec interface graphique animée, mode sombre/clair, historique persistant, drag & drop, miniature vidéo, et plus encore.

## Fonctionnalités principales
- Téléchargement de VOD Kick.com (pas de live)
- Interface graphique Windows 11 moderne (Tkinter custom)
- Barre de progression animée, stats avancées (taille, vitesse instantanée et moyenne, ETA)
- Historique persistant (restauré à chaque lancement)
- Drag & drop d’URL
- Miniature vidéo affichée automatiquement
- Switch dark/light instantané
- Notification sonore à la fin

## Installation

1. Installez Python 3.10+ et [ffmpeg](https://ffmpeg.org/download.html)
2. Installez les dépendances Python :
```
pip install -r requirements.txt
```
3. Lancez l’application :
```
python main.py
```

## Création d’un exécutable Windows

```
pyinstaller --noconfirm --onefile --windowed main.py
```
Le .exe sera dans `dist/`.

## Dépendances principales
- tkinter
- playwright
- m3u8
- Pillow
- ffmpeg-python

## Auteurs
- @Mizaruta

---

Pour toute suggestion ou bug, ouvrez une issue sur GitHub !
