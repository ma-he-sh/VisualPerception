import cv2
import numpy as np

class Node():
    def __init__(self, index, x, y, r):
        self.index = index
        self.x = x
        self.y = y
        self.r = r
        self.is_start    = False
        self.is_goal     = False
        self.is_obstacle = False
        self.cost = 0
        self.parent = None

class ImageToNodes():
    def __init__(self, image_path ):
        self.image_path = image_path
        self.nodes      = []
        self.num_nodes  = 0
        self.pos        = [] # raw positions

    def generate_nodes(self):
        localMap = cv2.imread( self.image_path )
        gray = cv2.cvtColor( localMap, cv2.COLOR_BGR2GRAY )
        gray_blured = cv2.blur( gray, (3, 3) )
        
        detected_circles = cv2.HoughCircles( gray_blured, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=1, maxRadius=40 )
        if detected_circles is not None:
            detected_circles = np.uint16( np.around( detected_circles ) )
            for pt in detected_circles[0, :]:
                x, y, r = pt[0], pt[1], pt[2]
                
                self.pos.append( [x, y] )
                # border outline
                #cv2.circle( localMap, center=(x, y), radius=r, color=( 0, 0, 0 ), thickness=1 )
                objClass = Node( self.num_nodes, x, y, r )
                self.nodes.append( objClass )

                self.num_nodes+=1

        return self.num_nodes, self.nodes, self.pos
