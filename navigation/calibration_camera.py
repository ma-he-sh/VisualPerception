"""
Camera calibration script
@modified code, original code taken from https://learnopencv.com/camera-calibration-using-opencv/
"""

from os import path
import time
import cv2
import glob
import numpy as np
from modules.helpers import create_paths, path_exists
from config import camera_config, STEREO_VISION

if not STEREO_VISION:
    print( "MAKESURE STERIO VISON IS DEFINE FOR CALIBRATING" )

# get dir where the calibration files exists
CALIBRATION_PATH = "./calibrations"

chessBoardSize = ( 9, 6 ) # dimension of the checkboard
frameSize      = ( 320, 426 ) # width, height
winSize        = (11, 11)
zerorZone      = (-1, -1)

criteria = ( cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001 )

objectPoints = np.zeros( (chessBoardSize[0] * chessBoardSize[1], 3), np.float32 )
objectPoints[:,:2] = np.mgrid[0:chessBoardSize[0], 0:chessBoardSize[1]].T.reshape(-1, 2)
objectPoints = objectPoints * 20

# store object points and image points
objectPointsArr = []
imagePointsArrL = []
imagePointsArrR = []

def calibrate():
    leftCamImages = sorted( glob.glob( CALIBRATION_PATH + "/rt_*.png" ) )
    rightCamImages= sorted( glob.glob( CALIBRATION_PATH + "/lt_*.png" ) )

    for leftImage, rightImage in zip( leftCamImages, rightCamImages ):
        imgL = cv2.imread( leftImage )
        imgR = cv2.imread( rightImage )

        print( imgL.shape )

        leftGrayImage = cv2.cvtColor( imgL, cv2.COLOR_BGR2GRAY )
        rightGrayImage= cv2.cvtColor( imgR, cv2.COLOR_BGR2GRAY )

        # find chess board corners
        retL, cornersL = cv2.findChessboardCorners( leftGrayImage, chessBoardSize, None )
        retR, cornersR = cv2.findChessboardCorners( rightGrayImage, chessBoardSize, None )

        if retL and retR == True:
            objectPoints.append( objectPoints )

            cornersL = cv2.cornerSubPix( leftGrayImage, cornersL, winSize, zerorZone, criteria )
            imagePointsArrL.append( cornersL )

            cornersR = cv2.cornerSubPix( rightGrayImage, cornersR, winSize, zerorZone, criteria )
            imagePointsArrR.append( cornersR )

    # calibration
    retL, mtxL, distL, rvecsL, tvecsL = cv2.calibrateCamera( objectPoints, imagePointsArrL, frameSize, None, None )
    heightL, widthL, channelL = ( 320, 426, 3 )
     

if __name__ == '__main__':
    pathExists = path_exists( CALIBRATION_PATH )
    if not pathExists:
        print( "NO CALIBRATION FILES EXISTS" )
    else:
        calibrate()