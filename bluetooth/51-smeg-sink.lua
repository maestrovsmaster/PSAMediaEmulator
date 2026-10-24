-- WirePlumber 0.4: ноутбук працює лише як A2DP-колонка (і може грати в навушники),
-- без HFP/HSP, щоб телефон не намагався вести через нього дзвінки
bluez_monitor.properties["bluez5.roles"] = "[ a2dp_sink a2dp_source ]"
