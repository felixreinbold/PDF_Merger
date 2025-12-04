🚀 Installation & Build der EXE

1. Python installieren

Falls Python noch nicht installiert ist:
👉 https://www.python.org/downloads/


2. Projekt herunterladen
Per Git:
git clone REPO_URL_HIER_EINFÜGEN

3. Abhängigkeiten installieren

Im Projektordner ausführen:

pip install -r requirements.txt
pip install pyinstaller

4. EXE lokal erstellen
pyinstaller pdf_merger.spec


Nach wenigen Sekunden befindet sich die fertige Anwendung hier:

dist/PDF_Merger/PDF_Merger.exe

▶ Anwendung starten

Doppelklicke:

dist/PDF_Merger/PDF_Merger.exe
