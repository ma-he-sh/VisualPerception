import numpy as np
import cv2 as cv

stereo = cv.StereoBM_create( numDisparities=16, blockSize=15 )

class Stereo:
    def __init__(self, left_img, right_img):
        self.stereo   = stereo.compute( left_img, right_img )
    
    def get_disparity(self):
        return self.stereo