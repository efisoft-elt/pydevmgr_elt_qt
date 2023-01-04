from pydevmgr_elt_qt.base.device_container import  DeviceAppender, DeviceDispatcher, DeviceFilter, DeviceFilteredAppander
from pydevmgr_core import Downloader, open_device
from pydevmgr_elt_qt.motor import MotorCtrl
from pydevmgr_elt_qt.lamp import LampCtrl

from pydevmgr_elt_qt.adc import AdcCtrl
import sys 
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
from PyQt5 import QtCore


if __name__ == "__main__":
    

    app = QApplication(sys.argv)
   
    class Widget(QWidget):
        main_layout:  QHBoxLayout
        
        def __init__(self, *args, **kwargs):
            QWidget.__init__(self, *args, **kwargs)
            
            self.main_layout = QHBoxLayout(objectName="main_layout")
            self.setLayout(self.main_layout)
             
            widget1 = QWidget()
            layout1 = QVBoxLayout(objectName="layout1")
            widget1.setLayout(layout1) 

            widget2 = QWidget()
            layout2 = QVBoxLayout(objectName="layout2")
            widget2.setLayout(layout2) 
            
            self.main_layout.addWidget( widget1) 
            self.main_layout.addWidget( widget2) 
            
            self.clearButton = QPushButton(text="Clear")
            self.main_layout.addWidget( self.clearButton)
            
            self.extendButton = QPushButton(text="Extend")
            self.main_layout.addWidget( self.extendButton)
            
            self.replaceButton = QPushButton(text="Replace")
            self.main_layout.addWidget( self.replaceButton)



    w = Widget()
    
    motor = open_device("tins/motor1.yml(motor1)")
    lamp = open_device("tins/lamp1.yml(lamp1)")
    adc = open_device("tins/adc1.yml(adc1)")
    devices = [motor, lamp, adc]

    downloader = Downloader()
    w.show()
    

    fas = DeviceDispatcher( [
            DeviceFilteredAppander( DeviceAppender(layout="layout1"),
                DeviceFilter(dev_type=["Lamp", "Motor"]) ), 
            DeviceFilteredAppander( DeviceAppender(layout="layout2"), 
                 DeviceFilter(dev_type=['Adc']) )
          ], downloader=downloader )
    
     


    
    w.clearButton.clicked.connect( lambda : fas.clear(w) )
    w.extendButton.clicked.connect( lambda : fas.extend( w, devices))
    w.replaceButton.clicked.connect( lambda : fas.replace(w,devices))
    

  
    timer = QtCore.QTimer()
    timer.timeout.connect(downloader.download)
    
    sys.exit(app.exec_())


    with device:   
        with lamp:
            timer.start(100)
            sys.exit(app.exec_())

