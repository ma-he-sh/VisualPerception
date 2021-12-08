"""
Calibration camera validation
"""

import cv2
import numpy as np
from modules.camera import Camera, SrcAvailability
from config import *

# list available camera sources
src = SrcAvailability()
deviceList = src.getDeviceList()
print(deviceList)

# create rectified image for views
cvFile = cv2.FileStorage( CAMERA_CONFIGS_STEREO_MAP, cv2.FILE_STORAGE_READ )
ltStereoMapX = cvFile.getNode("LTStereoMapX").mat()
ltStereoMapY = cvFile.getNode("LTStereoMapY").mat()
rtStereoMapX = cvFile.getNode("RTStereoMapX").mat()
rtStereoMapY = cvFile.getNode("RTStereoMapY").mat()
cvFile.release()

if not STEREO_VISION:
	print("NEED TO RUN THE SCRIPT WITH STEREO CAMERAS")
	exit

# =============================

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


DISPARITY = None
FILTER_IMAGE = None

# mouse click handler :: focus on certain pixels to obtain distance and disparity
def mouse_listener(e, pixel_x, pixel_y, flags, param ):
    print('event recieved')
    if e == cv2.EVENT_LBUTTONUP:
        avg_disparity = 0
        for u in range (-1,2):
            for v in range (-1,2):
                avg_disparity += disp[pixel_y+u,pixel_x+v]
        avg_disparity=avg_disparity/9
        Distance= -593.97*avg_disparity**(3) + 1506.8*avg_disparity**(2) - 1373.1*avg_disparity + 522.06
        Distance= np.around(Distance*0.01,decimals=2)
        print('Distance: '+ str(Distance)+' m')
        print('Measure at '+str(Distance)+' cm, the dispasrity is ' + str(avg_disparity))

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
        gray_frame = []

        for stream in camera_list:
            image = stream.get_frame()
            if image is not None:
                image = stream.stabalized(image)
                frame = stream.resize(image)
                cv2.normalize(frame, frame, 0, 255, cv2.NORM_MINMAX )
                # frame 
                full_frame.append( frame )
                # gray image frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_frame.append( gray )

        if len( full_frame ) > 0:
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

            disparityLeft = np.int16(disparityL)
            disparityRight= np.int16(disparityR)

            # apply wls filter to smooth the disparity layers
            filterImageWLS = WLS_FILTER.filter( disparityL, leftGrayImage, None, disparityR )
            filterImageWLS = cv2.normalize(src=filterImageWLS, dst=filterImageWLS, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX)
            filterImageWLS = np.uint8(filterImageWLS)

            DISPARITY = disparityL
            FILTER_IMAGE=filterImageWLS

            # clean the background artificats
            disp= ((disparityL.astype(np.float32)/ 16)-MIN_DISPARITY)/NUM_DISPARITIES
            morphologyFilter = cv2.morphologyEx(disparityL,cv2.MORPH_CLOSE, kernel)
            disparityFinal= (morphologyFilter-morphologyFilter.min())*255
            disparityFinal= disparityFinal.astype(np.uint8)     
            filterImage   = cv2.applyColorMap(filterImageWLS,cv2.COLORMAP_OCEAN)

            cv2.setMouseCallback("Depth Perception", mouse_listener, filterImage)

            cv2.imshow('Depth Perception',filterImage)
            cv2.imshow( "preview", visual )
            cv2.waitKey(1)

except KeyboardInterrupt:
    pass
finally:
    if leftCam is not None:
        leftCam.stop()
    if rightCam is not None:
        rightCam.stop()