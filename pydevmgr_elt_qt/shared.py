from pydevmgr_core.base.vtype import VType
from systemy.system import BaseFactory
from pydevmgr_qt.api import PairingType, QtNodeFactory, BaseQtNode, get_style, Style

class QtInput(BaseQtNode):
    pass

class QtIoNode(BaseQtNode):
    """ A QtNode made from two widgets  
    
    The node has the:
    - input (QtNode), represent the user edditable value 
    - output (QtNode), represent the current value on the system
    
    The get method returns the input node value (e.g. `.input.get()`)
    The set method set the value on the output. If input and ouput value are different 
    the widget style will be changed. 
    

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        # touch all child  nodes 
        list(self.find( BaseQtNode, -1 ))

    class Config:
        input : BaseFactory = QtNodeFactory()  
        output: BaseFactory = QtNodeFactory()
        pairing_type = PairingType.none #stop auto pairing at this level  
         
            
    def fget(self):
        return self.input.get()

    def fset(self, value):
        self.output.set(value)
        try:
            cv = self.input.get()   
        except (ValueError, TypeError):
            test_different = True 
        else:
            test_different = value != cv
        if test_different:
            self.output.widget.setStyleSheet( get_style(Style.DIFFERENT) )
        else:
            self.output.widget.setStyleSheet( get_style(Style.SIMILAR) )

class QtIoFactory(BaseFactory):
    """ Factory for a QtIoNode according to vtype 

    At build, the output widget is set as 'in_'+name and output is name
    """
    vtype: VType
    name: str 
    clear: bool = True 

    @classmethod
    def get_system_class(cls):
        return QtIoNode

    def build(self, parent=None, name=None):
        return QtIoNode.Config( 
                vtype = self.vtype, 
                input = QtNodeFactory(vtype = self.vtype, widget =  "in_"+self.name, clear=self.clear),
                output= QtNodeFactory(vtype = self.vtype, widget = self.name), 
                pair = self.name, 
            ).build(parent, name)

def test_build(QtDevice, device):
    from PyQt5.QtWidgets import QApplication 
    from pydevmgr_qt.qtobjects import Connector 
    import sys 
    
    app = QApplication(sys.argv)
    Widget = QtDevice.get_widget_class()
    if isinstance(QtDevice, type):
        qtdevice = QtDevice( widget=Widget() )
    else:
        qtdevice = QtDevice
    
    connection = qtdevice.connect(device, Connector())
    print( "Pairs" , len(connection._node_pairs))
    return app, qtdevice, connection 

def test_run( app, qtdevice, device, connection, online=True):
    from PyQt5 import QtCore
    qtdevice.widget.show()
    timer = QtCore.QTimer()
    if online:
        timer.timeout.connect(connection.update)
        timer.start(200)
        with device:
            return app.exec()
    else:
        return app.exec()


def test_widget(QtDevice, device, online=None, Widget=None):
    import os 
    if online is None:
        online = bool(int(os.environ.get("TEST_QT", False)))
    app, qtdevice, connection = test_build(QtDevice, device)
    return test_run(app,  qtdevice, device,  connection, online=online)  
  


