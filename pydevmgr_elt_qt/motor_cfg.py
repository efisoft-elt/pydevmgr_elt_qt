from dataclasses import dataclass
from enum import Enum, EnumMeta
from typing import Tuple
from pydantic.main import BaseModel
from pydevmgr_core import DataLink, NodeVar
from pydevmgr_core.parsers import DefaultFloat

from .elt_device_cfg import EltDeviceCfg 
from pydevmgr_core_qt import QtIo, IoGroup, QtIoSetter, get_setter_class, get_getter_class, get_builder_class, get_connector_class
from .io import find_ui

from pydevmgr_core_qt import  Action, record_qt
from PyQt5 import QtWidgets, uic 
from pydevmgr_elt import Motor
Base = EltDeviceCfg



@dataclass
class Sequence:
    action_number: int
    value1: float
    value2: float 


@dataclass
class QtSequence:
    action: QtWidgets.QComboBox
    value1: QtWidgets.QLineEdit 
    value2: QtWidgets.QLineEdit 


@dataclass
class QtInitSequenceSetter:
    actions: Enum = Motor.Cfg.InitSeqNumber
    def set(self, widget: QtWidgets.QLabel, seq: Sequence):
        action_txt = self.actions(seq.action_number).name
        widget.setText( f"{action_txt:>13} {seq.value1:.3f} {seq.value2:.3f}")

@dataclass
class QtInitSequenceGetter:
    action_getter = get_getter_class( QtWidgets.QComboBox, Enum)(Motor.Cfg.InitSeqNumber)
    value_getter = get_getter_class( QtWidgets.QLineEdit, float)(parser=DefaultFloat)

    def get(self, widgets: QtSequence) -> Sequence:
        return (self.action_getter.get(widgets.action), 
               self.value_getter.get(widgets.value1), 
               self.value_getter.get(widgets.value2))

@dataclass
class QtInitSequenceInputBuilder:
    action_builder = get_builder_class(QtWidgets.QComboBox, EnumMeta)(Motor.Cfg.InitSeqNumber)
    
    def build(self, widgets: QtSequence):
        self.action_builder.build(widgets.action)
        widgets.value1.setText("0.0")
        widgets.value2.setText("0.0")

@dataclass
class QtInitSequenceInputSetter:
    action_setter = get_setter_class( QtWidgets.QComboBox, Enum)(Motor.Cfg.InitSeqNumber)
    value_setter = get_setter_class(QtWidgets.QLineEdit, float)(format="%.3f")

    def set(self, 
        widgets: QtSequence, 
        values: Sequence
     ) -> None:
        self.action_setter.set(widgets.action, values.action)
        self.value_setter.set( widgets.value1, values.value1)
        self.value_setter.set( widgets.value2, values.value2)


class Proc:
        bool_io = QtIoSetter( 
                    setter = get_setter_class(QtWidgets.QLabel, bool)(), 
                    getter = get_getter_class(QtWidgets.QCheckBox, bool)() 
                )
        float_io = QtIoSetter( 
                    setter = get_setter_class(QtWidgets.QLabel, float)(format="%.3f"), 
                    getter = get_getter_class(QtWidgets.QLineEdit, float)() 
                )
        int_io = QtIoSetter( 
                    setter = get_setter_class(QtWidgets.QLabel, int)(), 
                    getter = get_getter_class(QtWidgets.QLineEdit, int)() 
                )

        axis_io = QtIoSetter( 
                    setter =  get_setter_class(QtWidgets.QLabel, Enum)(Motor.Cfg.AXIS_TYPE), 
                    getter =  get_getter_class(QtWidgets.QComboBox, Enum)(Motor.Cfg.AXIS_TYPE)
                )
        init_seq_io =  QtIoSetter( 
                    setter = QtInitSequenceSetter(), 
                    getter = QtInitSequenceGetter() 
                )


        bool_getter = get_getter_class( QtWidgets.QCheckBox, bool)()
        bool_setter = get_setter_class( QtWidgets.QLabel, bool)()
        
        float_getter = get_getter_class( QtWidgets.QLineEdit, float)()
        float_setter = get_setter_class( QtWidgets.QLabel, float)(format="%.3f")
        
        int_getter = get_getter_class( QtWidgets.QLineEdit, int)()
        int_setter = get_setter_class( QtWidgets.QLabel,  int)()

        axis_getter = get_getter_class( QtWidgets.QComboBox, Enum)(Motor.Cfg.AXIS_TYPE)
        axis_builder = get_builder_class( QtWidgets.QComboBox, EnumMeta)(Motor.Cfg.AXIS_TYPE)
        axis_setter = get_setter_class( QtWidgets.QComboBox, Enum)(Motor.Cfg.AXIS_TYPE)
        
        init_seq_setter = QtInitSequenceInputSetter()
        init_seq_getter = QtInitSequenceGetter()
        init_seq_builder = QtInitSequenceInputBuilder()

        button_connector = get_connector_class(QtWidgets.QPushButton, Action)() 



class CfgData(BaseModel):
        active_low_index:   NodeVar[bool]   =  False
        active_low_lhw:     NodeVar[bool]   =  False
        active_low_lstop:   NodeVar[bool]   =  False
        active_low_ref:     NodeVar[bool]   =  False
        active_low_uhw:     NodeVar[bool]   =  False
        active_low_ustop:   NodeVar[bool]   =  False
        axis_type:          NodeVar[int]    =  Motor.Cfg.AXIS_TYPE.LINEAR
        backlash:           NodeVar[float]  =  0.0
        brake:              NodeVar[bool]   =  False
        check_inpos:        NodeVar[bool]   =  False
        disable:            NodeVar[bool]   =  False
        exec_post_init:     NodeVar[bool]   =  False
        exec_post_move:     NodeVar[bool]   =  False
        exec_pre_init:      NodeVar[bool]   =  False
        exec_pre_move:      NodeVar[bool]   =  False
        init_seq10_action:  NodeVar[int]    =  0
        init_seq10_value1:  NodeVar[float]  =  0.0
        init_seq10_value2:  NodeVar[float]  =  0.0
        init_seq1_action:   NodeVar[int]    =  0
        init_seq1_value1:   NodeVar[float]  =  0.0
        init_seq1_value2:   NodeVar[float]  =  0.0
        init_seq2_action:   NodeVar[int]    =  0
        init_seq2_value1:   NodeVar[float]  =  0.0
        init_seq2_value2:   NodeVar[float]  =  0.0
        init_seq3_action:   NodeVar[int]    =  0
        init_seq3_value1:   NodeVar[float]  =  0.0
        init_seq3_value2:   NodeVar[float]  =  0.0
        init_seq4_action:   NodeVar[int]    =  0
        init_seq4_value1:   NodeVar[float]  =  0.0
        init_seq4_value2:   NodeVar[float]  =  0.0
        init_seq5_action:   NodeVar[int]    =  0
        init_seq5_value1:   NodeVar[float]  =  0.0
        init_seq5_value2:   NodeVar[float]  =  0.0
        init_seq6_action:   NodeVar[int]    =  0
        init_seq6_value1:   NodeVar[float]  =  0.0
        init_seq6_value2:   NodeVar[float]  =  0.0
        init_seq7_action:   NodeVar[int]    =  0
        init_seq7_value1:   NodeVar[float]  =  0.0
        init_seq7_value2:   NodeVar[float]  =  0.0
        init_seq8_action:   NodeVar[int]    =  0
        init_seq8_value1:   NodeVar[float]  =  0.0
        init_seq8_value2:   NodeVar[float]  =  0.0
        init_seq9_action:   NodeVar[int]    =  0
        init_seq9_value1:   NodeVar[float]  =  0.0
        init_seq9_value2:   NodeVar[float]  =  0.0
        lock:               NodeVar[bool]   =  False
        lock_pos:           NodeVar[float]  =  0.0
        lock_tolerance:     NodeVar[float]  =  0.0
        low_brake:          NodeVar[bool]   =  False
        low_inpos:          NodeVar[bool]   =  False
        max_pos:            NodeVar[float]  =  0.0
        min_pos:            NodeVar[float]  =  0.0
        tout_init:          NodeVar[int]    =  0
        tout_move:          NodeVar[int]    =  0
        tout_switch:        NodeVar[int]    =  0
        velocity:           NodeVar[float]  =  0.0


def set_motor_cfg_widget(w):
    # group all io object in one structure 
    class io:
        brake       = IoGroup(w.in_brake, w.brake)
        low_brake   = IoGroup(w.in_low_brake, w.low_brake)
        check_inpos = IoGroup(w.in_check_inpos, w.check_inpos)
        low_inpos   = IoGroup(w.in_low_inpos, w.low_inpos)
        active_low_lstop = IoGroup(w.in_active_low_lstop, w.active_low_lstop)
        active_low_lhw   = IoGroup(w.in_active_low_lhw, w.active_low_lhw)
        active_low_ref   = IoGroup(w.in_active_low_ref, w.active_low_ref)
        active_low_index = IoGroup(w.in_active_low_index, w.active_low_index)

        active_low_uhw   = IoGroup(w.in_active_low_uhw, w.active_low_uhw)
        active_low_ustop = IoGroup(w.in_active_low_ustop, w.active_low_ustop)
        exec_pre_init    = IoGroup(w.in_exec_pre_init, w.exec_pre_init)
        exec_post_init   = IoGroup(w.in_exec_post_init, w.exec_post_init)
        exec_pre_move  = IoGroup(w.in_exec_pre_move, w.exec_pre_move)
        exec_post_move = IoGroup(w.in_exec_post_move, w.exec_post_move)
        disable        = IoGroup(w.in_disable, w.disable)
        lock           = IoGroup(w.in_lock, w.lock)
        
        
        min_pos        = IoGroup(w.in_min_pos, w.min_pos)
        max_pos        = IoGroup(w.in_max_pos, w.max_pos)
        lock_pos       = IoGroup(w.in_lock_pos, w.lock_pos)
        lock_tolerance = IoGroup(w.in_lock_tolerance, w.lock_tolerance)
        backlash       = IoGroup(w.in_backlash, w.backlash)
        

        tout_init   = IoGroup(w.in_tout_init, w.tout_init)
        tout_move   = IoGroup(w.in_tout_move, w.tout_move)
        tout_switch = IoGroup(w.in_tout_switch, w.tout_switch)
        
        ints = [tout_init, tout_move, tout_switch]

        axis = IoGroup(w.in_axis_type, w.axis_type)
    
        init_seq1 = IoGroup( QtSequence(w.init1_action, w.init1_value1, w.init1_value2), w.init1_actual) 
        init_seq2 = IoGroup( QtSequence(w.init2_action, w.init2_value1, w.init2_value2), w.init2_actual) 
        init_seq3 = IoGroup( QtSequence(w.init3_action, w.init3_value1, w.init3_value2), w.init3_actual) 
        init_seq4 = IoGroup( QtSequence(w.init4_action, w.init4_value1, w.init4_value2), w.init4_actual) 
        init_seq5 = IoGroup( QtSequence(w.init5_action, w.init5_value1, w.init5_value2), w.init5_actual) 
        init_seq6 = IoGroup( QtSequence(w.init6_action, w.init6_value1, w.init6_value2), w.init6_actual) 
        init_seq7 = IoGroup( QtSequence(w.init7_action, w.init7_value1, w.init7_value2), w.init7_actual) 
        init_seq8 = IoGroup( QtSequence(w.init8_action, w.init8_value1, w.init8_value2), w.init8_actual) 
        init_seq9 = IoGroup( QtSequence(w.init9_action, w.init9_value1, w.init9_value2), w.init9_actual) 
        init_seq10 = IoGroup( QtSequence(w.init10_action, w.init10_value1, w.init10_value2), w.init10_actual) 
        

    w.io = io

class MotorCfgSetter:
    
    def set(self, widget, data: CfgData):
        cfg = data.cfg
        
        io = widget.io

        ################### Bools ####################################
        S = Proc.bool_io.set
        S(io.brake,  cfg.brake  )
        S(io.low_brake, cfg.low_brake)
        S(io.check_inpos, cfg.check_inpos)
        S(io.low_inpos, cfg.low_inpos)

        S(io.active_low_lstop, cfg.active_low_lstop)
        S(io.active_low_lhw, cfg.active_low_lhw)
        S(io.active_low_ref, cfg.active_low_ref)
        S(io.active_low_index, cfg.active_low_index)

        S(io.active_low_uhw, cfg.active_low_uhw)
        S(io.active_low_ustop, cfg.active_low_ustop)
        S(io.exec_pre_init, cfg.exec_pre_init)
        S(io.exec_post_init, cfg.exec_post_init)

        S(io.exec_pre_move, cfg.exec_pre_move)
        S(io.exec_post_move, cfg.exec_post_move)
        S(io.disable, cfg.disable)
        S(io.lock, cfg.lock)     

        ################### floats ####################################
        S = Proc.float_io.set
        S(io.min_pos, cfg.min_pos)
        S(io.max_pos, cfg.max_pos)
        S(io.lock_pos, cfg.lock_pos)
        S(io.lock_tolerance, cfg.lock_tolerance)
        S(io.backlash, cfg.backlash)        
        
        ##################### ints ####################################
        S = Proc.int_io.set
        S(io.tout_init, cfg.tout_init)
        S(io.tout_move, cfg.tout_move)
        S(io.tout_switch, cfg.tout_switch)

        self.axis_io.set( io.axis,  cfg.axis_type)


        S = self.init_seq_io.set
        S(io.init_seq1, cfg.init_seq1)
        S(io.init_seq2, cfg.init_seq2)
        S(io.init_seq3, cfg.init_seq3)
        S(io.init_seq4, cfg.init_seq4)
        S(io.init_seq5, cfg.init_seq5)
        S(io.init_seq6, cfg.init_seq6)
        S(io.init_seq7, cfg.init_seq7)
        S(io.init_seq8, cfg.init_seq8)
        S(io.init_seq9, cfg.init_seq9)
        S(io.init_seq10, cfg.init_seq10)

@record_qt(Motor, "cfg")
class MotorCfg(Base):

    class Widget(QtWidgets.QFrame):

     
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            uic.loadUi(find_ui('motor_cfg_frame.ui'), self) 
            set_motor_cfg_widget(self)

    class Monitor(Base.Monitor):
        class Data(Base.Monitor.Data):
            Cfg = Motor.Data.Cfg
            cfg: Cfg = Cfg()
        
        DataSetter = MotorCfgSetter()

        data_setter = DataSetter()

        def update(self, w , data):
            self.data_setter.set(w, data)
    
    class Connector(Base.Connector):

         
        class Data(Motor.Data.Cfg):
            pass
        
        def disconnect(self, widget):
            super().disconnect(widget)

            Proc.button_connector.disconnect( widget.in_upload_to )
            Proc.button_connector.disconnect( widget.in_from_config_file )
            Proc.button_connector.disconnect( widget.in_download_from )      

        def connect(self, widget, motor):
            super().connect(widget, motor)

            feedback = None #QtTextFeedback( widget.rpc_feedback )
            

            Proc.axis_builder.build(widget.in_axis_type)
            B = Proc.init_seq_builder.build
            B( (widget.init1_action, widget.init1_value1, widget.init1_value2) )
            B( (widget.init2_action, widget.init2_value1, widget.init2_value2) )
            B( (widget.init3_action, widget.init3_value1, widget.init3_value2) )
            B( (widget.init4_action, widget.init4_value1, widget.init4_value2) )
            B( (widget.init5_action, widget.init5_value1, widget.init5_value2) )
            B( (widget.init6_action, widget.init6_value1, widget.init6_value2) )
            B( (widget.init7_action, widget.init7_value1, widget.init7_value2) )
            B( (widget.init8_action, widget.init8_value1, widget.init8_value2) )
            B( (widget.init9_action, widget.init9_value1, widget.init9_value2) )
            B( (widget.init10_action,widget.init10_value1,widget.init10_value2) )

            
            def configure_motor():
                cfg = self.Data()
                dl = DataLink( motor.cfg, cfg) 
                dl.download()
                
                self.set_config(widget, cfg)    
                dl.upload()
            
            widget.configure_action = Action(configure_motor, [], feedback)
            Proc.button_connector.connect( widget.in_upload_to, widget.configure_action)
            
            def download_and_set_inputs():
                cfg = self.Data()
                dl = DataLink(motor.cfg, cfg)
                dl.download()
                self.set_inputs(widget, cfg) 

            widget.download_action = Action( download_and_set_inputs, [], feedback)
            Proc.button_connector.connect( widget.in_download_from, widget.download_action)
        
            def set_inputs_from_config():
                cfg = self.Data()
                dl = DataLink(motor.cfg, cfg)
                nodes = motor.get_configuration()
                dl.download_from_nodes(nodes)     
                self.set_inputs( widget, cfg)
            widget.upload_config_action = Action( set_inputs_from_config, [], feedback)
            Proc.button_connector.connect( widget.in_from_config_file, widget.upload_config_action)
            
            if motor.is_connected():
                download_and_set_inputs()
            else:
                set_inputs_from_config()

        def set_inputs(self, w, cfg):

            ##### Bools ################################
            S = Proc.bool_setter.set
            S( w.in_brake, cfg.brake)
            S( w.in_low_brake, cfg.low_brake)
            S( w.in_check_inpos, cfg.check_inpos)
            S( w.in_low_inpos, cfg.low_inpos)

            S(w.in_active_low_lstop, cfg.active_low_lstop)
            S(w.in_active_low_lhw, cfg.active_low_lhw)
            S(w.in_active_low_ref, cfg.active_low_ref)
            S(w.in_active_low_index, cfg.active_low_index)

            S(w.in_active_low_uhw, cfg.active_low_uhw)
            S(w.in_active_low_ustop, cfg.active_low_ustop)
            S(w.in_exec_pre_init, cfg.exec_pre_init)
            S(w.in_exec_post_init, cfg.exec_post_init)

            S(w.in_exec_pre_move, cfg.exec_pre_move)
            S(w.in_exec_post_move, cfg.exec_post_move)
            S(w.in_disable, cfg.disable)
            S(w.in_lock, cfg.lock)
        
            ####### floats ###########################
            S = Proc.float_setter.set
            S(w.in_min_pos, cfg.min_pos)
            S(w.in_max_pos, cfg.max_pos)
            S(w.in_lock_pos, cfg.lock_pos)
            S(w.in_lock_tolerance, cfg.lock_tolerance)
            S(w.in_backlash, cfg.backlash)
            
            ####### ints ###########################
            S = Proc.int_setter.set
            S(w.in_tout_init, cfg.tout_init)
            S(w.in_tout_move, cfg.tout_move)
            S(w.in_tout_switch, cfg.tout_switch)           
            
            
            Proc.axis_setter.set( w.in_axis_type, cfg.axis_type)
            
            ######### init seq #################### 
            S = Proc.init_seq_setter.set 
            S( (w.init1_action, w.init1_value1, w.init1_value2) , 
               (cfg.init_seq1_action, cfg.init_seq1_value1, cfg.init_seq1_value2) )
            S( (w.init2_action, w.init2_value1, w.init2_value2) , 
               (cfg.init_seq2_action, cfg.init_seq2_value1, cfg.init_seq2_value2) )
            S( (w.init3_action, w.init3_value1, w.init3_value2) , 
               (cfg.init_seq3_action, cfg.init_seq3_value1, cfg.init_seq3_value2) )
            S( (w.init4_action, w.init4_value1, w.init4_value2) , 
               (cfg.init_seq4_action, cfg.init_seq4_value1, cfg.init_seq4_value2) )
            S( (w.init5_action, w.init5_value1, w.init5_value2) , 
               (cfg.init_seq5_action, cfg.init_seq5_value1, cfg.init_seq5_value2) )
            S( (w.init6_action, w.init6_value1, w.init6_value2) , 
               (cfg.init_seq6_action, cfg.init_seq6_value1, cfg.init_seq6_value2) )
            S( (w.init7_action, w.init7_value1, w.init7_value2) , 
               (cfg.init_seq7_action, cfg.init_seq7_value1, cfg.init_seq7_value2) )
            S( (w.init8_action, w.init8_value1, w.init8_value2) , 
               (cfg.init_seq8_action, cfg.init_seq8_value1, cfg.init_seq8_value2) )
            S( (w.init9_action, w.init9_value1, w.init9_value2) , 
               (cfg.init_seq9_action, cfg.init_seq9_value1, cfg.init_seq9_value2) )
            S( (w.init10_action, w.init10_value1, w.init10_value2) , 
               (cfg.init_seq10_action, cfg.init_seq10_value1, cfg.init_seq10_value2) )


            
        def set_config(self, w, cfg):
            ##### Bools ################################
            G = Proc.bool_getter.get
            cfg.brake = G(w.in_brake)
            cfg.low_brake = G(w.in_low_brake)
            cfg.check_inpos = G(w.in_check_inpos)
            cfg.low_inpos = G(w.in_low_inpos)
            
            cfg.active_low_lstop = G(w.in_active_low_lstop)
            cfg.active_low_lhw = G(w.in_active_low_lhw)
            cfg.active_low_ref = G(w.in_active_low_ref)
            cfg.active_low_index = G(w.in_active_low_index)
            
            cfg.active_low_uhw = G(w.in_active_low_uhw)
            cfg.active_low_ustop = G(w.in_active_low_ustop)
            cfg.exec_pre_init = G(w.in_exec_pre_init)
            cfg.exec_post_init = G(w.in_exec_post_init)
            cfg.exec_pre_move = G(w.in_exec_pre_move)
            cfg.exec_post_move = G(w.in_exec_post_move)
            cfg.disable = G(w.in_disable)
            cfg.lock = G(w.in_lock)    
            
            ####### floats ###########################3
            G = Proc.float_getter.get
            cfg.min_pos = G(w.in_min_pos)
            cfg.max_pos = G(w.in_max_pos)
            cfg.lock_pos = G(w.in_lock_pos)
            cfg.lock_tolerance = G(w.in_lock_tolerance)
            cfg.backlash = G(w.in_backlash)
            
            ####### ints ###########################3
            G = Proc.int_getter.get
            cfg.tout_init = G(w.in_tout_init)
            cfg.tout_move = G(w.in_tout_move)
            cfg.tout_switch = G(w.in_tout_switch)

            ########################################### 
            cfg.axis_type = Proc.axis_getter.get( w.in_axis_type)

            
            G = Proc.init_seq_getter.get
            (cfg.init_seq1_action, 
             cfg.init_seq1_value1, 
             cfg.init_seq1_value2)  = G( (w.init1_action, w.init1_value1, w.init1_value2) )
            (cfg.init_seq2_action, 
             cfg.init_seq2_value1, 
             cfg.init_seq2_value2)  = G( (w.init2_action, w.init2_value1, w.init2_value2) )
            (cfg.init_seq3_action, 
             cfg.init_seq3_value1, 
             cfg.init_seq3_value2)  = G( (w.init3_action, w.init3_value1, w.init3_value2) )
            (cfg.init_seq4_action, 
             cfg.init_seq4_value1, 
             cfg.init_seq4_value2)  = G( (w.init4_action, w.init4_value1, w.init4_value2) )
            (cfg.init_seq5_action, 
             cfg.init_seq5_value1, 
             cfg.init_seq5_value2)  = G( (w.init5_action, w.init5_value1, w.init5_value2) )
            (cfg.init_seq6_action, 
             cfg.init_seq6_value1, 
             cfg.init_seq6_value2)  = G( (w.init6_action, w.init6_value1, w.init6_value2) )
            (cfg.init_seq7_action, 
             cfg.init_seq7_value1, 
             cfg.init_seq7_value2)  = G( (w.init7_action, w.init7_value1, w.init7_value2) )
            (cfg.init_seq8_action, 
             cfg.init_seq8_value1, 
             cfg.init_seq8_value2)  = G( (w.init8_action, w.init8_value1, w.init8_value2) )
            (cfg.init_seq9_action, 
             cfg.init_seq9_value1, 
             cfg.init_seq9_value2)  = G( (w.init9_action, w.init9_value1, w.init9_value2) )
            (cfg.init_seq10_action, 
             cfg.init_seq10_value1, 
             cfg.init_seq10_value2)  = G( (w.init10_action, w.init10_value1, w.init10_value2) )


                

