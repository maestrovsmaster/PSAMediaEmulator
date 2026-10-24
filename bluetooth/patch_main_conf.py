#!/usr/bin/env python3
# Прописує в /etc/bluetooth/main.conf налаштування "Bluetooth-колонки".
# Запускати через sudo. Перед зміною робить резервну копію main.conf.smeg.bak
import re
import shutil
import sys

CONF = sys.argv[1] if len(sys.argv) > 1 else "/etc/bluetooth/main.conf"

# Class 0x240414: сервіси Audio + Rendering, пристрій Audio/Video -> Loudspeaker
SETTINGS = {
    "Name": "SMEG",
    "Class": "0x240414",
    "DiscoverableTimeout": "0",
    "AlwaysPairable": "true",
    "PairableTimeout": "0",
}

with open(CONF) as f:
    text = f.read()

shutil.copy(CONF, CONF + ".smeg.bak")

for key, value in SETTINGS.items():
    line = f"{key} = {value}"
    pattern = re.compile(rf"^#?\s*{key}\s*=.*$", re.MULTILINE)
    if pattern.search(text):
        text = pattern.sub(line, text, count=1)
    else:
        text = text.replace("[General]\n", f"[General]\n{line}\n", 1)
    print(line)

with open(CONF, "w") as f:
    f.write(text)
