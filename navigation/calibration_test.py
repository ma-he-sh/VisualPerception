"""
Calibrated camera test
"""
import cv2
import numpy as np
from sklearn.preprocessing import normalize
from modules.camera import Camera, SrcAvailability
from config import camera_config, STEREO_VISION, CAMERA_CONFIGS_STEREO_MAP

# gives a list of availble cameras
src = SrcAvailability()
deviceList = src.getDeviceList()
print( deviceList )

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

#stereo = cv2.StereoBM_create( numDisparities=64, blockSize=11 )
window_size = 3
min_disp = 10
num_disp = 130 - min_disp
stereo = cv2.StereoSGBM_create(
    numDisparities=num_disp,
    blockSize=window_size,
    uniquenessRatio=10,
    speckleWindowSize=100,
    speckleRange=32,
    disp12MaxDiff=5,
    P1=8*3*window_size**2,
    P2=32*3*window_size**2
)

stereoR=cv2.ximgproc.createRightMatcher(stereo)
# WLS filters
lmbda = 80000
sigma = 1.8
visual_multiplier = 1.0
wls_filter = cv2.ximgproc.createDisparityWLSFilter(matcher_left=stereo)
wls_filter.setLambda(lmbda)
wls_filter.setSigmaColor(sigma)

kernel= np.ones((3,3),np.uint8)

def coords_mouse_disp(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        #print x,y,disp[y,x],filteredImg[y,x]
        average=0
        for u in range (-1,2):
            for v in range (-1,2):
                average += disp[y+u,x+v]
        average=average/9
        Distance= -593.97*average**(3) + 1506.8*average**(2) - 1373.1*average + 522.06
        Distance= np.around(Distance*0.01,decimals=2)
        print('Distance: '+ str(Distance)+' m')

try:
    camera_list = []
    camera_list.append( leftCam )
    camera_list.append( rightCam )

    while True:
        full_frame = []
        comp_frame = []
        for stream in camera_list:
            image = stream.get_frame()
            if image is not None:
                frame = stream.stabalized( image )
                frame = stream.resize( frame )
                cv2.normalize( frame, frame, 0, 255, cv2.NORM_MINMAX )
                #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                full_frame.append( frame )

        if len( full_frame ) > 0:
            leftImage = full_frame[0]
            #leftImage = cv2.remap( leftImage, ltStereoMapX, ltStereoMapY, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0 )

            rightImage= full_frame[1]
            #rightImage = cv2.remap( rightImage, rtStereoMapX, rtStereoMapY, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0 )

            visual = np.concatenate( (leftImage, rightImage), axis=1 )
            disparity = stereo.compute( leftImage, rightImage )

            dispL = disparity
            dispR= stereoR.compute(rightImage,leftImage)
            dispL= np.int16(dispL)
            dispR= np.int16(dispR)

            filteredImg= wls_filter.filter(dispL,leftImage,None,dispR)
            filteredImg = cv2.normalize(src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX);
            filteredImg = np.uint8(filteredImg)

            disp= ((disparity.astype(np.float32)/ 16)-min_disp)/num_disp
            closing= cv2.morphologyEx(disparity,cv2.MORPH_CLOSE, kernel)

            dispc= (closing-closing.min())*255
            dispC= dispc.astype(np.uint8)                                   
            disp_Color= cv2.applyColorMap(dispC,cv2.COLORMAP_OCEAN)         
            filt_Color= cv2.applyColorMap(filteredImg,cv2.COLORMAP_OCEAN)

            cv2.imshow('Filtered Color Depth',filt_Color)
            cv2.imshow( "gray", disparity )
            cv2.imshow( "preview", visual )

            cv2.setMouseCallback("Filtered Color Depth",coords_mouse_disp,filt_Color)

            cv2.waitKey(1)

except KeyboardInterrupt:
    pass
finally:
    if leftCam is not None:
        leftCam.stop()
    if rightCam is not None:
        rightCam.stop()
