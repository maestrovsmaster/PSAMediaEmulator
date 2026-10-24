#!/bin/bash
# Налаштовує ноутбук як Bluetooth-колонку (A2DP sink + AVRCP) для SmegEmulator.
# Запускати від звичайного користувача (НЕ через sudo) — пароль sudo спитає сам.
set -e
cd "$(dirname "$(readlink -f "$0")")"
DIR="$(pwd)"

echo "== 1/5 Пакети =="
sudo apt-get install -y bluez python3-pydbus python3-pyqt6 python3-gi libspa-0.2-bluetooth

echo "== 2/5 /etc/bluetooth/main.conf =="
sudo python3 bluetooth/patch_main_conf.py
sudo rfkill unblock bluetooth
sudo systemctl enable bluetooth
sudo systemctl restart bluetooth

echo "== 3/5 WirePlumber (тільки A2DP, без HFP) =="
mkdir -p ~/.config/wireplumber/bluetooth.lua.d
cp bluetooth/51-smeg-sink.lua ~/.config/wireplumber/bluetooth.lua.d/
systemctl --user restart wireplumber

echo "== 4/5 Агент спарювання (systemd --user) =="
mkdir -p ~/.config/systemd/user
sed "s|@AGENT@|$DIR/bluetooth/smeg_bt_agent.py|" bluetooth/smeg-bt-agent.service \
    > ~/.config/systemd/user/smeg-bt-agent.service
systemctl --user daemon-reload
systemctl --user enable --now smeg-bt-agent.service
systemctl --user restart smeg-bt-agent.service

echo "== 5/5 Перевірка =="
sleep 2
bluetoothctl show | grep -E 'Alias|Class|Powered|Discoverable:|Pairable:|Audio Sink|Remote Control'
echo
echo "Готово. На телефоні знайдіть пристрій 'SMEG' і підключіться."
echo "Емулятор: python3 main.py"
