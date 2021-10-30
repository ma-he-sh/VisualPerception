import cv2
import numpy as np
import threading
from modules.errors import Error

class SrcNotFound(Error):
    pass

class SrcAvailability:
    def __init__(self, minRange=0, maxRange=10):
        self.minRange = minRange
        self.maxRange = maxRange
        pass

    def _checkSource(self, srcID):
        cap = cv2.VideoCapture(srcID)
        return cap.isOpened()

    def getDeviceList(self):
        cam_list = []

        for x in range( self.minRange, self.maxRange ):
            if self._checkSource( x ):
                cam_data = {
                    'name' : 'webcam',
                    'index': x,
                }
                cam_list.append( cam_data )
        return cam_list

class Camera:
    in_width    = 1920
    in_height   = 1080
    framerate   = 20
    out_width   = 640
    out_height  = 480
    video = None

    def __init__(self, srcID, configs={} ):
        self.srcID = srcID
        self.configs = configs

    @staticmethod
    def src_exists( srcID ):
        try:
            cam = cv2.VideoCapture( srcID )
        except Exception:
            raise SrcNotFound('Source not accessible : ' + srcID )
    
    def init_camera(self):
        self.video = cv2.VideoCapture( self.srcID )
        self.video.set( cv2.CAP_PROP_FRAME_WIDTH, self.in_width )
        self.video.set( cv2.CAP_PROP_FRAME_HEIGHT, self.in_height )
        self.video.set( cv2.CAP_PROP_FPS, self.framerate )

    def setup(self):
        self.init_camera()

    def release(self):
        if self.video is not None:
            self.video.release()
        cv2.destroyAllWindows()
    
    def resize(self, image):
        return cv2.resize( image, ( self.out_width, self.out_height ), interpolation=cv2.INTER_AREA )

    def get_frame(self):
        ret, image = self.video.read()
        return ret, image
    
    @staticmethod
    def preview( image, frame_name ):
        cv2.imshow( frame_name, image )

class CameraThread(threading.Thread):
    def __init__(self, win_name, srcID ):
        threading.Thread.__init__(self)
        self.win_name = win_name
        self.srcID    = srcID
        self.camera   = Camera( srcID )

    def run(self):
        print("STARTING CAMERA THREAD")
        self.camera.setup()

    def getFrame(self):
        ret, image = self.camera.get_frame()
        return ret, image