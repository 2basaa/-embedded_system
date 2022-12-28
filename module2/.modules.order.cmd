cmd_/home/pi/kumikomi/module2/modules.order := {   echo /home/pi/kumikomi/module2/kadai10.ko; :; } | awk '!x[$$0]++' - > /home/pi/kumikomi/module2/modules.order
