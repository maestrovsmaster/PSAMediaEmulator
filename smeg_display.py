import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt
from pydbus import SystemBus


class SmegDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.bus = SystemBus()
        self.initUI()

        # Таймер для оновлення метаданих (щосекунди)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_track_data)
        self.timer.start(1000)

    def initUI(self):
        # Налаштування вікна в стилі PSA
        self.setWindowTitle('SMEG+ Emulator')
        self.setFixedSize(800, 480)  # Стандартна роздільна здатність
        self.setStyleSheet("background-color: #1a1a1a;")  # Темний фон

        self.layout = QVBoxLayout()

        self.label_artist = QLabel("Artist")
        self.label_artist.setStyleSheet("color: #00aaff; font-size: 24px; font-weight: bold;")
        self.label_artist.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_title = QLabel("Song Title")
        self.label_title.setStyleSheet("color: white; font-size: 32px;")
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addStretch()
        self.layout.addWidget(self.label_artist)
        self.layout.addWidget(self.label_title)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def update_track_data(self):
        try:
            # Шукаємо плеєр (аналогічно нашому першому скрипту)
            obj = self.bus.get('org.bluez', '/')
            for path, interfaces in obj.GetManagedObjects().items():
                if 'org.bluez.MediaPlayer1' in interfaces:
                    player = self.bus.get('org.bluez', path)
                    meta = player.Track
                    self.label_artist.setText(meta.get('Artist', 'Unknown Artist'))
                    self.label_title.setText(meta.get('Title', 'Unknown Track'))
        except:
            self.label_title.setText("Searching for Phone...")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SmegDisplay()
    ex.show()
    sys.exit(app.exec())