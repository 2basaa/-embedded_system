cmd_/home/pi/kumikomi/module/modules.order := {   echo /home/pi/kumikomi/module/mymodule.ko; :; } | awk '!x[$$0]++' - > /home/pi/kumikomi/module/modules.order
