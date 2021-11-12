import cv2
import numpy as np
import threading
from imutils.video import VideoStream
import imutils
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

class FullFrame:
    def __init__(self, left_img, right_img):
        self.left_img   = left_img
        self.right_img  = right_img
        self.full_frame = self.getFullFrame() 
    
    def getFullFrame(self):
        return np.concatenate( (self.left_img, self.right_img), axis=1 )

    def write_to_disk(self):
        cv2.imwrite( "./full_frame.png", self.full_frame )

class Camera:
    def __init__(self, name, srcID, config={} ):
        self._name = name
        self.srcID = srcID
        self.config = {
            'in_width'  : 320,
            'in_height' : 240,
            'fps'       : 20,
            'out_width' : 320,
            'out_height': 240,
            'angle'     : 0,
        }
        self.video = None

        for _key in self.config:
            if _key in config:
                self.config[_key] = config[_key]

    @staticmethod
    def src_exists( srcID ):
        try:
            cam = cv2.VideoCapture( srcID )
        except Exception:
            raise SrcNotFound('Source not accessible : ' + srcID )

    def init_camera(self):
        self.video = VideoStream( self.srcID ).start() # warm startup

    def start(self):
        print("camera initialize")
        self.init_camera()

    def stop(self):
        print("camera stopping")
        if self.video is not None:
            self.video.stop()

    def resize(self, image):
        return imutils.resize( image, width=self.config['out_width'], height=self.config['out_height'] )

    def stabalized(self, image):
        return imutils.rotate_bound( image, self.config['angle'] )

    def get_frame(self):
        if self.video is not None:
            return self.video.read()
        else:
            return None

    def write_to_disk(self, image ):
        if self.video is not None:
            image_name = "./image_{fileID}_.png".format(fileID=self.srcID)
            cv2.imwrite( image_name, image )

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