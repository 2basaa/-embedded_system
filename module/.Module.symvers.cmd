cmd_/home/pi/kumikomi/module/Module.symvers := sed 's/\.ko$$/\.o/' /home/pi/kumikomi/module/modules.order | scripts/mod/modpost -m -a  -o /home/pi/kumikomi/module/Module.symvers -e -i Module.symvers   -T -
