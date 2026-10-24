# PSA Media Emulator — Citroën C4 Picasso SMEG

Емулятор екрана медіасистеми SMEG (Citroën C4 Picasso) на PyQt6. Ноутбук працює як
Bluetooth-колонка: телефон підключається до пристрою **SMEG** і стрімить музику (A2DP),
а емулятор показує виконавця, альбом і назву треку та керує відтворенням (AVRCP).

## Залізо

- USB Bluetooth-свисток на чипі Realtek **RTL8761BU** (у нашому випадку TP-Link UB500, `2357:0604`).
  Драйвер `btusb` і прошивка `rtl_bt/rtl8761bu_fw.bin` уже є в Ubuntu 24.04, ставити нічого не треба.
- Linux з BlueZ 5.7x і PipeWire + WirePlumber 0.4 (Ubuntu 24.04).

## Як це працює

| Компонент | Роль |
|---|---|
| `bluetoothd` (BlueZ) | Bluetooth-стек; експортує трек і кнопки телефона як `org.bluez.MediaPlayer1` |
| PipeWire + WirePlumber | приймає A2DP-аудіо від телефона й відтворює його через динаміки |
| `bluetooth/smeg_bt_agent.py` | агент: тримає адаптер видимим як «SMEG» і приймає спарювання без підтвердження |
| `smeg_final.py` | GUI емулятора: читає `MediaPlayer1` через D-Bus, кнопки ⏮ ▶ ⏭ |

## Встановлення (один раз)

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

## Щоденне використання

1. Вставте свисток у USB. Агент сам увімкне й налаштує адаптер.
2. На телефоні: Bluetooth → **SMEG** → підключитися. Код підтверджувати не треба.
3. Запустіть емулятор:
   ```bash
   python3 main.py
   ```
   або зберіть бінарник за допомогою `./build.sh`, тоді він з'явиться в `dist/SmegEmulator`.
4. Керування: кнопки на екрані або клавіші ← / Space / →.

## Ручне керування свистком

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

### Агент

```bash
systemctl --user status smeg-bt-agent       # стан
journalctl --user -u smeg-bt-agent -f       # лог спарювань наживо
systemctl --user restart smeg-bt-agent      # перезапуск
systemctl --user disable --now smeg-bt-agent   # вимкнути автозапуск
```

### Пристрої

```bash
bluetoothctl devices Paired
bluetoothctl info XX:XX:XX:XX:XX:XX        # Connected / Trusted / UUID
bluetoothctl remove XX:XX:XX:XX:XX:XX      # забути телефон (спарювання з нуля)
```

### Аудіо та AVRCP

```bash
wpctl status                               # у Sources/Streams має бути bluez_input.XX_XX_...
pactl list short sources | grep bluez

# Метадані треку напряму з BlueZ (так само їх читає емулятор)
busctl tree org.bluez | grep player
dbus-send --system --print-reply --dest=org.bluez \
  /org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX/player0 \
  org.freedesktop.DBus.Properties.Get string:org.bluez.MediaPlayer1 string:Track
```

## Якщо щось не працює

| Симптом | Що зробити |
|---|---|
| `hciconfig` порожній | перевставити свисток і подивитися `sudo dmesg \| tail`; перевірити, що вбудований BT не забирає `hci0` (`bluetoothctl list`) |
| Телефон не бачить SMEG | `bluetoothctl show`: має бути `Discoverable: yes`; `systemctl --user restart smeg-bt-agent` |
| Підключився, але звуку немає | `wpctl status`; `systemctl --user restart wireplumber`; на телефоні перевірити, що для SMEG увімкнено «Медіа-аудіо» |
| Звук є, а на екрані «ШУКАЮ ТЕЛЕФОН...» | запустити музичний плеєр на телефоні: `MediaPlayer1` з'являється тільки разом з активним плеєром |
| Помилка спарювання після перевстановлення | `bluetoothctl remove <MAC>` на ноутбуці й «Забути пристрій» на телефоні |
| Повернути main.conf | `sudo cp /etc/bluetooth/main.conf.smeg.bak /etc/bluetooth/main.conf && sudo systemctl restart bluetooth` |

## Файли

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
