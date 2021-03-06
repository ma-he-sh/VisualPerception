#!/usr/bin/env  python3

from config import *
from modules.errors import *
import time
import RPi.GPIO as GPIO
import math

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

    def __init__(self, mode=0, config={}):
        self.dev_mode = ( mode == 1 )
        pass

    def stop(self):
        if self.dev_mode:
            print('--stop--')
            return

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
        if self.dev_mode:
            print('--demo mode setup--')
            return 

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
        if self.dev_mode:
            print('---motor left--')
            return

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
        if self.dev_mode:
            print('--motor right--')
            return

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
        if self.dev_mode:
            print('--move--')
            return
            
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
   
    def getTimePerDistance(self, _distance ):
        """
        _distance need to defined in cm
        Based on the circumference of the wheel
        C = 2 * PI * R
        C = 2 * PI * ( d / 2 )
        C = 2 * PI * 6.5
        C = 20.42

        It takes 0.43 seconds for 1 rev
        time = ( _distance / C ) * 0.43
        """

        # @TODO need to tweak these
        time_constant = TIME_FOR_REV # per rev
        wheel_diameter= WHEEL_DIAMETER# in cm
        speed         = ROBOT_SPEED   # speed need to be a constant

        C = 2 * math.pi * ( wheel_diameter / 2 )
        return speed, ( _distance / C ) * time_constant
   
    def driveRobot(self, _distance ):
        if self.dev_mode:
            print('--drive robot--')
            return

        # calculate total time need to travel
        
        dir = 1     # forward
        if _distance < 0:
            dir = 0 # backward

        speed, calc_time = self.getTimePerDistance( abs(_distance) )

        self._motorLeft(1, dir, speed )
        self._motorRight(1, dir, speed )
        
        time.sleep( calc_time )

    def moveForward(self, _distance):
        if self.dev_mode:
            print('--move forward--')
            return

        # move forward given the distance
        speed, calc_time = self.getTimePerDistance( _distance )

        self._motorLeft( 1, 1, speed )
        self._motorRight( 1, 1, speed )

        time.sleep( calc_time )

    def moveBackward(self, _distance ):
        if self.dev_mode:
            print('--move backward--')
            return

        # calculate total time need to travel
        speed, calc_time = self.getTimePerDistance( _distance )

        self._motorLeft(1, 0, speed )
        self._motorRight(1, 0, speed )

        time.sleep( calc_time )

    def turnRight(self, speed, _time ):
        if self.dev_mode:
            print('--turn right--')
            return

        self._motorLeft(1, 0, speed )
        self._motorRight( 1, 1, speed )
        time.sleep( _time )

    def turnLeft(self, speed, _time ):
        if self.dev_mode:
            print('--turn left--')
            return

        self._motorLeft(1, 1, speed )
        self._motorRight( 1, 0, speed )
        time.sleep( _time )

    def turn90Left(self):
        if self.dev_mode:
            print('--turn 90 left--')
            return

        speed = ROBOT_SPEED
        self.turnLeft( speed, TIME_FOR_90 )

    def turn45Left(self):
        if self.dev_mode:
            print('--turn 45 left--')
            return

        speed = ROBOT_SPEED
        self.turnLeft( speed, TIME_FOR_45 )
   
    def turn90Right(self):
        if self.dev_mode:
            print('--turn 90 right--')
            return

        speed = ROBOT_SPEED
        self.turnRight( speed, TIME_FOR_90 )

    def turn135Left(self):
        if self.dev_mode:
            print('--turn 135 left--')
            return

        speed = ROBOT_SPEED
        self.turnLeft( speed, TIME_FOR_135 )
   
    def turn135Right(self):
        if self.dev_mode:
            print('--turn 135 right--')
            return

        speed = ROBOT_SPEED
        self.turnRight( speed, TIME_FOR_135 )

    def turn45Right(self):
        if self.dev_mode:
            print('--turn 45 right--')
            return

        speed = ROBOT_SPEED
        self.turnRight( speed, TIME_FOR_45 )
    
    def turn180(self):
        if self.dev_mode:
            print('--turn 180 --')
            return

        speed = ROBOT_SPEED
        self.turnLeft( speed, TIME_FOR_180 )

    def _io_cleanup(self):
        self.stop()
        GPIO.cleanup()
        print("IO CLEANED")
