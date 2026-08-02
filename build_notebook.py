#!/usr/bin/env python3
"""Build the two-notebook Colab flow:
  1. flow_discovery.ipynb  → Playwright ile API endpoint yakala
  2. shorts_automation.ipynb → Üretim motoru
"""

import json

# ─── Read discovery engine ───────────────────────────────────────────────────
with open("flow_discovery.py", "r") as f:
    discovery_code = f.read()

discovery_lines = [line + "\n" for line in discovery_code.split("\n")]
if discovery_lines and discovery_lines[-1].strip() == "":
    discovery_lines[-1] = discovery_lines[-1].rstrip("\n")

# ─── Build flow_discovery.ipynb ──────────────────────────────────────────────
setup = [
    "# CELL 1 — Kurulum (Bir kez çalıştırın)\n",
    "!pip install -q playwright nest-asyncio playwright-stealth\n",
    "!playwright install chromium --with-deps\n",
    "print('✅ Playwright kuruldu')\n",
]

discovery_nb = {
    "cells": [
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": setup,
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": discovery_lines,
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# CELL 3 — Sonuçları Görüntüle (Bunu da çalıştırın)\n",
                "import os\n",
                "if os.path.exists('flow_best_endpoint.json'):\n",
                "    with open('flow_best_endpoint.json', 'r') as f:\n",
                "        print('\\n\\n' + '='*50)\n",
                "        print('LÜTFEN AŞAĞIDAKİ METNİ KOPYALAYIP BANA GÖNDERİN:')\n",
                "        print('='*50 + '\\n')\n",
                "        print(f.read())\n",
                "else:\n",
                "    print('Henüz endpoint bulunamadı. Lütfen 2. hücreyi tekrar çalıştırın.')\n"
            ]
        },
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.10.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 4,
}

with open("flow_discovery.ipynb", "w") as f:
    json.dump(discovery_nb, f, indent=1)
print("✅ flow_discovery.ipynb oluşturuldu")

# ─── Also rebuild main notebook ──────────────────────────────────────────────
with open("engine.py", "r") as f:
    raw = f.read()

engine_lines = [line + "\n" for line in raw.split("\n")]
if engine_lines and engine_lines[-1].strip() == "":
    engine_lines[-1] = engine_lines[-1].rstrip("\n")

setup_main = [
    "# CELL 1 — Kurulum\n",
    "!pip install -q faster-whisper edge-tts moviepy==1.0.3 Pillow -U google-generativeai\n",
    "!apt-get update -qq && apt-get install -y -qq imagemagick ffmpeg > /dev/null 2>&1\n",
    "!mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.bak 2>/dev/null; true\n",
    "!wget -qO Montserrat-Black.ttf https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Black.ttf\n",
    "print('✅ Kurulum tamamlandı!')\n",
]

main_nb = {
    "cells": [
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": setup_main,
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
        "language_info": {"name": "python", "version": "3.10.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 4,
}

with open("shorts_automation.ipynb", "w") as f:
    json.dump(main_nb, f, indent=1)
print("✅ shorts_automation.ipynb güncellendi")
