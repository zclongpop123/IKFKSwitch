#========================================
# author: changlong.zang
#   mail: zclongpop@163.com
#   date: Mon, 04 Jan 2016, 15:51:16
#========================================
import os, re, sip
from PyQt4 import QtCore, QtGui, uic
import maya.cmds as mc
import maya.OpenMayaUI as OpenMayaUI
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def getMayaWindow():
    '''
    return maya window by Qt object..
    '''
    maya_window = OpenMayaUI.MQtUtil.mainWindow()
    if maya_window:
        return sip.wrapinstance(long(maya_window), QtCore.QObject)



def undo_decorator(func):
    '''
    To fix maya can't undo bug..
    '''
    def doIt(*args, **kvargs):
        mc.undoInfo(openChunk=True)
        result = func(*args, **kvargs)
        mc.undoInfo(closeChunk=True)

        return result

    doIt.__name__ = func.__name__
    doIt.__doc__  = func.__doc__

    return doIt


windowClass, baseClass = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ik_fk_switch.ui'))
class UI(windowClass, baseClass):
    '''
    user interface...
    '''
    def __init__(self, parent=getMayaWindow()):
        super(UI, self).__init__(parent)
        self.setupUi(self)
        self.show()


    def on_btn_LoadNameSpace_clicked(self, args=None):
        if args==None:return
        self.let_NameSpace.setText(get_namespace())


    @undo_decorator
    def on_btn_SwitchLeftArm_clicked(self, args=None):
        if args==None:return

        namespace = str(self.let_NameSpace.text())

        if mc.getAttr('{0}FKIKArm_L.FKIKBlend'.format(namespace)) < 5:
            set_arm_to_ik(namespace, 'L')
            mc.setAttr('{0}FKIKArm_L.FKIKBlend'.format(namespace), 10)
        else:
            set_arm_to_fk(namespace, 'L')
            mc.setAttr('{0}FKIKArm_L.FKIKBlend'.format(namespace), 0)


    @undo_decorator
    def on_btn_SwitchRightArm_clicked(self, args=None):
        if args==None:return

        namespace = str(self.let_NameSpace.text())

        if mc.getAttr('{0}FKIKArm_R.FKIKBlend'.format(namespace)) < 5:
            set_arm_to_ik(namespace, 'R')
            mc.setAttr('{0}FKIKArm_R.FKIKBlend'.format(namespace), 10)
        else:
            set_arm_to_fk(namespace, 'R')
            mc.setAttr('{0}FKIKArm_R.FKIKBlend'.format(namespace), 0)



    @undo_decorator
    def on_btn_SwitchLeftLeg_clicked(self, args=None):
        if args==None:return

        namespace = str(self.let_NameSpace.text())

        if mc.getAttr('{0}FKIKLeg_L.FKIKBlend'.format(namespace)) < 5:
            set_leg_to_ik(namespace, 'L')
            mc.setAttr('{0}FKIKLeg_L.FKIKBlend'.format(namespace), 10)
        else:
            set_leg_to_fk(namespace, 'L')
            mc.setAttr('{0}FKIKLeg_L.FKIKBlend'.format(namespace), 0)



    @undo_decorator
    def on_btn_SwitchRightLeg_clicked(self, args=None):
        if args==None:return

        namespace = str(self.let_NameSpace.text())

        if mc.getAttr('{0}FKIKLeg_R.FKIKBlend'.format(namespace)) < 5:
            set_leg_to_ik(namespace, 'R')
            mc.setAttr('{0}FKIKLeg_R.FKIKBlend'.format(namespace), 10)
        else:
            set_leg_to_fk(namespace, 'R')
            mc.setAttr('{0}FKIKLeg_R.FKIKBlend'.format(namespace), 0)




def get_namespace():
    '''
    get select control namespace...
    '''
    sel_ctl = mc.ls(sl=True)
    if not sel_ctl:
        return str()

    namespace = re.match('(\w+:)+', sel_ctl[0])
    if not namespace:
        return str()

    return namespace.group()




def set_arm_to_fk(namespace, side):
    '''
    switch Arm to FK...
    '''
    shoulder_ctl = '{0}FKShoulder_{1}'.format(namespace, side)
    elobow_ctl   = '{0}FKElbow_{1}'.format(namespace,    side)
    wrist_ctl    = '{0}FKWrist_{1}'.format(namespace,    side)

    shoulder_jnt = '{0}Shoulder_{1}'.format(namespace, side)
    elobow_jnt   = '{0}Elbow_{1}'.format(namespace,    side)
    wrist_jnt    = '{0}Wrist_{1}'.format(namespace,    side)

    for ctl, jnt in ((shoulder_ctl, shoulder_jnt), (elobow_ctl, elobow_jnt), (wrist_ctl, wrist_jnt)):
        rotation = mc.xform(jnt, q=True, ws=True, ro=True)
        mc.xform(ctl, ws=True, ro=rotation)




def set_arm_to_ik(namespace, side):
    '''
    switch Arm to IK...
    '''
    arm_ctl  = '{0}IKArm_{1}'.format(namespace,   side)
    pole_ctl = '{0}PoleArm_{1}'.format(namespace, side)

    elobow_jnt   = '{0}Elbow_{1}'.format(namespace,    side)
    wrist_jnt    = '{0}Wrist_{1}'.format(namespace,    side)
    wrist_ik_jnt = '{0}IKXWrist_{1}'.format(namespace, side)

    temp_jnt = mc.duplicate(wrist_ik_jnt, po=True)[0]
    temp_ctl = mc.duplicate(arm_ctl,      po=True)[0]

    mc.parentConstraint(temp_jnt,  temp_ctl, mo=True)
    mc.parentConstraint(wrist_jnt, temp_jnt)

    for ctl, jnt in ((arm_ctl, wrist_jnt), (pole_ctl, elobow_jnt)):
        posi = mc.xform(jnt, q=True, ws=True,  t=True)
        mc.xform(ctl, ws=True, t=posi)

    rx, ry, rz = mc.getAttr('{0}.rotate'.format(temp_ctl))[0]
    mc.setAttr('{0}.rotate'.format(arm_ctl), rx, ry, rz)

    mc.delete(temp_jnt, temp_ctl)




def set_leg_to_fk(namespace, side):
    '''
    switch Leg to FK...
    '''
    hip_ctl   = '{0}FKHip_{1}'.format(namespace,   side)
    knee_ctl  = '{0}FKKnee_{1}'.format(namespace,  side)
    ankle_ctl = '{0}FKAnkle_{1}'.format(namespace, side)
    toes_ctl  = '{0}FKToes_{1}'.format(namespace,  side)

    hip_jnt   = '{0}Hip_{1}'.format(namespace,   side)
    knee_jnt  = '{0}Knee_{1}'.format(namespace,  side)
    ankle_jnt = '{0}Ankle_{1}'.format(namespace, side)
    toes_jnt  = '{0}Toes_{1}'.format(namespace,  side)

    for ctl, jnt in ((hip_ctl, hip_jnt), (knee_ctl, knee_jnt), (ankle_ctl, ankle_jnt)):
        rotation = mc.xform(jnt, q=True, ws=True, ro=True)
        mc.xform(ctl, ws=True, ro=rotation)




def set_leg_to_ik(namespace, side):
    '''
    switch Arm to IK...
    '''
    leg_ctl  = '{0}IKLeg_{1}'.format(namespace,   side)
    pole_ctl = '{0}PoleLeg_{1}'.format(namespace, side)

    knee_jnt     = '{0}Knee_{1}'.format(namespace,     side)
    ankle_jnt    = '{0}Ankle_{1}'.format(namespace,    side)
    ankle_ik_jnt = '{0}IKXAnkle_{1}'.format(namespace, side)

    mc.setAttr('{0}.swivel'.format(leg_ctl), 0)
    mc.setAttr('{0}.roll'.format(leg_ctl),   0)
    mc.setAttr('{0}.toe'.format(leg_ctl),    0)
    mc.setAttr('{0}RollHeel_{1}.r'.format(namespace, side),    0, 0, 0)
    mc.setAttr('{0}RollToesEnd_{1}.r'.format(namespace, side), 0, 0, 0)
    mc.setAttr('{0}RollToes_{1}.r'.format(namespace, side),    0, 0, 0)

    temp_jnt = mc.duplicate(ankle_ik_jnt, po=True)[0]
    temp_ctl = mc.duplicate(leg_ctl,      po=True)[0]

    mc.parentConstraint(temp_jnt,  temp_ctl, mo=True)
    mc.parentConstraint(ankle_jnt, temp_jnt)

    for ctl, jnt in ((leg_ctl, ankle_jnt), (pole_ctl, knee_jnt)):
        posi = mc.xform(jnt, q=True, ws=True,  t=True)
        mc.xform(ctl, ws=True, t=posi)

    rx, ry, rz = mc.getAttr('{0}.rotate'.format(temp_ctl))[0]
    mc.setAttr('{0}.rotate'.format(leg_ctl), rx, ry, rz)

    mc.delete(temp_jnt, temp_ctl)


    posi = mc.xform('{0}FKXKnee_{1}'.format(namespace, side), q=True, ws=True, t=True)
    mc.xform(pole_ctl, ws=True, t=posi)
