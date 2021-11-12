"""
Camera calibration script
"""
import time
import cv2
from modules.camera import Camera
from config import camera_config


leftCam = Camera( 'left', camera_config['left_cam_src'], camera_config['left_cam_config'] )
rightCam= Camera( 'right', camera_config['right_cam_src'], camera_config['right_cam_config'] )

leftCam.start()
rightCam.start()
time.sleep(0.2)

frame_index = 0
while True:
    full_frame = []
    for stream in [ leftCam, rightCam ]:
        frame = stream.get_frame()
        if frame is not None:
            frame = stream.stabalized( frame )
            frame = stream.resize( frame )
            full_frame.append( frame )

    if len( full_frame ) == 2:
        if cv2.waitKey(0) & 0xFF == ord('s'):
            leftImage = full_frame[0]
            rightImage= full_frame[1]
            image_name = "./calibration/{name}_{index}.png".format( name='lt', index=frame_index )
            cv2.imwrite( image_name, leftImage )

            image_name = "./calibration/{name}_{index}.png".format( name='rt', index=frame_index )
            cv2.imwrite( image_name, rightImage )

            print( "<< IMAGE SAVED >>" )
            full_frame = []
            frame_index+=1
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

leftCam.stop()
rightCam.stop()