# 🚀 Installation & Build der EXE

## 1️⃣ Python installieren

Falls Python noch nicht vorhanden ist:

👉 **https://www.python.org/downloads/**

> **Wichtig:** Während der Installation die Option  
> **"Add Python to PATH"** aktivieren.

## 2️⃣ Projekt herunterladen

Ordner in beliebigem Pfad erstellen. z.B. Desktop. in der Konsole öffnen und
Per Git:

```sh
git clone https://github.com/felixreinbold/PDF_Merger.git
```

ODER als ZIP herunterladen & entpacken.

## 3️⃣ Abhängigkeiten installieren

Im Projektordner (`PDF_Merger/`) folgendes ausführen:

```sh
pip install -r requirements.txt
pip install pyinstaller
```

> Diese Befehle installieren alle benötigten Bibliotheken  
> inklusive `tkinterdnd2` und `PyInstaller`.

## 4️⃣ EXE lokal erstellen

```sh
pyinstaller pdf_merger.spec
```

Nach wenigen Sekunden erscheint die fertige Anwendung hier:

```
dist/PDF_Merger/PDF_Merger.exe
```

# ▶ Anwendung starten

Doppelklicke die Datei:

```
dist/PDF_Merger/PDF_Merger.exe
```

Die Anwendung öffnet sich ohne Installation und ohne Administratorrechte.

