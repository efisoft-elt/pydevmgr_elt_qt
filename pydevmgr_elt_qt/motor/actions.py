from typing import Optional
from pydevmgr_core.base.upload import upload
from pydevmgr_qt.api import (
        QtFormular,  QtNodeFactory, QtTextFeedback, 
        Connector, QtInterface, PairingType, QtSelfFeedback, 
        FeedbackVar, 
        Action, ActionEnum, ActionMap
        )
from pydevmgr_elt import Motor 
from pydevmgr_elt_qt.device.line import QtMenuFeedback 
from enum import Enum, auto 


class MOVE_MODE(int, Enum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2

class MOTOR_COMMAND(int, Enum):
    MOVE_ABS = auto()
    MOVE_REL = auto()
    MOVE_VEL = auto() 
    STOP = auto()
    
val_feedback=QtSelfFeedback.Config()

class Move(QtFormular):
    class Config:
        position =  QtNodeFactory(vtype=(float,0.0),  widget="input_pos_target", format="%.3f",
                feedback=val_feedback
                )
        velocity =  QtNodeFactory(vtype=(float,1.0),  widget="input_velocity",  format="%.3f", 
                feedback=val_feedback
                )
        move_mode = QtNodeFactory( vtype=(MOVE_MODE, MOVE_MODE.ABSOLUTE), widget="move_mode") 
        feedback: FeedbackVar = QtTextFeedback( node=QtNodeFactory(vtype=str, widget="rpc_feedback")) 

    def link_action(self, motor: Motor)->None:

        def move(mode, pos, vel):
            if mode ==  MOVE_MODE.ABSOLUTE:
                motor.move_abs(pos, vel)
            elif mode == MOVE_MODE.RELATIVE:
                motor.move_rel(pos, vel)
            elif mode == MOVE_MODE.VELOCITY:
                motor.move_vel(vel)
        
        feedback = self.feedback  
        self.set_action( Action( move, [self.move_mode, self.position, self.velocity], feedback=feedback ) )

class MoveAbs(QtFormular):
    class Config:
        feedback: FeedbackVar  = Move.feedback
        position = Move.position
        velocity = Move.velocity 
    
    def link_action(self, motor: Motor)->None:
        self.set_action( Action( motor.move_abs, [self.position, self.velocity], feedback=self.feedback ) )

class MoveRel(QtFormular):
    class Config:
        feedback: FeedbackVar = Move.feedback
        position = Move.position
        velocity = Move.velocity 

    def link_action(self, motor: Motor)->None:
        self.set_action( Action( motor.move_rel, [self.position, self.velocity], feedback=self.feedback ) )

class MoveVel(QtFormular):
    class Config:
        feedback: FeedbackVar = Move.feedback
        velocity = Move.velocity 
    def link_action(self, motor: Motor)->None:
        self.set_action( Action( motor.move_vel, [self.velocity], feedback=self.feedback ) )



class MotorCommands(QtFormular):
    class Config:
        menu = QtNodeFactory( vtype=MOTOR_COMMAND, widget="state_action")
        feedback: Optional[FeedbackVar] = QtMenuFeedback.Config( node=QtNodeFactory( vtype=str ,widget="state_action"))
        
        velocity = Move.velocity
        position = Move.position 
        pairing_type = PairingType.none
        
    def link_action(self, motor: Motor)->None:
        feedback = self.feedback 

        def reset_menu():
            self.actioner.setCurrentIndex(0)
        
        motor_action = ActionEnum( after=reset_menu)
        motor_action.add_action( 
                    MOTOR_COMMAND.MOVE_ABS, 
                    Action(motor.move_abs, [self.position, self.velocity], feedback=feedback)
                    )
        motor_action.add_action( 
                    MOTOR_COMMAND.MOVE_REL, 
                    Action(motor.move_rel, [self.position, self.velocity], feedback=feedback)
                    )
        motor_action.add_action( 
                    MOTOR_COMMAND.MOVE_VEL, 
                    Action(motor.move_vel, [self.velocity], feedback=feedback)
                    )
        motor_action.add_action( 
                    MOTOR_COMMAND.STOP, 
                    Action(motor.stop, [], feedback=feedback)
                )
        self.set_action( motor_action) 

class MoveByName(QtFormular):
    class Config:
        velocity =  Move.velocity 
        feedback: FeedbackVar = Move.feedback 

    def link_action(self, motor:Motor):
        feedback = self.feedback
        def reset_menu():
            self.actioner.setCurrentIndex(0)

        self.actioner.addItems( [""]+list(motor.posnames) )
        posname_action = ActionMap( after= reset_menu )
        for posname in motor.posnames:
            posname_action.add_action( posname, Action( motor.move_name, [posname, self.velocity], feedback=feedback ))
        self.set_action( posname_action )   

class Stop(QtFormular):
    class Config:
        feedback: FeedbackVar = Move.feedback 

    def link_action(self, motor:Motor)->None:
        self.set_action( Action( motor.stop, feedback=self.feedback) )


class DownloadFromPlc(QtFormular):
    """ Action attached to a parent with a .cfg interface  

    All nodes in the cfg interface must have the .input attribute 

    This will update all `node`.input value from PLC    
    """
    class Config:
        cfg : QtInterface.Config 
        pairing_type = PairingType.none # stop any connection here 

    def link_action(self, motor):

        pairs = self.cfg.get_node_pairs( motor.cfg  , pairing_type =PairingType.source )
        pairs = [ (n, w.input) for n,w in pairs]
        c = Connector()
        c.add_node_pairs( pairs)        
        action = Action(c.update)
        # action = Action( lambda :print(pairs) )
        self.set_action( action )

        
class UploadToPlc(QtFormular):
    """ Upload plc node from a parent with the .cfg attribute containing nodes """ 
    class Config:
        cfg : QtInterface.Config  
        pairing_type = PairingType.none # stop any connection here 

    def link_action(self, motor):
        
        pairs = self.cfg.get_node_pairs(
                    motor.cfg, 
                    pairing_type=PairingType.target 
                )
        
        c = Connector()
        c.add_node_pairs( pairs) 

        action = Action(c.update)
        # action = Action( lambda :print(pairs) )
        self.set_action( action )


class LoadInitialConfig(QtFormular):
    """ Modify inputs of parent.cfg with device configuration 
    
    """
    class Config:
        cfg : QtInterface.Config 
        pairing_type = PairingType.none # stop any connection here 

    def link_action(self, motor):
        pairs = self.cfg.get_node_pairs( motor.cfg , pairing_type=PairingType.source )
        def update():
            cfg = motor.get_configuration()
            values = {w.input:cfg[n] for n,w in pairs if n in cfg}
            upload(values)
            self.get_parent().refresh()

        self.set_action( Action(update)) 
        

