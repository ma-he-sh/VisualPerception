import cv2
import numpy as np
import threading
from modules.errors import Error

class SrcNotFound(Error):
    pass

class CameraTimeout(Error):
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
    in_width    = 320
    in_height   = 240
    framerate   = 20
    out_width   = 320
    out_height  = 240
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
        print("camera initialize")
        self.init_camera()
        print(self.video )

    def release(self):
        if self.video is not None:
            self.video.release()
        cv2.destroyAllWindows()
    
    def resize(self, image):
        return cv2.resize( image, ( self.out_width, self.out_height ), interpolation=cv2.INTER_AREA )

    def get_frame(self):
        if self.video is not None and self.video.isOpened():
            ret, image = self.video.read()
            return ret, image
        return None, None

    def is_ready(self):
        if self.video is not None:
            print( self.video.isOpened() )
            return self.video.isOpened()
        return False
    
    @staticmethod
    def preview( image, frame_name ):
        cv2.imshow( frame_name, image )

class CameraThread(threading.Thread):
    def __init__(self, win_name, srcID ):
        threading.Thread.__init__(self)
        self.win_name = win_name
        self.srcID    = srcID
        self.camera   = Camera( srcID )
        self._stop_event = threading.Event()

    def run(self):
        self.camera.setup()
        print("STARTING CAMERA THREAD")

    def getFrame(self):
        ret, image = self.camera.get_frame()
        return ret, image

    def cameraReady(self):
        return self.camera.is_ready()

    def stop(self):
        self.camera.release()
        self._stop_event.set()
    
    def stopped(self):
        return self._stop_event.is_set()