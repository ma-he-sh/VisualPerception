#!/usr/bin/env python3

from modules.errors import ThrowPinNotConfigured
from config import camera_config
import time
import cv2
from imutils.video import VideoStream
import imutils
import socket

from modules.camera import Camera, CameraThread, CameraTimeout, FullFrame, SrcAvailability, SrcNotFound
from config import DEV_MODE

# gives a list of availble cameras
#src = SrcAvailability()
#deviceList = src.getDeviceList()
#print( deviceList )

class RobotHandler():
    def __init__(self, robot_config={}, camera_config={}):
        self.robot_config = robot_config
        self.camera_config= camera_config
        #self.bot = motion.Motion( robot_config['dev_mode'] )
        self.cam1= Camera( 'left', camera_config['left_cam_src'], camera_config['left_cam_config'] )
        self.cam2= Camera( 'right', camera_config['right_cam_src'], camera_config['right_cam_config'] )

    def initialize(self):
        print( "======ROBOT INITIALIZE======" )
        try: 
            """
            Initize the robot
            """
            #self.bot.setup()

            # camera src validate
            Camera.src_exists( self.camera_config['left_cam_src'] )
            Camera.src_exists( self.camera_config['right_cam_src'] )

            # let the camera warmup
            print("Preparing webcams :: warming up")
            self.cam1.start()
            self.cam2.start()
            time.sleep( 0.2 )

            while True:
                full_frame = []
                for stream in [ self.cam1, self.cam2 ]:
                    frame = stream.get_frame()
                    if frame is not None:
                        frame = stream.stabalized( frame )
                        frame = stream.resize( frame )
                        # debug
                        #stream.write_to_disk( frame )
                        full_frame.append( frame )

                if len( full_frame ) == 2:
                    nav_image = FullFrame( full_frame[0], full_frame[1] )
                    # debug
                    #nav_image.write_to_disk()
                    full_frame = []

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
            #self.bot._io_cleanup()

if __name__ == '__main__':
    robot_config = {
        'dev_mode' : DEV_MODE
    }
    robotHandler = RobotHandler(robot_config, camera_config)
    robotHandler.initialize()







# if __name__ == '__main__':
#     #robotHandler = RobotHandler({}, camera_config)
#     #robotHandler.initialize()





#     bot = motion.Motion()
#     try:
#         bot.setup()


#         speed = 60
        
#         #bot._motorLeft(1, 0, speed )
#         #bot._motorRight(1, 0, speed )
#         #time.sleep( 0.65 )


#         #bot.turn90Left()
#         #bot.turn45Left()
#         #bot.turn180()

#         bot.turn180()

#         #bot.driveRobot( 1 )
#         #bot.driveRobot( -100 )

#         #bot._motorLeft(1, 0 , speed)
#         #bot._motorRight( 1, 0, speed )
#         #time.sleep(0.43)
#         #bot._motorLeft(1, 1 , speed)
#         #bot._motorRight( 1, 1, speed )
#         #time.sleep(1)
#         #bot._motorLeft(1, 0 , speed)
#         #bot._motorRight( 1, 0, speed )

#         #bot.move( speed, 'forward', 'right', 90 )
#         #time.sleep(20)

#     except KeyboardInterrupt:
#         print('exiting');
#     finally:
#         bot._io_cleanup()

#     # #camDevices = SrcAvailability()
#     # #print( camDevices.getDeviceList() )

#     # ls_camera_src = 0
#     # rs_camera_src = 2

#     # # define webcams

#     # try:
#     #     """
#     #     TEST
#     #     """
#     #     bot.setup()

#     #     # Camera.src_exists( ls_camera_src )
#     #     # Camera.src_exists( rs_camera_src )

#     #     # #rightCamera.setup()
#     #     # #leftCamera.setup()

#     #     # # rightCameraT.start()
#     #     # # leftCameraT.start()

#     #     # cam1 = VideoStream( src=ls_camera_src ).start()
#     #     # cam2 = VideoStream( src=rs_camera_src ).start()

#     #     # time.sleep(0.2)

#     #     # while True:
#     #     #     frames = []

#     #     #     print('frames')

#     #     #     for stream in [ cam1, cam2 ]:
#     #     #         print(stream)
#     #     #         frame = stream.read()
#     #     #         frame = imutils.resize(frame, width=400)

#     #     #         print(frame)
#     #     #         cv2.imshow( "preview", frame )

#     #     #     key = cv2.waitKey(1) & 0xFF
#     #     #     if key == ord("1"):
#     #     #         break
            

#     #     # cam1.stop()
#     #     # cam2.stop()
        

#     #     # # cameraThreadReady = False
#     #     # # now = time.time()
#     #     # # while not rightCameraT.isAlive() and not leftCameraT.isAlive():
#     #     # #     print(".")
#     #     # #     curr = time.time()
#     #     # #     difference = int( now - curr )
#     #     # #     if difference == 30:
#     #     # #         raise CameraTimeout('Camera connection timeout, reached 30sec')

#     #     # # cameraThreadReady = True

#     #     # # while cameraThreadReady:
#     #     # #     if rightCameraT.cameraReady() and leftCameraT.cameraReady():
#     #     # #         print('in loop')
#     #     # #         # cam1_ret, cam1_frame = rightCamera.get_frame()
#     #     # #         # time.sleep(0.2)
#     #     # #         # cam2_ret, cam2_frame = leftCamera.get_frame()

#     #     # #         #Camera.preview(cam1_frame, 'right')
#     #     # #         #Camera.preview(cam2_frame, 'left')

#     #     # #         # print( cam1_frame )
#     #     # #         # print( cam2_frame )

#     #     # #         # if cv2.waitKey(1) & 0xFF == ord("q"):   
#     #     # #         #     break

#     #     # #         ret1, image1 = rightCameraT.getFrame()
#     #     # #         #ret2, image2 = leftCameraT.getFrame()

#     #     # #         print(image1)
#     #     # #         #print( image2 )

#     #     # # # speed = 50
#     #     # # # bot._motorLeft(1, 1 , speed)
#     #     # # # bot._motorRight( 1, 1, speed )
#     #     # # # time.sleep(20)
#     #     # # # bot._motorLeft(1, 0 , speed)
#     #     # # # bot._motorRight( 1, 0, speed )
#     #     # # # time.sleep(1)
#     #     # # # bot._motorLeft(1, 1 , speed)
#     #     # # # bot._motorRight( 1, 1, speed )
#     #     # # # time.sleep(1)
#     #     # # # bot._motorLeft(1, 0 , speed)
#     #     # # # bot._motorRight( 1, 0, speed )

#     # except SrcNotFound as ex:
#     #     print( ex )
#     # except ThrowPinNotConfigured:
#     #     print( 'Motor pins not defined' )
#     # except KeyboardInterrupt:
#     #     print('STOPING')
#     # finally:
#     #     #leftCamera.release()
#     #     #rightCamera.release()
#     #     #rightCameraT.stop()
#     #     #leftCameraT.stop()
#     #     bot._io_cleanup()
