"""
Camera calibration script
@modified code, original code taken from https://learnopencv.com/camera-calibration-using-opencv/
"""

import os
import time
import cv2
import glob
import numpy as np
from modules.helpers import create_paths, path_exists
from config import camera_config, STEREO_VISION, CAMERA_CONFIGS_STEREO_MAP

if not STEREO_VISION:
    print( "MAKESURE STERIO VISON IS DEFINE FOR CALIBRATING" )

if os.path.isfile( CAMERA_CONFIGS_STEREO_MAP ):
    os.unlink( CAMERA_CONFIGS_STEREO_MAP )
else:
    print("")

# get dir where the calibration files exists
CALIBRATION_PATH = "./calibrations"

chessBoardSize = ( 8, 6 ) # dimension of the checkboard
frameSize      = ( 640, 480 ) # width, height
winSize        = (11, 11)
zerorZone      = (-1, -1)

criteria = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001 )

objectPoints = np.zeros( (chessBoardSize[0] * chessBoardSize[1], 3), np.float32 )
objectPoints[:,:2] = np.mgrid[0:chessBoardSize[0], 0:chessBoardSize[1]].T.reshape(-1, 2)

# store object points and image points
objectPointsArr = []
imagePointsArrL = []
imagePointsArrR = []

def calibrate():
    leftCamImages = sorted( glob.glob( CALIBRATION_PATH + "/rt_*.png" ) )
    rightCamImages= sorted( glob.glob( CALIBRATION_PATH + "/lt_*.png" ) )

    imageShapeL = None
    imageShapeR = None

    for leftImage, rightImage in zip( leftCamImages, rightCamImages ):
        imgL = cv2.imread( leftImage )
        imgR = cv2.imread( rightImage )

        leftGrayImage = cv2.cvtColor( imgL, cv2.COLOR_BGR2GRAY )
        rightGrayImage= cv2.cvtColor( imgR, cv2.COLOR_BGR2GRAY )

        imageShapeL = leftGrayImage.shape
        imageShapeR = rightGrayImage.shape

        # find chess board corners
        # image_invertedL = np.array(256 - leftGrayImage, dtype=np.uint8)
        # image_invertedR = np.array(256 - rightGrayImage, dtype=np.uint8)
        flags = 0
        flags |= cv2.CALIB_CB_ADAPTIVE_THRESH
        flags |= cv2.CALIB_CB_NORMALIZE_IMAGE
        flags |= cv2.CALIB_CB_FAST_CHECK
        retL, cornersL = cv2.findChessboardCorners( leftGrayImage, chessBoardSize, flags )
        retR, cornersR = cv2.findChessboardCorners( rightGrayImage, chessBoardSize, flags )

        if retL and retR == True:
            print("-")
            objectPointsArr.append( objectPoints )

            cornersL = cv2.cornerSubPix( leftGrayImage, cornersL, winSize, zerorZone, criteria )
            imagePointsArrL.append( cornersL )

            cornersR = cv2.cornerSubPix( rightGrayImage, cornersR, winSize, zerorZone, criteria )
            imagePointsArrR.append( cornersR )

        #visual = np.concatenate( (imgL, imgR), axis=1 )
        #cv2.imshow( "preview", visual )
        #cv2.waitKey(0)

    print( imageShapeL, imageShapeL )

    # calibration
    imgLW, imgLH = imageShapeL[:2]
    retL, mtxL, distL, rvecsL, tvecsL = cv2.calibrateCamera( objectPointsArr, imagePointsArrL, imageShapeL[::-1], None, None )
    new_mtxL, roiL= cv2.getOptimalNewCameraMatrix(mtxL,distL,(imgLW, imgLH),1, (imgLW, imgLH))

    imgRW, imgRH = imageShapeR[:2]
    retR, mtxR, distR, rvecsR, tvecsR = cv2.calibrateCamera( objectPointsArr, imagePointsArrR, imageShapeR[::-1], None, None )
    new_mtxR, roiR= cv2.getOptimalNewCameraMatrix(mtxR,distR,(imgRW, imgRH),1, (imgRW, imgRH))

    # stereo calibration
    flags = 0
    flags |= cv2.CALIB_FIX_PRINCIPAL_POINT
    #flags |= cv2.CALIB_USE_INTRINSIC_GUESS
    #flags |= cv2.CALIB_FIX_FOCAL_LENGTH
    #flags |= cv2.CALIB_FIX_ASPECT_RATIO
    #flags |= cv2.CALIB_ZERO_TANGENT_DIST
    #flags |= cv2.CALIB_RATIONAL_MODEL
    #flags |= cv2.CALIB_SAME_FOCAL_LENGTH
    #flags |= cv2.CALIB_FIX_K3
    #flags |= cv2.CALIB_FIX_K4
    #flags |= cv2.CALIB_FIX_K5
    #flags |= cv2.CALIB_FIX_INTRINSIC

    criteria_stereo= (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # calculate the camera matrix
    retS, new_mtxL, distL, new_mtxR, distR, Rot, Trns, Emat, Fmat = cv2.stereoCalibrate(objectPointsArr,
                                                          imagePointsArrL,
                                                          imagePointsArrR,
                                                          new_mtxL,
                                                          distL,
                                                          new_mtxR,
                                                          distR,
                                                          imageShapeR[::-1],
                                                          criteria_stereo,
                                                          flags)
    
    # stereo rectification
    rectify_scale= 1 # image not croped set 1 else 0
    rect_l, rect_r, proj_mat_l, proj_mat_r, Q, roiL, roiR= cv2.stereoRectify(new_mtxL, distL, new_mtxR, distR, imageShapeR[::-1], Rot, Trns, rectify_scale,(0,0))

    # create rectification maps
    StereoMapLeft   = cv2.initUndistortRectifyMap(new_mtxL, distL, rect_l, proj_mat_l, imageShapeL[::-1], cv2.CV_16SC2)
    StereoMapRight  = cv2.initUndistortRectifyMap(new_mtxR, distR, rect_r, proj_mat_r, imageShapeR[::-1], cv2.CV_16SC2)
    
    # saving mapped data as xml
    cvFile = cv2.FileStorage( CAMERA_CONFIGS_STEREO_MAP, cv2.FILE_STORAGE_WRITE )
    cvFile.write("LTStereoMapX",   StereoMapLeft[0])
    cvFile.write("LTStereoMapY",   StereoMapLeft[1])
    cvFile.write("RTStereoMapX",  StereoMapRight[0])
    cvFile.write("RTStereoMapY",  StereoMapRight[1])
    cvFile.release()

if __name__ == '__main__':
    pathExists = path_exists( CALIBRATION_PATH )
    if not pathExists:
        print( "NO CALIBRATION FILES EXISTS" )
    else:
        calibrate()