from modules import motion
from modules.errors import ThrowPinNotConfigured
import time
import cv2
from imutils.video import VideoStream
import imutils

from modules.camera import Camera, CameraThread, CameraTimeout, SrcAvailability, SrcNotFound

if __name__ == '__main__':
    bot = motion.Motion()

    camDevices = SrcAvailability()
    #print( camDevices.getDeviceList() )

    ls_camera_src = 0
    rs_camera_src = 2

    # define cameras
    # rightCamera = Camera( ls_camera_src )
    # leftCamera  = Camera( rs_camera_src )

    # rightCameraT = CameraThread( "rightCam", rs_camera_src )
    # leftCameraT  = CameraThread( "leftCamera", ls_camera_src )

    try:
        """
        TEST
        """
        bot.setup()

        Camera.src_exists( ls_camera_src )
        Camera.src_exists( rs_camera_src )

        #rightCamera.setup()
        #leftCamera.setup()

        # rightCameraT.start()
        # leftCameraT.start()

        cam1 = VideoStream( src=ls_camera_src ).start()
        cam2 = VideoStream( src=rs_camera_src ).start()

        time.sleep(0.2)

        while True:
            frames = []

            print('frames')

            for stream in [ cam1, cam2 ]:
                print(stream)
                frame = stream.read()
                frame = imutils.resize(frame, width=400)

                print(frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("1"):
                break
            

        cam1.stop()
        cam2.stop()
        

        # cameraThreadReady = False
        # now = time.time()
        # while not rightCameraT.isAlive() and not leftCameraT.isAlive():
        #     print(".")
        #     curr = time.time()
        #     difference = int( now - curr )
        #     if difference == 30:
        #         raise CameraTimeout('Camera connection timeout, reached 30sec')

        # cameraThreadReady = True

        # while cameraThreadReady:
        #     if rightCameraT.cameraReady() and leftCameraT.cameraReady():
        #         print('in loop')
        #         # cam1_ret, cam1_frame = rightCamera.get_frame()
        #         # time.sleep(0.2)
        #         # cam2_ret, cam2_frame = leftCamera.get_frame()

        #         #Camera.preview(cam1_frame, 'right')
        #         #Camera.preview(cam2_frame, 'left')

        #         # print( cam1_frame )
        #         # print( cam2_frame )

        #         # if cv2.waitKey(1) & 0xFF == ord("q"):   
        #         #     break

        #         ret1, image1 = rightCameraT.getFrame()
        #         #ret2, image2 = leftCameraT.getFrame()

        #         print(image1)
        #         #print( image2 )

        # # speed = 50
        # # bot._motorLeft(1, 1 , speed)
        # # bot._motorRight( 1, 1, speed )
        # # time.sleep(20)
        # # bot._motorLeft(1, 0 , speed)
        # # bot._motorRight( 1, 0, speed )
        # # time.sleep(1)
        # # bot._motorLeft(1, 1 , speed)
        # # bot._motorRight( 1, 1, speed )
        # # time.sleep(1)
        # # bot._motorLeft(1, 0 , speed)
        # # bot._motorRight( 1, 0, speed )

    except SrcNotFound as ex:
        print( ex )
    except ThrowPinNotConfigured:
        print( 'Motor pins not defined' )
    except KeyboardInterrupt:
        print('STOPING')
    finally:
        #leftCamera.release()
        #rightCamera.release()
        #rightCameraT.stop()
        #leftCameraT.stop()
        bot._io_cleanup()
