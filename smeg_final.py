import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QFrame
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
from pydbus import SystemBus


class SmegEmulator(QWidget):
    def __init__(self):
        super().__init__()
        try:
            self.bus = SystemBus()
        except Exception as e:
            print(f"Помилка D-Bus: {e}")

        self.player = None
        self.initUI()

        # Таймер оновлення
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(500)

    def _get_player(self):
        """Шукає активний плеєр через BlueZ"""
        try:
            obj = self.bus.get('org.bluez', '/')
            managed_objects = obj.GetManagedObjects()
            for path in managed_objects:
                if 'org.bluez.MediaPlayer1' in managed_objects[path]:
                    return self.bus.get('org.bluez', path)
        except Exception:
            return None
        return None

    def initUI(self):
        self.setWindowTitle('Citroen SMEG+ Digital Emulator')
        self.setFixedSize(800, 480)

        # Темний градієнтний фон як у магнітоли
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d1a26, stop:0.5 #1a2632, stop:1 #0d1a26);
                color: #8ed8f8;
                font-family: Arial, sans-serif;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(8)

        # =============== ВЕРХНЯ ЧАСТИНА: МЕТАДАНІ ===============
        top_section = QHBoxLayout()
        top_section.setSpacing(10)

        # Ліва панель з іконкою та великою кнопкою
        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)

        # Іконка музичної ноти
        left_icon_container = QFrame()
        left_icon_container.setFixedSize(90, 140)
        left_icon_container.setStyleSheet("""
            background-color: #0d1a26;
            border: 3px solid #4a7a93;
            border-radius: 5px;
        """)
        left_icon_layout = QVBoxLayout(left_icon_container)
        left_icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        music_icon = QLabel("♫")
        music_icon.setStyleSheet("font-size: 76px; color: #4a8098; border: none; background: transparent;")
        music_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_icon_layout.addWidget(music_icon)

        # Велика кнопка відтворення (ліворуч як на фото)
        left_play_btn = QPushButton("▶")
        left_play_btn.setFixedSize(90, 60)
        left_play_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d4a5c, stop:1 #1d3a4c);
                color: #c8e8f8;
                border: 3px solid #4a7a93;
                border-radius: 5px;
                font-size: 28px;
            }
            QPushButton:pressed {
                background: #4a7a93;
            }
        """)
        left_play_btn.clicked.connect(self.action_toggle)

        left_panel.addWidget(left_icon_container)
        left_panel.addWidget(left_play_btn)
        left_panel.addStretch()

        # Середня секція - інформація про трек
        info_section = QVBoxLayout()
        info_section.setSpacing(3)

        # Artist/Album box (верхня лінія з іконками)
        artist_container = QFrame()
        artist_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3d5a6f, stop:1 #2d4a5f);
            border: 3px solid #6a9ab8;
            border-radius: 4px;
        """)
        artist_layout = QHBoxLayout(artist_container)
        artist_layout.setContentsMargins(12, 10, 12, 10)

        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 22px; color: #c8e8f8; background: transparent; border: none;")

        self.label_artist = QLabel("ШУКАЮ ТЕЛЕФОН...")
        self.label_artist.setStyleSheet("font-size: 26px; color: #c8e8f8; background: transparent; border: none; font-weight: normal;")

        artist_layout.addWidget(user_icon)
        artist_layout.addWidget(self.label_artist)
        artist_layout.addStretch()

        # Album/Genre box
        album_container = QFrame()
        album_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2d4a5c, stop:1 #1d3a4c);
            border: 3px solid #6a9ab8;
            border-radius: 4px;
        """)
        album_layout = QHBoxLayout(album_container)
        album_layout.setContentsMargins(12, 10, 12, 10)

        cd_icon = QLabel("💿")
        cd_icon.setStyleSheet("font-size: 22px; color: #c8e8f8; background: transparent; border: none;")

        self.label_genre = QLabel("Альбом")
        self.label_genre.setStyleSheet("font-size: 26px; color: #c8e8f8; background: transparent; border: none; font-weight: normal;")

        album_layout.addWidget(cd_icon)
        album_layout.addWidget(self.label_genre)
        album_layout.addStretch()

        # Title box (нижня лінія)
        title_container = QFrame()
        title_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2d4a5c, stop:1 #1d3a4c);
            border: 3px solid #6a9ab8;
            border-radius: 4px;
        """)
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(12, 10, 12, 10)

        note_icon = QLabel("♪")
        note_icon.setStyleSheet("font-size: 26px; color: #c8e8f8; background: transparent; border: none;")

        self.label_title = QLabel("Bluetooth стрімінг")
        self.label_title.setStyleSheet("font-size: 26px; color: #c8e8f8; background: transparent; border: none; font-weight: normal;")

        title_layout.addWidget(note_icon)
        title_layout.addWidget(self.label_title)
        title_layout.addStretch()

        info_section.addWidget(artist_container)
        info_section.addWidget(album_container)
        info_section.addWidget(title_container)

        # Права секція - Source і Bluetooth
        right_section = QVBoxLayout()
        right_section.setSpacing(5)

        source_label = QLabel("Source ▼")
        source_label.setFixedHeight(35)
        source_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        source_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3d5a6f, stop:1 #2d4a5f);
            border: 3px solid #6a9ab8;
            border-radius: 4px;
            color: #c8e8f8;
            font-size: 17px;
            font-weight: normal;
        """)

        bluetooth_container = QFrame()
        bluetooth_container.setFixedSize(130, 155)
        bluetooth_container.setStyleSheet("""
            background-color: #0d1a26;
            border: 3px solid #4a7a93;
            border-radius: 5px;
        """)
        bluetooth_layout = QVBoxLayout(bluetooth_container)
        bluetooth_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_bt_icon = QLabel("ᛒ")
        self.lbl_bt_icon.setStyleSheet("font-size: 72px; color: #2a4a5c; border: none; background: transparent;")
        self.lbl_bt_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        bt_text = QLabel("Bluetooth")
        bt_text.setStyleSheet("font-size: 15px; color: #6a96a8; border: none; background: transparent;")
        bt_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        bluetooth_layout.addWidget(self.lbl_bt_icon)
        bluetooth_layout.addWidget(bt_text)

        right_section.addWidget(source_label)
        right_section.addWidget(bluetooth_container)

        top_section.addLayout(left_panel)
        top_section.addLayout(info_section, 1)
        top_section.addLayout(right_section)

        # =============== СЕРЕДНЯ ЧАСТИНА: КНОПКИ КЕРУВАННЯ ===============
        controls_container = QFrame()
        controls_container.setFixedHeight(110)
        controls_container.setStyleSheet("background: transparent; border: none;")

        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setSpacing(15)
        controls_layout.setContentsMargins(200, 10, 200, 10)

        btn_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d5a6f, stop:1 #2d4a5f);
                color: #8ed8f8;
                border: 3px solid #5a8ba3;
                border-radius: 8px;
                font-size: 32px;
                min-width: 100px;
                min-height: 70px;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a8ba3, stop:1 #4a7a93);
            }
        """

        self.btn_prev = QPushButton("⏮")
        self.btn_play = QPushButton("▶")
        self.btn_next = QPushButton("⏭")

        for btn in [self.btn_prev, self.btn_play, self.btn_next]:
            btn.setStyleSheet(btn_style)
            controls_layout.addWidget(btn)

        self.btn_prev.clicked.connect(self.action_prev)
        self.btn_play.clicked.connect(self.action_toggle)
        self.btn_next.clicked.connect(self.action_next)

        # =============== НИЖНЯ ЧАСТИНА: СТАТУС БАР ===============
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(55)
        bottom_bar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0d1a26, stop:1 #1a2632);
            border-top: 3px solid #4a7a93;
        """)

        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(25, 8, 25, 8)

        shuffle_icon = QLabel("🔀")
        shuffle_icon.setStyleSheet("font-size: 22px; color: #4a7083; background: transparent; border: none;")

        play_indicator = QLabel("▶")
        play_indicator.setStyleSheet("font-size: 20px; color: #5aa8c8; background: transparent; border: none;")

        self.time_label = QLabel("00:00")
        self.time_label.setStyleSheet("font-size: 24px; color: #a8e8ff; background: transparent; border: none; font-weight: bold;")

        # Версія прошивки по центру
        firmware_version = QLabel("SMEG5.43.A.R2")
        firmware_version.setStyleSheet("font-size: 16px; color: #5a8090; background: transparent; border: none;")
        firmware_version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.track_count = QLabel("Track 01/01")
        self.track_count.setStyleSheet("font-size: 20px; color: #7ab6c8; background: transparent; border: none;")

        bottom_layout.addWidget(shuffle_icon)
        bottom_layout.addWidget(play_indicator)
        bottom_layout.addWidget(self.time_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(firmware_version)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.track_count)

        # Додаємо все до головного layout
        main_layout.addLayout(top_section)
        main_layout.addWidget(controls_container)
        main_layout.addWidget(bottom_bar)

        self.setLayout(main_layout)

    def update_all(self):
        if not self.player:
            self.player = self._get_player()
            if self.player:
                self.lbl_bt_icon.setStyleSheet(
                    "font-size: 72px; color: #5aa8c8; border: none; background: transparent;")

        if self.player:
            try:
                meta = self.player.Track

                # ОТРИМУЄМО ДАНІ ТА ОБРІЗАЄМО ДО 30 СИМВОЛІВ
                raw_artist = meta.get('Artist', 'UNKNOWN ARTIST').upper()
                raw_title = meta.get('Title', 'No Title')
                raw_album = meta.get('Album', 'No Album')

                self.label_artist.setText(raw_artist[:30])
                self.label_title.setText(raw_title[:30])
                self.label_genre.setText(raw_album[:30])

                status = self.player.Status
                self.btn_play.setText("⏸" if status == "playing" else "▶")
            except Exception:
                self.player = None
                self.lbl_bt_icon.setStyleSheet("font-size: 72px; color: #2a4a5c; border: none; background: transparent;")
                self.label_artist.setText("З'ЄДНАННЯ РОЗІРВАНО")

    def action_next(self):
        if self.player: self.player.Next()

    def action_prev(self):
        if self.player: self.player.Previous()

    def action_toggle(self):
        if self.player:
            if self.player.Status == "playing":
                self.player.Pause()
            else:
                self.player.Play()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Right:
            self.action_next()
        elif event.key() == Qt.Key.Key_Left:
            self.action_prev()
        elif event.key() == Qt.Key.Key_Space:
            self.action_toggle()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SmegEmulator()
    ex.show()
    sys.exit(app.exec())