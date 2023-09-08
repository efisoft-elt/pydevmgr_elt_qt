from pydevmgr_qt import ( 
        QtFormular,  
        QtNodeFactory,
        QtSelfFeedback, 
    )
from pydevmgr_elt import Adc 
from pydevmgr_qt.api import Action, ActionEnum
from pydevmgr_elt_qt.motor.actions import MotorCommands as MotorMoveFromMenu, MOVE_MODE
from enum import Enum, auto 


class AXES(int, Enum):
    BOTH  = 0
    AXIS1  = 1
    AXIS2 = 2

class ADC_COMMAND(str, Enum):
    START_TRACK = auto()
    STOP_TRACK  = auto()
    MOVE_ANGLE = auto() 
    

class StartTrack(QtFormular):
    class Config:
        angle = QtNodeFactory(vtype=float, widget="input_angle") 
   
    def link_action(self, adc: Adc):
        track = Action( adc.start_track, [self.angle], 
                       feedback=self.feedback  
            )
        self.set_action( track )

class StopTrack(QtFormular):
    def link_action( self, adc:Adc):
        stop = Action(adc.stop_track, feedback=self.feedback)
        self.set_action(stop)

class MoveAngle(QtFormular):
    class Config:
        angle = QtNodeFactory(vtype=float, widget="input_angle") 
         
    def link_action(self, adc:Adc):
        move = Action(adc.move_angle, [self.angle], feedback = self.feedback)
        self.set_action( move) 



val_feedback=QtSelfFeedback.Config()

class Move(QtFormular): 
    class Config:
        mode =QtNodeFactory(vtype=MOVE_MODE, widget="move_mode")
        axis = QtNodeFactory(vtype=(AXES,AXES.BOTH), widget="input_axis")
        position = QtNodeFactory(vtype=(float,0.0),  widget="input_pos_target", format="%.3f",
                feedback=val_feedback
                )
        velocity =  QtNodeFactory(vtype=(float,1.0),  widget="input_velocity",  format="%.3f", 
                feedback=val_feedback
            )
    def link_action(self, adc: Adc)->None:

        def move(mode, axis, pos, vel):
            if mode ==  MOVE_MODE.ABSOLUTE:
                adc.move_abs(axis, pos, vel)
            elif mode == MOVE_MODE.RELATIVE:
                adc.move_rel(axis, pos, vel)
            elif mode == MOVE_MODE.VELOCITY:
                adc.move_vel(axis, vel)
        feedback = self.feedback  
        self.set_action( 
                Action( move, 
                        [self.mode, self.axis, self.position, self.velocity], 
                        feedback=feedback 
                    )
                )

   

class AdcCommands(QtFormular):
    class Config:
        angle = StartTrack.angle 
        
        menu_adc = QtNodeFactory(vtype=ADC_COMMAND, widget="state_action") 

    def link_action(self, adc: Adc)->None:

        def reset_menu():
            self.actioner.setCurrentIndex(0)
        
        adc_action = ActionEnum( after=reset_menu)
        adc_action.add_action( 
                    ADC_COMMAND.MOVE_ANGLE, 
                    Action( adc.move_angle, 
                           [self.angle], 
                           feedback=self.feedback
                    )
                )

        adc_action.add_action( 
                    ADC_COMMAND.START_TRACK, 
                    Action( adc.start_track, 
                           [self.angle], 
                           feedback=self.feedback
                    )
                )
        adc_action.add_action( 
                    ADC_COMMAND.STOP_TRACK, 
                    Action(adc.stop_track, 
                           feedback=self.feedback
                    )
                )
        self.set_action(adc_action) 

