# PSA Media Emulator — Citroën C4 Picasso SMEG

**[English](#english)** · **[Українська](#українська)**

---

## English

A PyQt6 emulator of the SMEG media system screen (Citroën C4 Picasso). The laptop acts as a
Bluetooth speaker: a phone connects to the **SMEG** device and streams music (A2DP), while the
emulator shows the artist, album and track title and controls playback (AVRCP).

### Hardware

- A USB Bluetooth dongle with a Realtek **RTL8761BU** chip (here a TP-Link UB500, `2357:0604`).
  The `btusb` driver and the `rtl_bt/rtl8761bu_fw.bin` firmware ship with Ubuntu 24.04; nothing to install.
- Linux with BlueZ 5.7x and PipeWire + WirePlumber 0.4 (Ubuntu 24.04).

### How it works

| Component | Role |
|---|---|
| `bluetoothd` (BlueZ) | Bluetooth stack; exposes the phone's track and buttons as `org.bluez.MediaPlayer1` |
| PipeWire + WirePlumber | receives A2DP audio from the phone and plays it through the speakers |
| `bluetooth/smeg_bt_agent.py` | agent: keeps the adapter discoverable as "SMEG" and accepts pairing without confirmation |
| `smeg_final.py` | emulator GUI: reads `MediaPlayer1` over D-Bus, ⏮ ▶ ⏭ buttons |

### Installation (once)

```bash
cd ~/Documents/PSAMediaEmulator
./setup.sh
```

Run it as a regular user, **not** with `sudo`: the script asks for the sudo password itself.
What `setup.sh` does:

1. Installs `bluez python3-pydbus python3-pyqt6 python3-gi libspa-0.2-bluetooth`.
2. Writes to `/etc/bluetooth/main.conf` (a backup is saved as `main.conf.smeg.bak`):
   ```ini
   Name = SMEG
   Class = 0x240414          # Audio/Video → Loudspeaker, the phone shows a speaker icon
   DiscoverableTimeout = 0   # always discoverable
   AlwaysPairable = true
   PairableTimeout = 0
   ```
   Then runs `rfkill unblock bluetooth` and restarts `bluetooth`.
3. Copies `bluetooth/51-smeg-sink.lua` to `~/.config/wireplumber/bluetooth.lua.d/`.
   This file keeps only the A2DP roles, without HFP/HSP, so the phone doesn't route calls through the laptop.
   Then restarts WirePlumber.
4. Installs and enables the `smeg-bt-agent.service` user service, which starts with the session.

### Python environment (PyCharm / `.venv`)

PyQt6 and pydbus are installed as system packages (`apt`): `pydbus` needs `gi` (PyGObject),
which would have to be compiled to install it into a venv with `pip`. So the venv must see system packages.

If PyCharm created `.venv` and you get `ModuleNotFoundError: No module named 'PyQt6'`:

```bash
sed -i 's/^include-system-site-packages = false/include-system-site-packages = true/' .venv/pyvenv.cfg
```

Or create the venv correctly from the start:

```bash
python3 -m venv --system-site-packages .venv
```

Check:

```bash
.venv/bin/python -c "from PyQt6.QtWidgets import QApplication; import pydbus, gi; print('ok')"
```

Then in PyCharm: File → Invalidate Caches / Restart to clear the red underlines.

### Daily use

1. Plug the dongle into USB. The agent powers on and configures the adapter by itself.
2. On the phone: Bluetooth → **SMEG** → connect. No code confirmation needed.
3. Start the emulator:
   ```bash
   python3 main.py
   ```
   or build a binary with `./build.sh`; it will appear in `dist/SmegEmulator`.
4. Controls: on-screen buttons or the ← / Space / → keys.

### Manual dongle control

```bash
# Does the system see the dongle
lsusb | grep -i -E 'bluetooth|realtek|2357'
sudo dmesg | grep -i -E 'rtl|btusb|hci0'      # should show "RTL: fw version ..."
hciconfig -a                                   # hci0 UP RUNNING, Manufacturer: Realtek

# Unblock and start
sudo rfkill unblock bluetooth
sudo systemctl restart bluetooth

# Turn on the speaker manually (without the agent)
bluetoothctl power on
bluetoothctl system-alias SMEG
bluetoothctl discoverable-timeout 0
bluetoothctl discoverable on
bluetoothctl pairable on

# Adapter state (Alias, Class, Discoverable, UUID Audio Sink / A/V Remote Control)
bluetoothctl show
```

#### Agent

```bash
systemctl --user status smeg-bt-agent       # status
journalctl --user -u smeg-bt-agent -f       # live pairing log
systemctl --user restart smeg-bt-agent      # restart
systemctl --user disable --now smeg-bt-agent   # disable autostart
```

#### Devices

```bash
bluetoothctl devices Paired
bluetoothctl info XX:XX:XX:XX:XX:XX        # Connected / Trusted / UUID
bluetoothctl remove XX:XX:XX:XX:XX:XX      # forget the phone (pair from scratch)
```

#### Audio and AVRCP

```bash
wpctl status                               # Sources/Streams should list bluez_input.XX_XX_...
pactl list short sources | grep bluez

# Track metadata straight from BlueZ (the same way the emulator reads it)
busctl tree org.bluez | grep player
dbus-send --system --print-reply --dest=org.bluez \
  /org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX/player0 \
  org.freedesktop.DBus.Properties.Get string:org.bluez.MediaPlayer1 string:Track
```

### Troubleshooting

| Symptom | What to do |
|---|---|
| `hciconfig` is empty | re-plug the dongle and check `sudo dmesg \| tail`; make sure the built-in BT isn't taking `hci0` (`bluetoothctl list`) |
| The phone doesn't see SMEG | `bluetoothctl show` must say `Discoverable: yes`; `systemctl --user restart smeg-bt-agent` |
| Connected but no sound | `wpctl status`; `systemctl --user restart wireplumber`; on the phone, check that "Media audio" is enabled for SMEG |
| Sound plays but the screen says «ШУКАЮ ТЕЛЕФОН...» ("searching for phone") | start a music player on the phone: `MediaPlayer1` only appears while a player is active |
| Pairing fails after reinstalling | `bluetoothctl remove <MAC>` on the laptop and "Forget device" on the phone |
| Restore main.conf | `sudo cp /etc/bluetooth/main.conf.smeg.bak /etc/bluetooth/main.conf && sudo systemctl restart bluetooth` |

### Files

```
main.py                         GUI entry point
smeg_final.py                   SMEG screen emulator
setup.sh                        Bluetooth speaker setup
bluetooth/smeg_bt_agent.py      pairing + discoverability agent
bluetooth/smeg-bt-agent.service systemd --user service template
bluetooth/51-smeg-sink.lua      WirePlumber config
bluetooth/patch_main_conf.py    edits /etc/bluetooth/main.conf
build.sh, *.spec, hooks/        PyInstaller build
```

---

## Українська

Емулятор екрана медіасистеми SMEG (Citroën C4 Picasso) на PyQt6. Ноутбук працює як
Bluetooth-колонка: телефон підключається до пристрою **SMEG** і стрімить музику (A2DP),
а емулятор показує виконавця, альбом і назву треку та керує відтворенням (AVRCP).

### Залізо

- USB Bluetooth-свисток на чипі Realtek **RTL8761BU** (у нашому випадку TP-Link UB500, `2357:0604`).
  Драйвер `btusb` і прошивка `rtl_bt/rtl8761bu_fw.bin` уже є в Ubuntu 24.04, ставити нічого не треба.
- Linux з BlueZ 5.7x і PipeWire + WirePlumber 0.4 (Ubuntu 24.04).

### Як це працює

| Компонент | Роль |
|---|---|
| `bluetoothd` (BlueZ) | Bluetooth-стек; експортує трек і кнопки телефона як `org.bluez.MediaPlayer1` |
| PipeWire + WirePlumber | приймає A2DP-аудіо від телефона й відтворює його через динаміки |
| `bluetooth/smeg_bt_agent.py` | агент: тримає адаптер видимим як «SMEG» і приймає спарювання без підтвердження |
| `smeg_final.py` | GUI емулятора: читає `MediaPlayer1` через D-Bus, кнопки ⏮ ▶ ⏭ |

### Встановлення (один раз)

```bash
cd ~/Documents/PSAMediaEmulator
./setup.sh
```

Запускайте від звичайного користувача, **не** через `sudo`: пароль sudo скрипт попросить сам.
Що робить `setup.sh`:

1. Ставить пакети `bluez python3-pydbus python3-pyqt6 python3-gi libspa-0.2-bluetooth`.
2. Прописує в `/etc/bluetooth/main.conf` (резервна копія лежить у `main.conf.smeg.bak`):
   ```ini
   Name = SMEG
   Class = 0x240414          # Audio/Video → Loudspeaker, телефон бачить іконку колонки
   DiscoverableTimeout = 0   # видимий завжди
   AlwaysPairable = true
   PairableTimeout = 0
   ```
   Потім виконує `rfkill unblock bluetooth` і перезапускає `bluetooth`.
3. Копіює `bluetooth/51-smeg-sink.lua` у `~/.config/wireplumber/bluetooth.lua.d/`.
   Цей файл залишає тільки ролі A2DP, без HFP/HSP, щоб телефон не вів через ноутбук дзвінки.
   Після цього перезапускає WirePlumber.
4. Ставить і вмикає user-службу `smeg-bt-agent.service`, яка стартує разом із сесією.

### Python-середовище (PyCharm / `.venv`)

PyQt6 і pydbus ставляться системними пакетами (`apt`): `pydbus` потребує `gi` (PyGObject),
який через `pip` у venv треба компілювати. Тому venv має бачити системні пакети.

Якщо PyCharm створив `.venv` і видає `ModuleNotFoundError: No module named 'PyQt6'`:

```bash
sed -i 's/^include-system-site-packages = false/include-system-site-packages = true/' .venv/pyvenv.cfg
```

Або створіть venv одразу правильно:

```bash
python3 -m venv --system-site-packages .venv
```

Перевірка:

```bash
.venv/bin/python -c "from PyQt6.QtWidgets import QApplication; import pydbus, gi; print('ok')"
```

Після цього в PyCharm: File → Invalidate Caches / Restart, щоб зникли червоні підкреслення.

### Щоденне використання

1. Вставте свисток у USB. Агент сам увімкне й налаштує адаптер.
2. На телефоні: Bluetooth → **SMEG** → підключитися. Код підтверджувати не треба.
3. Запустіть емулятор:
   ```bash
   python3 main.py
   ```
   або зберіть бінарник за допомогою `./build.sh`, тоді він з'явиться в `dist/SmegEmulator`.
4. Керування: кнопки на екрані або клавіші ← / Space / →.

### Ручне керування свистком

```bash
# Чи бачить система свисток
lsusb | grep -i -E 'bluetooth|realtek|2357'
sudo dmesg | grep -i -E 'rtl|btusb|hci0'      # має бути "RTL: fw version ..."
hciconfig -a                                   # hci0 UP RUNNING, Manufacturer: Realtek

# Розблокувати та запустити
sudo rfkill unblock bluetooth
sudo systemctl restart bluetooth

# Увімкнути колонку вручну (без агента)
bluetoothctl power on
bluetoothctl system-alias SMEG
bluetoothctl discoverable-timeout 0
bluetoothctl discoverable on
bluetoothctl pairable on

# Стан адаптера (Alias, Class, Discoverable, UUID Audio Sink / A/V Remote Control)
bluetoothctl show
```

#### Агент

```bash
systemctl --user status smeg-bt-agent       # стан
journalctl --user -u smeg-bt-agent -f       # лог спарювань наживо
systemctl --user restart smeg-bt-agent      # перезапуск
systemctl --user disable --now smeg-bt-agent   # вимкнути автозапуск
```

#### Пристрої

```bash
bluetoothctl devices Paired
bluetoothctl info XX:XX:XX:XX:XX:XX        # Connected / Trusted / UUID
bluetoothctl remove XX:XX:XX:XX:XX:XX      # забути телефон (спарювання з нуля)
```

#### Аудіо та AVRCP

```bash
wpctl status                               # у Sources/Streams має бути bluez_input.XX_XX_...
pactl list short sources | grep bluez

# Метадані треку напряму з BlueZ (так само їх читає емулятор)
busctl tree org.bluez | grep player
dbus-send --system --print-reply --dest=org.bluez \
  /org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX/player0 \
  org.freedesktop.DBus.Properties.Get string:org.bluez.MediaPlayer1 string:Track
```

### Якщо щось не працює

| Симптом | Що зробити |
|---|---|
| `hciconfig` порожній | перевставити свисток і подивитися `sudo dmesg \| tail`; перевірити, що вбудований BT не забирає `hci0` (`bluetoothctl list`) |
| Телефон не бачить SMEG | `bluetoothctl show`: має бути `Discoverable: yes`; `systemctl --user restart smeg-bt-agent` |
| Підключився, але звуку немає | `wpctl status`; `systemctl --user restart wireplumber`; на телефоні перевірити, що для SMEG увімкнено «Медіа-аудіо» |
| Звук є, а на екрані «ШУКАЮ ТЕЛЕФОН...» | запустити музичний плеєр на телефоні: `MediaPlayer1` з'являється тільки разом з активним плеєром |
| Помилка спарювання після перевстановлення | `bluetoothctl remove <MAC>` на ноутбуці й «Забути пристрій» на телефоні |
| Повернути main.conf | `sudo cp /etc/bluetooth/main.conf.smeg.bak /etc/bluetooth/main.conf && sudo systemctl restart bluetooth` |

### Файли

```
main.py                         точка входу GUI
smeg_final.py                   емулятор екрана SMEG
setup.sh                        налаштування Bluetooth-колонки
bluetooth/smeg_bt_agent.py      агент спарювання + видимість
bluetooth/smeg-bt-agent.service шаблон systemd --user служби
bluetooth/51-smeg-sink.lua      конфіг WirePlumber
bluetooth/patch_main_conf.py    правка /etc/bluetooth/main.conf
build.sh, *.spec, hooks/        збірка PyInstaller
```
