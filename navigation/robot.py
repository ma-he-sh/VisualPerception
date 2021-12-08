#!/usr/bin/env python3

from requests import status_codes
from modules.errors import ThrowPinNotConfigured
from config import *
import time
import cv2
from imutils.video import VideoStream
import imutils
import socket
import numpy as np
import requests

from motion.motion import Motion
from modules.camera import Camera, CameraThread, CameraTimeout, FullFrame, SrcAvailability, SrcNotFound
from config import DEV_MODE

# gives a list of availble cameras
#src = SrcAvailability()
#deviceList = src.getDeviceList()
#print( deviceList )

# create rectified image for views
cvFile = cv2.FileStorage( CAMERA_CONFIGS_STEREO_MAP, cv2.FILE_STORAGE_READ )
ltStereoMapX = cvFile.getNode("LTStereoMapX").mat()
ltStereoMapY = cvFile.getNode("LTStereoMapY").mat()
rtStereoMapX = cvFile.getNode("RTStereoMapX").mat()
rtStereoMapY = cvFile.getNode("RTStereoMapY").mat()
cvFile.release()

if not STEREO_VISION:
	raise Exception("NEED TO RUN THE SCRIPT WITH STEREO CAMERAS")

MIN_DISTANCE_RANGE=15.0
MAX_DISTANCE_RANGE=40.0
MAP_ID="cc655ff3-5a7f-4779-b5d0-095f75c26bdb"

class HandleDistance():
    @staticmethod
    def is_obstacle( disparity=0 ):
        ref_distance =  -0.0153*disparity + 1.03
        if MIN_DISTANCE_RANGE <= ref_distance <= MAX_DISTANCE_RANGE:
            return True, ref_distance
        return False, ref_distance

    @staticmethod
    def send_robot_pos( map_id, robot_x, robot_y, obs_x, obs_y ):
        submit_data = {
            "robot_x": robot_x,
            "robot_y": robot_y,
            "map_id" : map_id,
            "obs_x"  : obs_x,
            "obs_y"  : obs_y
        }
        resp = requests.post("127.0.0.1/set_robot_pos", data=submit_data )
        if resp.status_code == 200:
            print("REQUEST SUCCESS")

    @staticmethod
    def get_commands( map_id ):
        cmd_list = []
        command_file = map_id + ".txt"
        fcmd = open(command_file, "r")
        commands = fcmd.readlines()
        for cmd in commands:
            if cmd:
                data = cmd.split(",")
                if len(data):
                    from_pos = cmd
                    cmd_list.append({
                        'from_x': data[0],
                        'from_y': data[1],
                        'distance': float(data[2]),
                        'turn': data[3],
                        'angle': float(data[4])
                    })   

        return cmd_list

# prepare stereo vison components
stereo = cv2.StereoSGBM_create(
	numDisparities=NUM_DISPARITIES,
	blockSize=WINDOW_SIZE,
	uniquenessRatio=UNIQUENESS_RATIO,
	speckleWindowSize=SPECKLE_WINDOW_SIZE,
	speckleRange=SPECKLE_RANGE,
	disp12MaxDiff=DISP_12_MAX_DIFF,
	P1=P1_VAL,
	P2=P2_VAL
)

# create disparity for right camera
stereoR=cv2.ximgproc.createRightMatcher(stereo)

kernel= np.ones((3,3),np.uint8)

# create WLS filter
WLS_FILTER=cv2.ximgproc.createDisparityWLSFilter(matcher_left=stereo)
WLS_FILTER.setLambda( WLS_LAMDA )
WLS_FILTER.setSigmaColor( WLS_SIGMA )

class RobotHandler():
    def __init__(self, robot_config={}, camera_config={}):
        self.robot_config = robot_config
        self.camera_config= camera_config
        self.bot = Motion( robot_config['dev_mode'] )
        self.cam1= Camera( 'left', camera_config['left_cam_src'], camera_config['left_cam_config'] )
        self.cam2= Camera( 'right', camera_config['right_cam_src'], camera_config['right_cam_config'] )

    def initialize(self):
        print( "======ROBOT INITIALIZE======" )
        try: 
            """
            Initize the robot
            """
            self.bot.setup()

            # camera src validate
            Camera.src_exists( self.camera_config['left_cam_src'] )
            Camera.src_exists( self.camera_config['right_cam_src'] )

            # let the camera warmup
            print("Preparing webcams :: warming up")
            self.cam1.start()
            self.cam2.start()
            time.sleep( 0.2 )

            get_new_cmd = True
            cmd_list    = []
            curr_distance = 0
            curr_pos_x  = 0
            curr_pos_y  = 0

            while True:
                if get_new_cmd:
                    cmd_list = HandleDistance.get_commands( MAP_ID )
                    if len(cmd_list) <= 0:
                        get_new_cmd = True
                    else:
                        get_new_cmd = False

                full_frame = []
                gray_frame = []

                for stream in [ self.cam1, self.cam2 ]:
                    frame = stream.get_frame()
                    if frame is not None:
                        frame = stream.stabalized( frame )
                        frame = stream.resize( frame )
                        cv2.normalize(frame, frame, 0, 255, cv2.NORM_MINMAX )
                        # debug
                        #stream.write_to_disk( frame )

                        # frame 
                        full_frame.append( frame )
                        # gray image frame
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        gray_frame.append( gray )

                if len( full_frame ) == 2:
                    nav_image = FullFrame( full_frame[0], full_frame[1] )
                    # debug
                    #nav_image.write_to_disk()

                    leftImage = full_frame[0]
                    #leftImage = cv2.remap( leftImage, ltStereoMapX, ltStereoMapY, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0 )
                    leftGrayImage = gray_frame[0]
                    #leftGrayImage = cv2.remap( leftGrayImage, ltStereoMapX, ltStereoMapY, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0 )
                    
                    rightImage= full_frame[1]
                    #rightImage = cv2.remap( rightImage, rtStereoMapX, rtStereoMapY, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0 )
                    rightGrayImage= gray_frame[1]
                    #rightGrayImage = cv2.remap( rightGrayImage, rtStereoMapX, rtStereoMapY, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0 )s

                    # full stereo image
                    visual = np.concatenate( ( leftImage, rightImage ), axis=1 )

                    # compute the images for depth map
                    disparityL = stereo.compute( leftGrayImage, rightGrayImage )
                    disparityR = stereoR.compute( rightGrayImage, leftGrayImage )

                    # apply wls filter to smooth the disparity layers
                    filterImageWLS = WLS_FILTER.filter( disparityL, leftGrayImage, None, disparityR )
                    filterImageWLS = cv2.normalize(src=filterImageWLS, dst=filterImageWLS, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX)
                    filterImageWLS = np.uint8(filterImageWLS)

                    disp= ((disparityL.astype(np.float32)/ 16)-MIN_DISPARITY)/NUM_DISPARITIES

                    # validate the distance
                    is_obstacle, obs_distance = HandleDistance.is_obstacle( disp )
                    if is_obstacle:
                        robot_x = curr_pos_x
                        robot_y = curr_pos_y
                        obs_x   = robot_x + obs_distance
                        obs_y   = robot_y + obs_distance

                        # send command with current robot pos and approximated obstacle pos
                        HandleDistance.send_robot_pos( MAP_ID, robot_x, robot_y, obs_x, obs_y )
                    else:
                        # driver robot
                        if len(cmd_list) > 0:
                            cmd = cmd_list.pop(0) # get current top cmd
                            if cmd is not None:
                                if curr_distance < cmd['distance']:
                                    req_angle = abs(cmd['angle'])

                                    if cmd['turn'] == "_no_turn":
                                        self.bot.driveRobot( cmd['distance'] )
                                    elif cmd['turn'] == "_right":
                                        if req_angle == 135:
                                            self.bot.turn135Right()
                                        elif req_angle == 90:
                                            self.bot.turn90Right()
                                        elif req_angle == 45:
                                            self.bot.turn45Right()
                                    elif cmd['turn'] == "_left":
                                        if req_angle == 135:
                                            self.bot.turn135Left()
                                        elif req_angle == 90:
                                            self.bot.turn90Left()
                                        elif req_angle == 45:
                                            self.bot.turn45Left()
                                    else:
                                        self.bot.stop()
                                
                                curr_distance = cmd['distance']
                                curr_pos_x =  cmd['from_x']
                                curr_pos_y =  cmd['from_y']
                        else:
                            self.bot.stop() # stop robot
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

        except SrcNotFound as ex:
            print( '<< ' + ex + ' >>' )
        except ThrowPinNotConfigured:
            print( '<< Motor pins are not defined  >>' )
        except KeyboardInterrupt:
            print( '<< Interrupted by keyboard >>' )
        finally:
            self.cam1.stop()
            self.cam2.stop()
            self.bot._io_cleanup()




# DEBUG CODE
#if __name__ == '__main__':
#    robot_config = {
#        'dev_mode' : DEV_MODE
#    }
#    robotHandler = RobotHandler(robot_config, camera_config)
#    robotHandler.initialize()


# if __name__ == '__main__':
#      #robotHandler = RobotHandler({}, camera_config)
#      #robotHandler.initialize()


#      bot = Motion()
#      try:
#          bot.setup()


#          speed = 100
        
#          #bot._motorLeft(1, 1, speed )
#          #bot._motorRight(1, 1, speed )
#          #time.sleep( 2 )
        
#          # pos 600, 600, dest 880, 600
#          bot.turn45Right() 
#          bot.driveRobot( 80 )
#          bot.turn45Left()
#          bot.driveRobot( 20 )
#          bot.turn45Left()
#          bot.driveRobot( 50 )

#          """
#          bot.turn45Right()
#          bot.driveRobot( 80 )
#          bot.turn45Left()
#          bot.driveRobot( 10 )
#          #----
#          bot.stop()
#          time.sleep(2)
#          bot.turn45Left()
#          bot.driveRobot( 23 )
#          bot.turn45Right()
#          bot.driveRobot( 20 )
#          bot.turn45Left()
#          bot.driveRobot( 23 )
#          """

# #         #bot.turn90Left()
# #         #bot.turn45Left()
# #         #bot.turn180()

# #         bot.turn180()

# #         #bot.driveRobot( 1 )
# #         #bot.driveRobot( -100 )

# #         #bot._motorLeft(1, 0 , speed)
# #         #bot._motorRight( 1, 0, speed )
# #         #time.sleep(0.43)
# #         #bot._motorLeft(1, 1 , speed)
# #         #bot._motorRight( 1, 1, speed )
# #         #time.sleep(1)
# #         #bot._motorLeft(1, 0 , speed)
# #         #bot._motorRight( 1, 0, speed )

# #         #bot.move( speed, 'forward', 'right', 90 )
# #         #time.sleep(20)

#      except KeyboardInterrupt:
#          print('exiting');
#      finally:
#          bot._io_cleanup()

# #     # #camDevices = SrcAvailability()
# #     # #print( camDevices.getDeviceList() )

# #     # ls_camera_src = 0
# #     # rs_camera_src = 2

# #     # # define webcams

# #     # try:
# #     #     """
# #     #     TEST
# #     #     """
# #     #     bot.setup()

# #     #     # Camera.src_exists( ls_camera_src )
# #     #     # Camera.src_exists( rs_camera_src )

# #     #     # #rightCamera.setup()
# #     #     # #leftCamera.setup()

# #     #     # # rightCameraT.start()
# #     #     # # leftCameraT.start()

# #     #     # cam1 = VideoStream( src=ls_camera_src ).start()
# #     #     # cam2 = VideoStream( src=rs_camera_src ).start()

# #     #     # time.sleep(0.2)

# #     #     # while True:
# #     #     #     frames = []

# #     #     #     print('frames')

# #     #     #     for stream in [ cam1, cam2 ]:
# #     #     #         print(stream)
# #     #     #         frame = stream.read()
# #     #     #         frame = imutils.resize(frame, width=400)

# #     #     #         print(frame)
# #     #     #         cv2.imshow( "preview", frame )

# #     #     #     key = cv2.waitKey(1) & 0xFF
# #     #     #     if key == ord("1"):
# #     #     #         break
            

# #     #     # cam1.stop()
# #     #     # cam2.stop()
        

# #     #     # # cameraThreadReady = False
# #     #     # # now = time.time()
# #     #     # # while not rightCameraT.isAlive() and not leftCameraT.isAlive():
# #     #     # #     print(".")
# #     #     # #     curr = time.time()
# #     #     # #     difference = int( now - curr )
# #     #     # #     if difference == 30:
# #     #     # #         raise CameraTimeout('Camera connection timeout, reached 30sec')

# #     #     # # cameraThreadReady = True

# #     #     # # while cameraThreadReady:
# #     #     # #     if rightCameraT.cameraReady() and leftCameraT.cameraReady():
# #     #     # #         print('in loop')
# #     #     # #         # cam1_ret, cam1_frame = rightCamera.get_frame()
# #     #     # #         # time.sleep(0.2)
# #     #     # #         # cam2_ret, cam2_frame = leftCamera.get_frame()

# #     #     # #         #Camera.preview(cam1_frame, 'right')
# #     #     # #         #Camera.preview(cam2_frame, 'left')

# #     #     # #         # print( cam1_frame )
# #     #     # #         # print( cam2_frame )

# #     #     # #         # if cv2.waitKey(1) & 0xFF == ord("q"):   
# #     #     # #         #     break

# #     #     # #         ret1, image1 = rightCameraT.getFrame()
# #     #     # #         #ret2, image2 = leftCameraT.getFrame()

# #     #     # #         print(image1)
# #     #     # #         #print( image2 )

# #     #     # # # speed = 50
# #     #     # # # bot._motorLeft(1, 1 , speed)
# #     #     # # # bot._motorRight( 1, 1, speed )
# #     #     # # # time.sleep(20)
# #     #     # # # bot._motorLeft(1, 0 , speed)
# #     #     # # # bot._motorRight( 1, 0, speed )
# #     #     # # # time.sleep(1)
# #     #     # # # bot._motorLeft(1, 1 , speed)
# #     #     # # # bot._motorRight( 1, 1, speed )
# #     #     # # # time.sleep(1)
# #     #     # # # bot._motorLeft(1, 0 , speed)
# #     #     # # # bot._motorRight( 1, 0, speed )

# #     # except SrcNotFound as ex:
# #     #     print( ex )
# #     # except ThrowPinNotConfigured:
# #     #     print( 'Motor pins not defined' )
# #     # except KeyboardInterrupt:
# #     #     print('STOPING')
# #     # finally:
# #     #     #leftCamera.release()
# #     #     #rightCamera.release()
# #     #     #rightCameraT.stop()
# #     #     #leftCameraT.stop()
# #     #     bot._io_cleanup()
