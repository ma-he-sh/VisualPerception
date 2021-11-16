"""
Calibrated camera test
"""
import cv2
import numpy as np
from modules.camera import Camera, SrcAvailability
from config import camera_config, STEREO_VISION, CAMERA_CONFIGS_STEREO_MAP

# creating rectified image for camera views
cvFile = cv2.FileStorage( CAMERA_CONFIGS_STEREO_MAP, cv2.FILE_STORAGE_READ )
ltStereoMapX = cvFile.getNode("LTStereoMapX").mat()
ltStereoMapY = cvFile.getNode("LTStereoMapY").mat()
rtStereoMapX = cvFile.getNode("RTStereoMapX").mat()
rtStereoMapY = cvFile.getNode("RTStereoMapY").mat()
cvFile.release()

if not STEREO_VISION:
    print("NEED TO RUN WITH STEREO CAMERAS")
    exit

leftCam = Camera( 'left', camera_config['left_cam_src'], camera_config['left_cam_config'] )
rightCam= Camera( 'right', camera_config['right_cam_src'], camera_config['right_cam_config'] )

leftCam.start()
rightCam.start()

try:
    camera_list = []
    camera_list.append( leftCam )
    camera_list.append( rightCam )

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
            leftImage = full_frame[0]
            leftImage = cv2.remap( leftImage, ltStereoMapX, ltStereoMapY, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0 )

            rightImage= full_frame[1]
            rightImage = cv2.remap( rightImage, rtStereoMapX, rtStereoMapY, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0 )

            visual = np.concatenate( (leftImage, rightImage), axis=1 )
            cv2.imshow( "preview", visual )
            cv2.waitKey(1)

except KeyboardInterrupt:
    pass
finally:
    if leftCam is not None:
        leftCam.stop()
    if rightCam is not None:
        rightCam.stop()