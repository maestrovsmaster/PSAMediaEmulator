#!/usr/bin/env python3
# Bluetooth-агент SMEG: тримає адаптер видимим як колонку "SMEG"
# і приймає спарювання від телефонів без підтвердження (як магнітола в авто).
from gi.repository import GLib
from pydbus import SystemBus

ALIAS = "SMEG"
AGENT_PATH = "/org/smeg/agent"
ADAPTER_IFACE = "org.bluez.Adapter1"

bus = SystemBus()


def trust(device):
    """Позначає пристрій довіреним, щоб наступні підключення йшли автоматично"""
    try:
        bus.get("org.bluez", device)["org.bluez.Device1"].Trusted = True
    except Exception as e:
        print(f"Не вдалося зробити {device} довіреним: {e}")


class Agent:
    """
    <node>
      <interface name="org.bluez.Agent1">
        <method name="Release"/>
        <method name="RequestPinCode">
          <arg type="o" name="device" direction="in"/>
          <arg type="s" name="pincode" direction="out"/>
        </method>
        <method name="DisplayPinCode">
          <arg type="o" name="device" direction="in"/>
          <arg type="s" name="pincode" direction="in"/>
        </method>
        <method name="RequestPasskey">
          <arg type="o" name="device" direction="in"/>
          <arg type="u" name="passkey" direction="out"/>
        </method>
        <method name="DisplayPasskey">
          <arg type="o" name="device" direction="in"/>
          <arg type="u" name="passkey" direction="in"/>
          <arg type="q" name="entered" direction="in"/>
        </method>
        <method name="RequestConfirmation">
          <arg type="o" name="device" direction="in"/>
          <arg type="u" name="passkey" direction="in"/>
        </method>
        <method name="RequestAuthorization">
          <arg type="o" name="device" direction="in"/>
        </method>
        <method name="AuthorizeService">
          <arg type="o" name="device" direction="in"/>
          <arg type="s" name="uuid" direction="in"/>
        </method>
        <method name="Cancel"/>
      </interface>
    </node>
    """

    def Release(self):
        print("Агента відключено BlueZ")

    def RequestPinCode(self, device):
        print(f"PIN-запит від {device}, віддаю 0000")
        trust(device)
        return "0000"

    def DisplayPinCode(self, device, pincode):
        print(f"PIN для {device}: {pincode}")

    def RequestPasskey(self, device):
        print(f"Passkey-запит від {device}, віддаю 0")
        trust(device)
        return 0

    def DisplayPasskey(self, device, passkey, entered):
        print(f"Passkey для {device}: {passkey:06d}")

    def RequestConfirmation(self, device, passkey):
        print(f"Спарювання з {device} ({passkey:06d}) підтверджено автоматично")
        trust(device)

    def RequestAuthorization(self, device):
        print(f"Авторизація {device} дозволена")
        trust(device)

    def AuthorizeService(self, device, uuid):
        print(f"Сервіс {uuid} для {device} дозволено")

    def Cancel(self):
        print("Спарювання скасовано")


def configure_adapter(path):
    """Вмикає адаптер і робить його постійно видимою колонкою"""
    try:
        adapter = bus.get("org.bluez", path)[ADAPTER_IFACE]
        adapter.Powered = True
        adapter.Alias = ALIAS
        adapter.PairableTimeout = 0
        adapter.Pairable = True
        adapter.DiscoverableTimeout = 0
        adapter.Discoverable = True
        print(f"Адаптер {path} ({adapter.Address}) видимий як '{ALIAS}'")
    except Exception as e:
        print(f"Не вдалося налаштувати адаптер {path}: {e}")


def configure_all_adapters():
    objects = bus.get("org.bluez", "/").GetManagedObjects()
    for path, interfaces in objects.items():
        if ADAPTER_IFACE in interfaces:
            configure_adapter(path)


def on_bluez_appeared(*_):
    """Викликається на старті і щоразу після перезапуску bluetoothd"""
    try:
        manager = bus.get("org.bluez", "/org/bluez")["org.bluez.AgentManager1"]
        manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
        manager.RequestDefaultAgent(AGENT_PATH)
        print("Агент зареєстровано (NoInputNoOutput)")
    except Exception as e:
        print(f"Помилка реєстрації агента: {e}")
    configure_all_adapters()


def on_interfaces_added(sender, obj, iface, signal, params):
    # Свисток перевставили в USB — налаштовуємо знову
    path, interfaces = params
    if ADAPTER_IFACE in interfaces:
        configure_adapter(path)


def on_properties_changed(sender, obj, iface, signal, params):
    # Хтось (напр. панель налаштувань GNOME) вимкнув видимість — повертаємо
    changed_iface, changed, _ = params
    if changed_iface == ADAPTER_IFACE and (changed.get("Discoverable") is False or changed.get("Powered") is True):
        GLib.timeout_add_seconds(1, lambda: configure_adapter(obj) and False)


if __name__ == "__main__":
    bus.register_object(AGENT_PATH, Agent(), None)
    bus.subscribe(sender="org.bluez", iface="org.freedesktop.DBus.ObjectManager",
                  signal="InterfacesAdded", signal_fired=on_interfaces_added)
    bus.subscribe(sender="org.bluez", iface="org.freedesktop.DBus.Properties",
                  signal="PropertiesChanged", signal_fired=on_properties_changed)
    bus.watch_name("org.bluez", name_appeared=on_bluez_appeared)
    GLib.MainLoop().run()
