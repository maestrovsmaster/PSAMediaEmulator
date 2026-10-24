# This is a sample Python script.
import sys

from PyQt6.QtWidgets import QApplication

from smeg_final import SmegEmulator


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SmegEmulator()
    ex.show()
    sys.exit(app.exec())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# Check info from Bluetooth bus
#dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_A4_75_B9_79_32_39/player0 org.freedesktop.DBus.Properties.Get string:org.bluez.MediaPlayer1 string:Track
