from typing import Type

from systemy.system import BaseFactory
from pydevmgr_elt_qt.shared import QtIoNode , QtInput 
from pydevmgr_elt.devices.motor.cfg import InitSeq
from pydevmgr_elt import Motor 
from pydevmgr_qt import QtNodeFactory, BaseQtNode, PairingType, QtInterface


class InitSeqInput(BaseQtNode):
    class Config:
        vtype: Type = InitSeq 
        action = QtNodeFactory( vtype=(Motor.Cfg.InitSeqNumber, Motor.Cfg.InitSeqNumber.END), 
                widget="init1_action", clear=True) 
        value1 = QtNodeFactory( vtype=float , widget="init1_value1") 
        value2 = QtNodeFactory( vtype=float , widget="init1_value2")
    
    def fget(self):
        return InitSeq( self.action.get() , self.value1.get(), self.value2.get()) 
    
    def fset(self, init_seq:InitSeq ):
        self.action.set( init_seq.action_number) 
        self.value1.set( init_seq.value1 )
        self.value2.set( init_seq.value2 ) 

class InitSeqInputFactory(BaseFactory):
    num: int 
    vtype: Type = InitSeq
    
    @classmethod 
    def get_system_class(cls):
        return InitSeqInput 
    
    def build(self, parent=None, name=None):
        n = self.num
        ic =  InitSeqInput.Config()
        ic.action.widget = f"init{n}_action"
        ic.value1.widget = f"init{n}_value1"
        ic.value2.widget = f"init{n}_value2"
        return ic.build( parent, name) 

        # return InitSeqInput.Config( 
        #         action = {"widget": f"init{n}_action", **InitSeqInput.action.dict()}, 
        #         value1 = {"widget": f"init{n}_value1"}, 
        #         value2 = {"widget": f"init{n}_value2"}
        #     ).build(parent, name)

class InitSeqOutputNode(BaseQtNode):
    class Config:
        vtype: Type =  InitSeq
    
    def fset(self, init_seq: InitSeq):
        text = f"{init_seq.action_number} {init_seq.value1} {init_seq.value2}"
        self.widget.setText( text ) 
        
    def fget(self):
        text = self.widget.text() 
        n, v1, v2 = text.split(" ")
        return InitSeq( int(n), float(v1), float(v2) )

class InitSeqOutputFactory(BaseFactory):
    num: int 
    vtype: Type = InitSeq 
    @classmethod
    def get_system_class(cls):
        return InitSeqOutputNode 

    def build(self, parent=None ,name=None):
        return InitSeqOutputNode.Config(
                widget=f"init{self.num}_actual"
            ).build(parent, name)

class InitSeqIoNode(QtIoNode):
    class Config:
        vtype: Type = InitSeq 
        output: BaseFactory = InitSeqOutputFactory(num=1)
        intput: BaseFactory = InitSeqInputFactory(num=1)

class InitSeqIoFactory(BaseFactory):
    num: int 
    vtype: Type = InitSeq
    
    @classmethod
    def get_system_class(cls):
        return InitSeqIoNode

    def build(self, parent=None, name=None):
        return InitSeqIoNode.Config(
                output = InitSeqOutputFactory(num=self.num),
                input = InitSeqInputFactory(num=self.num), 
                pair = f"init_seq{self.num}",
                # ConnectionConnectionconnection_type = ConnectionType.source 
            ).build(parent, name)


init_seq_factories = {}
for num in range(1,11):
    init_seq_factories[f"init_seq{num}"] =  InitSeqIoFactory(num=num) 

QtInitSeqInterface = type( "QtInitSeqInterface", (QtInterface,), init_seq_factories)


if __name__ == "__main__":
    InitSeqInputFactory(num=2)


