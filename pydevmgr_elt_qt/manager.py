from PyQt5.QtWidgets import QAction, QLabel, QMainWindow, QMenu
from pydantic.main import BaseModel
from pydevmgr_core  import NodeVar
from pydevmgr_core_qt import ( get_getter_class, get_connector_class, 
                                Action, QtTextFeedback,
                                QtManagerView)
from pydevmgr_elt.base.eltmanager import EltManager

from pydevmgr_elt_qt.helpers import CodeTextGroupSetter

Base = QtManagerView 

class QtManager(Base):
    
    class Widget(Base.Widget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
             
            self.actionMenu = QMenu("&Action", self)
            self.menuBar.addMenu(self.actionMenu)
            self.state = QLabel()
            self.top_layout.addWidget(self.state)
            self.rpc_feedback = QLabel()
            self.top_layout.addWidget(self.rpc_feedback)
            
            self.state.setMaximumHeight(30)
            self.rpc_feedback.setMaximumHeight(30)


    class Monitor(Base.Monitor):
        code_text_group = CodeTextGroupSetter()
        
        class Data(Base.Monitor.Data):

            class Stat(BaseModel):
                state: NodeVar[int] = 0
                state_txt: NodeVar[str] =  ""
                state_group: NodeVar[int] = 0
                
            stat = Stat()

        def update(self, widget, data):
            stat = data.stat
            self.code_text_group.set(
                            widget.state, 
                            (stat.state, stat.state_txt, stat.state_group)
                    )
            # if widget.downloader:
            #     widget.state.setText( "%d %d"%( len(widget.downloader._dict_nodes), len(widget.downloader._nodes) ) )  
            
    class Connector(Base.Connector):
        action_menu_connector = get_connector_class(QAction, Action)() 
        
        def add_action_menu(self, widget,  name, action):
            qact = QAction(name,  widget)
            widget.actionMenu.addAction(qact)
            self.action_menu_connector.connect( qact, action)
            
        def connect(self, widget, manager):
            
            feedback = QtTextFeedback( widget.rpc_feedback )

            widget.init_action = Action(manager.init,   [], feedback)
            widget.enable_action = Action(manager.enable, [], feedback)
            widget.disable_action = Action(manager.disable,[], feedback) 
            widget.reset_action = Action(manager.reset,  [], feedback)
            widget.configure_action = Action(manager.configure, [], feedback)
            widget.check_all_action = Action(manager.unignore_all, [], feedback)
            widget.uncheck_all_action = Action(manager.ignore_all, [], feedback)

            A = lambda n,a: self.add_action_menu(widget, n, a)
            
            A("INIT",    widget.init_action)
            A("ENABLE",  widget.enable_action)
            A("DISABLE", widget.disable_action)
            A("RESET",   widget.reset_action)
            widget.actionMenu.addSeparator()
            A("CONFIGURE", widget.configure_action)
            widget.actionMenu.addSeparator()
            A("CHECK ALL", widget.check_all_action)
            A("UNCHECK ALL", widget.uncheck_all_action)

                
             

