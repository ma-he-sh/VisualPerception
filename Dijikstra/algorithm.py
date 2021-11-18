import cv2
import numpy as np
from modules.algorithm import NodeObj, Exploration, Algorithm
from modules.robot import Robot

map_name = "./b3898d0e-ea1c-434b-b9b5-f354cead4217.jpg"
nodes = []

robot = Robot( (0,0), 8, 4 )

def generate_nodes():
    numNodes = 0
    if map_name is None:
        return numNodes, nodes

    localMap = cv2.imread( map_name )
    gray = cv2.cvtColor( localMap, cv2.COLOR_BGR2GRAY )
    gray_blured = cv2.blur( gray, (3, 3) )
    
    detected_circles = cv2.HoughCircles( gray_blured, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=1, maxRadius=40 )
    if detected_circles is not None:
        detected_circles = np.uint16( np.around( detected_circles ) )
        for pt in detected_circles[0, :]:
            x, y, r = pt[0], pt[1], pt[2]
            
            # border outline
            cv2.circle( localMap, center=(x, y), radius=r, color=( 0, 0, 0 ), thickness=1 )
            objClass = NodeObj( x, y, r )
            nodes.append( objClass )
            
            numNodes+=1

    return numNodes, nodes

if __name__ == "__main__":
    numNodes, nodes = generate_nodes()
     
    

    pass
