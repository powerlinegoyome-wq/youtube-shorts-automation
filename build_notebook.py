#!/usr/bin/env python3
"""Build the Colab notebook from engine.py.

Reads engine.py (plain Python) and packages it into a Jupyter
notebook with two cells:
  Cell 1 — Setup (pip, apt, ImageMagick fix)
  Cell 2 — Engine code
"""

import json

# ------------------------------------------------------------------
# Cell 1: Setup
# ------------------------------------------------------------------
setup_lines = [
    "# Cell 1 — Kurulum (ilk kez çalıştırın)\n",
    "!pip install -q faster-whisper edge-tts moviepy==1.0.3 Pillow -U google-generativeai\n",
    "!apt-get update -qq && apt-get install -y -qq imagemagick ffmpeg > /dev/null 2>&1\n",
    "!mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.bak 2>/dev/null; true\n",
    "!wget -qO Montserrat-Black.ttf https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Black.ttf\n",
    "print('✅ Kurulum tamamlandı!')",
]

# ------------------------------------------------------------------
# Cell 2: Engine (read from engine.py)
# ------------------------------------------------------------------
with open("engine.py", "r") as f:
    raw = f.read()

# Convert to notebook source lines (each line must end with \n
# except possibly the last one)
engine_lines = []
for line in raw.split("\n"):
    engine_lines.append(line + "\n")
# Remove trailing empty newline if present
if engine_lines and engine_lines[-1].strip() == "":
    engine_lines[-1] = engine_lines[-1].rstrip("\n")

# ------------------------------------------------------------------
# Assemble notebook
# ------------------------------------------------------------------
notebook = {
    "cells": [
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": setup_lines,
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": engine_lines,
        },
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.10.12",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 4,
}

with open("shorts_automation.ipynb", "w") as f:
    json.dump(notebook, f, indent=1)

print("✅ shorts_automation.ipynb oluşturuldu")
