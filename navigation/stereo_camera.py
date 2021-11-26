import numpy as np
import cv2
print( cv2.__version__ )

#from stereovision.blockmatchers import StereoBM, StereoSGBM
from stereovision.calibration import StereoCalibration
from config import camera_config, STEREO_VISION

calibration = StereoCalibration()
StereoBM = cv2.StereoBM_create()
StereoBM.search_range = 48
StereoBM.bm_preset    = 0
StereoBM.window_size  = 31

minBoxArea = 2000
maxLengthWidthRadio = 3
height = 480
width  = 640

leftCam = Camera( 'left', camera_config['left_cam_src'], camera_config['left_cam_config'] )
rightCam= Camera( 'right', camera_config['right_cam_src'], camera_config['right_cam_config'] )

leftCam.start()
rightCam.start()
time.sleep(0.2)

camera_list = []
camera_list.append( leftCam )
camera_list.append( rightCam )

full_frame = []
for stream in camera_list:
	image = stream.get_frame()
	if image is not None:
		frame = stream.stabalized( image )
		frame = stream.resize( frame )
		cv2.normalize( frame, frame, 0, 255, cv2.NORM_MINMAX )
		full_frame.append(frame)

rectified_stereo = calibration.rectify((full_frame[0], full_frame[1]))
disparity = StereoBM.get_disparity( rectified_stereo )
_, shapeMask = cv2.threshold( disparity, 0.7, 1.0, cv2.THRESH_BINARY )
disparityProcessed = shapeMask.copy()

print("CAMERA READY")

try:

	while True:
		full_frame = []
		for stream in camera_list:
			image = stream.get_frame()
			if image is not None:
				frame = stream.stabalized( image )
				frame = stream.resize( frame )
				cv2.normalize( frame, frame, 0, 255, cv2.NORM_MINMAX )
				full_frame.append(frame)

		if len( full_frame ) > 0:
			leftImage = full_frame[0]
			rightImage= full_frame[1]

			origLeftImage = leftImage.copy()
			origRightImage= rightImage.copy()

			leftGrayImage = cv2.cvtColor( leftImage, cv2.COLOR_BGR2GRAY )
			rightGrayImage= cv2.cvtColor( rightImage, cv2.COLOR_BGR2GRAY )
			
			rectified_stereo = calibration.rectify((full_frame[0], full_frame[1]))
			disparity = StereoBM.get_disparity( rectified_stereo )
			disparity = disparity / disparity.max()

			_, shapeMask = cv2.threshold( disparity, 0.7, 1.0, cv2.THRESH_BINARY )

			disparityProcessed = shapeMask.copy()
			disparityProcessed = disparityProcessed * 255.0
			disparityProcessed = disparityProcessed.astype(int)

			disparityProcessed = cv2.convertScaleAbs( disparityProcessed )
			
			countours, _ = cv2.findContours( disparityProcessed, 1, 2 )

			disparityProcessed = cv2.cvtColor( disparityProcessed, cv2.COLOR_GRAY2RGB )

			cv2.imshow("rectified", rectified_stereo[0] )
			cv2.imshow( "disparity", disparity )

			cv2.waitKey(1)

except KeyboardInterrupt:
    pass
finally:
    if leftCam is not None:
        leftCam.stop()
    if rightCam is not None:
        rightCam.stop()		