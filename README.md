# PDF Merger

Ein einfaches Tool zum Zusammenführen von PDF-Dateien mit Drag & Drop Funktion.

## Voraussetzungen

- Windows 10/11
- Python 3.x installiert

## Installation

1. **Repository klonen**
   ```bash
   git clone <URL_ZUM_REPO>
   cd PDF_Merger
   ```

2. **Abhängigkeiten installieren**
   Nutzen Sie den Python Launcher (`py`), um sicherzustellen, dass die Pakete korrekt installiert werden:
   ```powershell
   py -m pip install -r requirements.txt
   ```

## Programm starten

Sie können das Python-Skript direkt starten:
```powershell
py pdf_merger.py
```

## Executable (.exe) erstellen

Um eine eigenständige `.exe` Datei zu erstellen, nutzen wir `PyInstaller`.

1. **Build starten**
   ```powershell
   py -m PyInstaller pdf_merger.spec
   ```

2. **Programm finden**
   Nach dem Build-Prozess finden Sie die ausführbare Datei unter:
   `dist/pdf_merger/pdf_merger.exe`

   Sie können diesen gesamten Ordner verschieben oder verteilen.

## Fehlerbehebung

- **"pip/python wird nicht erkannt"**: Verwenden Sie stattdessen `py` und `py -m pip`, wie in den Anweisungen oben beschrieben.
- **Icon in Taskleiste fehlt**: Das Programm setzt automatisch eine `AppUserModelID`, damit das Icon korrekt angezeigt wird. Starten Sie das Programm neu, falls es nicht sofort erscheint.
