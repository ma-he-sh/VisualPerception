"""
Camera calibration capture script
"""
import time
from typing import final

from numpy.lib.index_tricks import index_exp
import cv2
import numpy as np
from modules.camera import Camera, SrcAvailability
from modules.helpers import create_paths
from config import camera_config, STEREO_VISION

# gives a list of availble cameras
src = SrcAvailability()
deviceList = src.getDeviceList()
print( deviceList )

# create dirs if not exists
CALIBRATION_PATH = "./calibrations"
create_paths( CALIBRATION_PATH )

leftCam = None
rightCam= None
mainCam = None

chessBoardSize = ( 8, 6 )
frameSize      = ( 480, 640 )
winSize        = (11,11)
zerorZone      = (-1, -1)

criteria = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001 )

if STEREO_VISION:
    leftCam = Camera( 'left', camera_config['left_cam_src'], camera_config['left_cam_config'] )
    rightCam= Camera( 'right', camera_config['right_cam_src'], camera_config['right_cam_config'] )

    leftCam.start()
    rightCam.start()
    time.sleep(0.2)
else:
    """
    USE TEST CAMERA
    """
    print("normal camera")
    mainCam = Camera( 'main', 0 )
    mainCam.start()
    time.sleep(0.2)

frame_index = 0
try:
    camera_list = []
    if STEREO_VISION:
        camera_list.append( leftCam )
        camera_list.append( rightCam )
    else:
        camera_list.append( mainCam )

    while True:
        full_frame = []
        for stream in camera_list:
            image = stream.get_frame()
            if image is not None:
                frame = stream.stabalized( image )
                frame = stream.resize( frame )
                cv2.normalize( frame, frame, 0, 255, cv2.NORM_MINMAX )
                full_frame.append( frame )
        
        if len( full_frame ) > 0:
            if STEREO_VISION:
                leftImage = full_frame[0]
                rightImage= full_frame[1]

                origLeftImage = leftImage.copy()
                origRightImage= rightImage.copy()

                leftGrayImage = cv2.cvtColor( leftImage, cv2.COLOR_BGR2GRAY )
                rightGrayImage= cv2.cvtColor( rightImage, cv2.COLOR_BGR2GRAY )

                # find chess board corners
                flags = 0
                flags |= cv2.CALIB_CB_ADAPTIVE_THRESH
                flags |= cv2.CALIB_CB_NORMALIZE_IMAGE
                flags |= cv2.CALIB_CB_FAST_CHECK
                retL, cornersL = cv2.findChessboardCorners( leftGrayImage, chessBoardSize, flags )
                retR, cornersR = cv2.findChessboardCorners( rightGrayImage, chessBoardSize, flags )

                if retL and retR == True:
                    cornersL = cv2.cornerSubPix( leftGrayImage, cornersL, winSize, zerorZone, criteria )
                    cornersR = cv2.cornerSubPix( rightGrayImage, cornersR, winSize, zerorZone, criteria )

                    # draw chess board corners
                    cv2.drawChessboardCorners( leftImage, chessBoardSize, cornersL, retL )
                    cv2.drawChessboardCorners( rightImage, chessBoardSize, cornersR, retR )

                    # image_name = CALIBRATION_PATH + "/{name}_{index}.png".format( name='lt', index=frame_index )
                    # cv2.imwrite( image_name, origLeftImage )

                    # image_name = CALIBRATION_PATH + "/{name}_{index}.png".format( name='rt', index=frame_index )
                    # cv2.imwrite( image_name, origRightImage )

                    # print("<< IMAGE SAVED >>")
                    # frame_index+=1

                visual = np.concatenate( (leftImage, rightImage), axis=1 )
                cv2.imshow( "preview", visual )

                if cv2.waitKey(1) & 0xFF == ord( "s" ):
                    image_name = CALIBRATION_PATH + "/{name}_{index}.png".format( name='lt', index=frame_index )
                    cv2.imwrite( image_name, origLeftImage )

                    image_name = CALIBRATION_PATH + "/{name}_{index}.png".format( name='rt', index=frame_index )
                    cv2.imwrite( image_name, origRightImage )

                    print("<< IMAGE SAVED >>")
                    frame_index+=1
            else:
                visual = full_frame[0]
                cv2.imshow( "preview", visual )

                if cv2.waitKey(1) & 0xFF == ord( "s" ):
                    cv2.imwrite( CALIBRATION_PATH + "/{name}_{index}.png".format( name='nm', index=frame_index ), visual )
                    print("<< IMAGE SAVED >>")
                    frame_index+=1

except KeyboardInterrupt:
    pass
finally:
    if leftCam is not None:
        leftCam.stop()
    if rightCam is not None:
        rightCam.stop()
    if mainCam is not None:
        mainCam.stop()
