from modules import motion
from modules.errors import ThrowPinNotConfigured
import time
import cv2

from modules.camera import Camera, SrcAvailability, SrcNotFound

if __name__ == '__main__':
    bot = motion.Motion()

    camDevices = SrcAvailability()
    #print( camDevices.getDeviceList() )

    ls_camera_src = 0
    rs_camera_src = 2

    # define cameras
    rightCamera = Camera( ls_camera_src )
    leftCamera  = Camera( rs_camera_src )

    try:
        """
        TEST
        """
        bot.setup()

        Camera.src_exists( ls_camera_src )
        Camera.src_exists( rs_camera_src )

        rightCamera.setup()
        leftCamera.setup()

        while True:
            print('in loop')
            cam1_ret, cam1_frame = rightCamera.get_frame()
            time.sleep(0.2)
            cam2_ret, cam2_frame = leftCamera.get_frame()

            #Camera.preview(cam1_frame, 'right')
            #Camera.preview(cam2_frame, 'left')

            print( cam1_frame )
            print( cam2_frame )

            if cv2.waitKey(1) & 0xFF == ord("q"):   
                break

        # speed = 50
        # bot._motorLeft(1, 1 , speed)
        # bot._motorRight( 1, 1, speed )
        # time.sleep(20)
        # bot._motorLeft(1, 0 , speed)
        # bot._motorRight( 1, 0, speed )
        # time.sleep(1)
        # bot._motorLeft(1, 1 , speed)
        # bot._motorRight( 1, 1, speed )
        # time.sleep(1)
        # bot._motorLeft(1, 0 , speed)
        # bot._motorRight( 1, 0, speed )

    except SrcNotFound as ex:
        print( ex )
    except ThrowPinNotConfigured:
        print( 'Motor pins not defined' )
    except KeyboardInterrupt:
        print('STOPING')
    finally:
        leftCamera.release()
        rightCamera.release()
        bot._io_cleanup()
