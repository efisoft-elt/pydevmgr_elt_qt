from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from pydevmgr_core.base.download import Downloader
from pydevmgr_core_qt.base_view import ConfigView
# from pydevmgr_core_qt.devices import DevicesWidget
from pydevmgr_core_qt.manager import QtManagerView
from pydevmgr_core_qt.view import ViewsConfig
from pydevmgr_elt import Motor, EltManager 
from pydevmgr_elt_qt.motor_ctrl import MotorCtrl
from pydevmgr_elt_qt.motor_cfg import MotorCfg
from pydevmgr_elt_qt.motor_line import MotorLine
from pydevmgr_elt_qt.manager import QtManager
import sys 
from pydevmgr_elt import io 


online = True


if __name__ == "__main__":

    mgr = EltManager("fcs", devices=[
        Motor('motor1', address="opc.tcp://192.168.1.11:4840", prefix="MAIN.Motor1"), 
        Motor('motor2', address="opc.tcp://192.168.1.11:4840", prefix="MAIN.Motor2"),
        # Motor('motor3', address="opc.tcp://192.168.1.11:4840", prefix="MAIN.Motor2")

        ])
    app = QApplication(sys.argv)
    
    config = ViewsConfig(**io.load_config("tins/tins_ui.yml") )
    
    qtmgr = QtManager(mgr, config=config)
    qtmgr.widget.show()
    

    c = 0
    def toto():
        global c
        if online:
            downloader.download()
        c += 1
        # if c==20:
        #     qtmgr.set_view("cfg")
        # if c==40:
        #     qtmgr.set_view("ctrl")
    

    downloader = Downloader()
    

    
    timer = QtCore.QTimer()
    # timer.timeout.connect(downloader.download)
    timer.timeout.connect(toto)
    if online:
        with mgr:
            qtmgr.connect_downloader(downloader)
            timer.start(100)
            sys.exit(app.exec_())
    else:
        timer.start(100)
        app.exec_()
