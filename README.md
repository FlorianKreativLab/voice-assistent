# VoiceAssistent 🎙️  
Deutschsprachiger Sprachassistent für Desktop (DE) · German Desktop Voice Assistant (EN)

---

# 🇩🇪 Deutsch

## Überblick

**VoiceAssistent** ist ein deutschsprachiger Sprachassistent für den Desktop.  
Er kombiniert:

- **Spracherkennung (STT)** mit [Vosk](https://alphacephei.com/vosk/) und den deutschen Modellen  
  `vosk-model-de-0.21` und `vosk-model-small-de-0.15`
- **Sprachausgabe (TTS)** mit [Piper](https://github.com/rhasspy/piper)
- eine **LLM-Schicht** (z. B. über Ollama in `src/llm/ollama_client.py`)
- Wake-Word-Erkennung, VAD, Mikrofonhandling und einfache Audio-Gates

> Dieses Projekt ist als **Lern- und Demoprojekt** gedacht und kann als Basis / Template
> für eigene Sprachassistenten verwendet werden.

Die Modelle selbst (Vosk, Piper) werden **nicht im Git-Repository mitgeliefert**, um die Größe klein zu halten.
Stattdessen beschreibt das Projekt, **wo** die Modelle herkommen und **wie** du sie lokal einbindest.

---

## Features

- 🗣️ **Offline-Spracherkennung (STT)**  
  - Vosk-Modelle für Deutsch (`vosk-model-de-0.21`, `vosk-model-small-de-0.15`)  
  - verschiedene Betriebsmodi (z. B. Inline-Erkennung, Offlinemodi)
- 🔊 **Natürliche Sprachausgabe (TTS)**  
  - Piper TTS über `src/speech/tts/engine.py`
  - auswählbare Stimmen (siehe `piper_voices.py`)
- 🤖 **LLM-Integration**  
  - Chat-Backend über `src/llm/ollama_client.py`
  - optionaler Chat-Speicher in `src/llm/memory.py`
- 👂 **Wake-Word & VAD**  
  - Wake-Word-Detection in `src/speech/wake/detector.py`
  - Voice-Activity-Detection & Aufnahme-Logik in `src/speech/stt`
- 🎛️ **CLI-Tools** (siehe `src/cli/`)  
  - `talk_chat_entry.py` → Einstiegspunkt für den interaktiven Voice-Chat  
  - `listen.py`, `listen_offline.py`, `listen_offline_commands.py` → verschiedene Hör-/Erkennungs-Modi  
  - Utility-Tools wie `list_mics.py`, `test_voices.py`, `mic_level.py`, `gate_test.py`, `say.py` etc.
- 🧱 **Modulare Architektur**  
  - getrennte Bereiche für **LLM**, **Speech**, **Audio** und **CLI** in `src/`  
  - gut geeignet als **Template** für eigene Assistenz-Systeme

---

## Projektstruktur

Grober Überblick über die wichtigsten Teile:

```text
src/
├── llm/          # LLM-Backend (z. B. Ollama-Client, Chat-Speicher)
├── speech/       # STT, TTS, Wake-Word
│   ├── stt/      # Spracherkennung (Vosk, VAD, Config)
│   ├── tts/      # Piper TTS (Engine, Voices)
│   └── wake/     # Wake-Word-Detection
├── audio/        # Audio-Gates, Lautstärke-Logik
└── cli/          # CLI-Entry-Points & Tools (talk_chat, listen, etc.)
```

Die eigentliche Einstiegspunkt-Datei für den Voice-Chat ist:

```text
src/cli/talk_chat_entry.py
```

Sie ruft intern `talk_chat.main()` auf und verbindet STT, TTS und LLM zu einer durchgängigen Konversation.

---

## Voraussetzungen

- Python 3.10+  
- Ein installiertes **Vosk**-Deutsches Modell  
  - z. B. `vosk-model-de-0.21` oder `vosk-model-small-de-0.15`
- Installierte **Piper**-Modelle (deutsche Stimme, z. B. „kerstin-low“)  
- (Optional) **Ollama** oder anderes LLM-Backend, das in `src/llm/ollama_client.py` konfiguriert ist
- Ein funktionierendes **Mikrofon**

> Wichtig: Die Modell-Dateien (Vosk / Piper) gehören **nicht ins Git-Repo**, sondern werden lokal installiert
> und über Pfade/Configs angebunden.

---

## Installation

1. Repository klonen:

```bash
git clone https://github.com/<DEIN_USER>/voice-assistent.git
cd voice-assistent
```

2. Virtuelle Umgebung & Dependencies installieren:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. Vosk-Modelle herunterladen und lokal ablegen  
   (z. B. in einem Ordner `models/vosk/de/` – Pfad entsprechend in deiner Config bzw. im Code anpassen)

4. Piper-Modelle (deutsche Stimmen) herunterladen und konfigurieren  
   (z. B. in `models/piper/` – Konfiguration in `src/speech/tts/piper_voices.py`)

---

## Nutzung

### 1. Voice-Chat starten

Vom Projekt-Root aus (mit aktivierter venv):

```bash
python -m src.cli.talk_chat_entry
```

Der Assistent:

- wartet auf das Wake-Word (über `listen_for_wake`)  
- nimmt Sprache auf  
- transkribiert sie mit Vosk  
- beantwortet über das LLM  
- spricht die Antwort mit Piper

### 2. Hilfstools

Einige nützliche CLI-Skripte in `src/cli/`:

```bash
python -m src.cli.list_mics          # verfügbare Mikrofone listen
python -m src.cli.test_voices        # TTS-Stimmen testen
python -m src.cli.mic_level          # Mikrofon-Pegel anzeigen
python -m src.cli.say "Hallo Welt"   # Text direkt sprechen
```

(Die tatsächlichen Kommandos können je nach Umgebung leicht variieren – siehe Quellcode in `src/cli/`.)

---

## (Optional) Shell-Aliase

Um die wichtigsten Kommandos schneller auszuführen, können z. B. folgende Aliase verwendet werden:

```bash
alias va-chat='python -m src.cli.talk_chat_entry'
alias va-mics='python -m src.cli.list_mics'
alias va-voices='python -m src.cli.test_voices'
alias va-say='python -m src.cli.say'
```

---

## Clean Code / Template-Charakter

Dieses Repository ist als **„Clean Code“-Projekt** gedacht, das gleichzeitig als
**Template** für eigene Sprachassistenten dienen kann:

- klare Trennung von **STT**, **TTS**, **LLM**, **Wake-Word** und **CLI**
- keine Modelle im Repository – ideal für GitHub & Bewerbungen
- README erklärt, wie man Modelle nachlädt und konfiguriert

---

## Disclaimer

Dieses Projekt ist ein **Lern- und Demonstrationsprojekt**.  
Es ist nicht dafür gedacht, sicherheitskritische oder produktive Umgebungen direkt zu betreiben.

---

# 🇬🇧 English

## Overview

**VoiceAssistent** is a German-speaking desktop voice assistant.  
It combines:

- **Speech-to-Text (STT)** using [Vosk](https://alphacephei.com/vosk/) with German models  
  `vosk-model-de-0.21` and `vosk-model-small-de-0.15`
- **Text-to-Speech (TTS)** using [Piper](https://github.com/rhasspy/piper)
- an **LLM backend** (e.g. via Ollama in `src/llm/ollama_client.py`)
- wake-word detection, VAD, microphone handling and simple audio gates

> This project is intended as a **learning and demonstration project** and can be used as a
> **template** for your own voice assistant setups.

The model files (Vosk, Piper) are **not part of the Git repository**, in order to keep the repo small and portable.
The README describes **where to obtain the models** and **how to plug them in locally**.

---

## Features

- 🗣️ **Offline speech recognition (STT)**  
  - German Vosk models (`vosk-model-de-0.21`, `vosk-model-small-de-0.15`)  
  - different recognition modes (inline, offline, command modes)
- 🔊 **Natural speech output (TTS)**  
  - Piper TTS via `src/speech/tts/engine.py`  
  - configurable voices (see `piper_voices.py`)
- 🤖 **LLM integration**  
  - chat backend implemented in `src/llm/ollama_client.py`  
  - optional conversational memory in `src/llm/memory.py`
- 👂 **Wake-word & VAD**  
  - wake-word detection in `src/speech/wake/detector.py`  
  - voice activity detection & recording logic in `src/speech/stt`
- 🎛️ **CLI tools** (see `src/cli/`)  
  - `talk_chat_entry.py` → main entry point for interactive voice chat  
  - `listen.py`, `listen_offline.py`, `listen_offline_commands.py` → various listening / recognition modes  
  - helper tools like `list_mics.py`, `test_voices.py`, `mic_level.py`, `gate_test.py`, `say.py` etc.
- 🧱 **Modular architecture**  
  - separate domains for **LLM**, **speech**, **audio**, and **CLI** in `src/`  
  - well suited as a **template** for custom assistant systems

---

## Project structure

High-level structure:

```text
src/
├── llm/          # LLM backend (e.g. Ollama client, chat memory)
├── speech/       # STT, TTS, wake word
│   ├── stt/      # speech recognition (Vosk, VAD, config)
│   ├── tts/      # Piper TTS (engine, voices)
│   └── wake/     # wake-word detection
├── audio/        # audio gates, level logic
└── cli/          # CLI entry points & tools (talk_chat, listen, etc.)
```

Main entry point for the voice chat:

```text
src/cli/talk_chat_entry.py
```

It calls `talk_chat.main()` internally and glues together STT, TTS, and LLM into a conversational loop.

---

## Requirements

- Python 3.10+  
- Installed **Vosk** German model(s)  
  - e.g. `vosk-model-de-0.21` or `vosk-model-small-de-0.15`
- Installed **Piper** voice models (e.g. German voice like „kerstin-low“)  
- (Optional) **Ollama** or another configured LLM backend in `src/llm/ollama_client.py`
- A working **microphone**

> Note: Model files (Vosk / Piper) should **not be committed to Git**, but installed locally
> and referenced via config or environment variables.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/<YOUR_USER>/voice-assistent.git
cd voice-assistent
```

2. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. Download Vosk German models and place them locally  
   (for example into `models/vosk/de/` and adjust the path/config accordingly).

4. Download Piper voice models and configure them  
   (for example into `models/piper/` and wire up in `src/speech/tts/piper_voices.py`).

---

## Usage

### 1. Start voice chat

From the project root (with virtualenv active):

```bash
python -m src.cli.talk_chat_entry
```

The assistant will:

- wait for a wake word  
- record user speech  
- transcribe via Vosk  
- answer through the LLM  
- speak the answer using Piper  

### 2. Helper tools

Useful CLI scripts in `src/cli/`:

```bash
python -m src.cli.list_mics
python -m src.cli.test_voices
python -m src.cli.mic_level
python -m src.cli.say "Hello world"
```

(See the source code in `src/cli/` for all available tools and options.)

---

## (Optional) Shell aliases

Some example aliases for convenience:

```bash
alias va-chat='python -m src.cli.talk_chat_entry'
alias va-mics='python -m src.cli.list_mics'
alias va-voices='python -m src.cli.test_voices'
alias va-say='python -m src.cli.say'
```

---

## Clean code / template nature

This repository is designed as a **clean code project** that also serves as a
**template** for building your own voice assistants:

- clear separation of **STT**, **TTS**, **LLM**, **wake word**, and **CLI**
- no models in the repository → ideal for GitHub and for use in applications / portfolios
- README explains how to obtain and plug in models

---

## Disclaimer

This project is a **learning and demonstration tool**.  
It is not intended for production use or security-critical applications.
