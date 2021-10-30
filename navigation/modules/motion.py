#!/usr/bin/env  python3

from config import *
from modules.errors import *
import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

FORWARD_DR = 'forward'
BACKWARD_DR= 'backward'
DR_NO      = 'no'

TURN_RIGHT = 'right'
TURN_LEFT  = 'left'

class Motion():
    motor_a_en = None
    motor_a_pin1 = None
    motor_a_pin2 = None
    
    motor_b_en = None
    motor_b_pin1 = None
    motor_b_pin2 = None

    pwm_A = 0
    pwm_B = 0

    FORWARD = 1
    BACKWARD= 0

    left_fw = 1
    left_bw = 0

    right_fw= 1
    right_bw= 0

    def __init__(self):
        pass

    def stop(self):
        self._stop_drive('A')
        self._stop_drive('B')

    def _stop_drive(self, motor ):
        if motor == 'A':
            GPIO.output( self.motor_a_pin1, GPIO.LOW )
            GPIO.output( self.motor_a_pin2, GPIO.LOW )
            GPIO.output( self.motor_a_en, GPIO.LOW )
        elif motor == 'B':
            GPIO.output( self.motor_b_pin1, GPIO.LOW )
            GPIO.output( self.motor_b_pin2, GPIO.LOW )
            GPIO.output( self.motor_b_en, GPIO.LOW )
        else:
            pass


    def setup(self):
        for var in ENV:
            if 'MOTOR' in var:
                if int(ENV[var]) < 0:
                    raise ThrowPinNotConfigured('pins not configured')
        
        self.motor_a_en = MOTOR_A_EN
        self.motor_a_pin1 = MOTOR_A_PIN1
        self.motor_a_pin2 = MOTOR_A_PIN2

        self.motor_b_en = MOTOR_B_EN
        self.motor_b_pin1 = MOTOR_B_PIN1
        self.motor_b_pin2 = MOTOR_B_PIN2

        GPIO.setup( self.motor_a_en, GPIO.OUT )
        GPIO.setup( self.motor_b_en, GPIO.OUT )

        GPIO.setup( self.motor_a_pin1, GPIO.OUT )
        GPIO.setup( self.motor_a_pin2, GPIO.OUT )
        GPIO.setup( self.motor_b_pin1, GPIO.OUT )
        GPIO.setup( self.motor_b_pin2, GPIO.OUT )

        self.stop()
        try:
            self.pwm_A = GPIO.PWM( self.motor_a_en, 1000 )
            self.pwm_B = GPIO.PWM( self.motor_b_en, 1000 )
        except:
            pass
        
    def _motorLeft(self, status, dir, speed):
        """
        MotorLeft
        """
        if status == 0: # stop
            self._stop_drive('B')
        else:
            if dir == self.BACKWARD:
                GPIO.output( self.motor_b_pin1, GPIO.HIGH )
                GPIO.output( self.motor_b_pin2, GPIO.LOW )
                self.pwm_B.start(100)
                self.pwm_B.ChangeDutyCycle(speed)
            elif dir == self.FORWARD:
                GPIO.output( self.motor_b_pin1, GPIO.LOW )
                GPIO.output( self.motor_b_pin2, GPIO.HIGH )
                self.pwm_B.start( 0 )
                self.pwm_B.ChangeDutyCycle(speed)

    def _motorRight(self, status, dir, speed):
        """
        MotorRight
        """
        if status == 0: # stop
            self._stop_drive('A')
        else:
            if dir == self.BACKWARD:
                GPIO.output( self.motor_a_pin1, GPIO.HIGH )
                GPIO.output( self.motor_a_pin2, GPIO.LOW )
                self.pwm_A.start(100)
                self.pwm_A.ChangeDutyCycle(speed)
            elif dir == self.FORWARD:
                GPIO.output( self.motor_a_pin1, GPIO.LOW )
                GPIO.output( self.motor_a_pin2, GPIO.HIGH )
                self.pwm_A.start(0)
                self.pwm_A.ChangeDutyCycle(speed)

    def move(self, speed, dir, turn, radius=0.6):
        """
        RobotDrive
        """
        if dir == FORWARD_DR:
            if turn == TURN_RIGHT:
                self._motorLeft( 0, self.left_fw, int( speed * radius ) )
                self._motorRight( 1, self.right_fw, speed )
            elif turn == TURN_LEFT:
                self._motorLeft( 1, self.left_fw, speed )
                self._motorRight( 0, self.right_bw, int( speed * radius ) )
            else:
                self._motorLeft( 1, self.left_fw, int( speed * radius ) )
                self._motorRight( 1, self.right_bw, speed )
        elif dir == BACKWARD_DR:
            if turn == TURN_RIGHT:
                self._motorLeft( 0, self.left_fw, int( speed*radius ) )
                self._motorRight( 1, self.right_bw, speed )
            elif turn == TURN_LEFT:
                self._motorLeft( 1, self.left_bw, speed )
                self._motorRight( 0, self.right_fw, int( speed * radius ) )
            else:
                self._motorLeft( 1, self.left_bw, speed )
                self._motorRight( 1, self.right_bw, speed )
        elif dir == DR_NO:
            if turn == TURN_RIGHT:
                self._motorLeft( 1, self.left_bw, speed )
                self._motorRight( 1, self.right_fw, speed )
            elif turn == TURN_LEFT:
                self._motorLeft( 1, self.left_fw, speed )
                self._motorRight( 1, self.right_bw, speed )
            else:
                self.stop()
        else:
            pass

    def _io_cleanup(self):
        self.stop()
        GPIO.cleanup()
        print("IO CLEANED")