import sys

path = 'd:/Work/IKFKSwitch'
path in sys.path or sys.path.append(path)


import ik_fk_switch
reload(ik_fk_switch)

ik_fk_switch.UI()