from pydbus import SystemBus
from pynput import keyboard


class SMEGController:
    def __init__(self):
        self.bus = SystemBus()
        self.player = self._get_player()

    def _get_player(self):
        obj = self.bus.get('org.bluez', '/')
        managed_objects = obj.GetManagedObjects()
        for path in managed_objects:
            if 'org.bluez.MediaPlayer1' in managed_objects[path]:
                return self.bus.get('org.bluez', path)
        return None

    def update_info(self):
        if self.player:
            meta = self.player.Track
            print(f"\r[SMEG] Грає: {meta.get('Artist', 'Unknown')} - {meta.get('Title', 'Unknown')}", end="")

    def on_press(self, key):
        if not self.player: return

        try:
            if key == keyboard.Key.right:
                self.player.Next()
                print("\n[Кермо] Наступний трек >>")
            elif key == keyboard.Key.left:
                self.player.Previous()
                print("\n[Кермо] Попередній трек <<")
            elif key == keyboard.Key.space:
                status = self.player.Status
                if status == "playing":
                    self.player.Pause()
                else:
                    self.player.Play()
                print(f"\n[Кермо] Play/Pause (Статус: {status})")
        except Exception as e:
            print(f"Помилка команд: {e}")


# Запуск системи
if __name__ == "__main__":
    smeg = SMEGController()
    print("--- Емуляція SMEG активована ---")
    print("Керування: Стрілки (Вліво/Вправо), Пробіл (Pause)")
    smeg.update_info()

    with keyboard.Listener(on_press=smeg.on_press) as listener:
        listener.join()