import numpy as np
import cv2 as cv

stereo = cv.StereoBM_create( numDisparities=16, blockSize=15 )

class Stereo:
    def __init__(self, left_img, right_img):
        self.stereo   = stereo.compute( left_img, right_img )

    def load_disaparity_conf(self):
        
    
    def get_disparity(self, dispariy_conf={}):
        for _key in self.disparity_config:
            if _key in dispariy_conf:

        return self.stereo
