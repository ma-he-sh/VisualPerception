import cv2
import numpy as np
from algorithm.node import Node

class Explorer():
    @staticmethod
    def get_map_grid( map_width, map_height, resolution ):
        map = []
        node_index=0

        # prepare generalized map based on new resolution
        height = 0
        width = 0
        for i in range( 0, map_height, resolution ):
            height += 1
        for j in range( 0, map_width, resolution ):
            width += 1

        # prepare map pixel
        for xi in range( 0, height ):
            map.append([])
            for yi in range( 0, width ):
                nodeObj = Node( node_index, xi * resolution, yi * resolution, resolution )
                map[xi].append( nodeObj )

                node_index+=1

        return map

    @staticmethod
    def get_obstacles( map_name ):
        # get obstacles from the given map
        localMap = cv2.imread( map_name )
        gray = cv2.cvtColor( localMap, cv2.COLOR_BGR2GRAY )
        gray_blured = cv2.blur( gray, (3, 3))
        obstacles = []

        index = 0
        detected_circles = cv2.HoughCircles( gray_blured, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=1, maxRadius=40 )
        if detected_circles is not None:
            detected_circles = np.uint16( np.around( detected_circles ) )
            for pt in detected_circles[0, :]:
                a, b, r = pt[0], pt[1], pt[2]
                pos = ( a, b )

                # border outline
                #cv2.circle( localMap, center=( a, b ), radius=r, color=( 0, 0, 0 ), thickness=1 )
                obstacles.append( pos )
                index += 1

        return obstacles

    @staticmethod
    def coord_within( x1, y1, x2, y2, objX, objY ):
        return ( objX >= x1 and objX <= x2 and objY >= y1 and objY <= y2 )

    @staticmethod
    def within_range( curr_node, obstacles, resolution ):
        """
        Check if the obstacle is withing mapping regions
        As extact mapping not available 
        """

        x1 = curr_node.x
        y1 = curr_node.y
        x2 = curr_node.x + resolution
        y2 = curr_node.y + resolution

        found = False
        for pos in obstacles:
            if Explorer.coord_within( x1, y1, x2, y2, pos[0], pos[1] ):
                found = True
                break
        return found

    @staticmethod
    def get_neighbours( curr_node, node_arr, resolution ):
        neighbours = []

        currX, currY = curr_node.x, curr_node.y
        # top 
        topX, topY = currX, currY + resolution
        # top right
        topRX, topRY = currX + resolution, currY + resolution
        # top left
        topLX, topLY = currX - resolution, currY + resolution
        # bottom
        bottomX, bottomY = currX , currY - resolution
        # bottom right
        bottomRX, bottomRY = currX + resolution, currY - resolution
        # bottom left
        bottomLX, bottomLY = currX - resolution, currY - resolution
        # right
        rightX, rightY = currX + resolution, currY
        # left
        leftX, leftY = currX - resolution, currY

        #print(node_arr)
        
        for row in node_arr:
            for obj in row:
                add_to_arr = False
                if obj.x == topX and obj.y == topY:
                    add_to_arr = True
                elif obj.x == bottomX and obj.y == bottomY:
                    add_to_arr = True
                elif obj.x == rightX and obj.y == rightY:
                    add_to_arr = True
                elif obj.x == leftX and obj.y == leftY:
                    add_to_arr = True
                elif obj.x == topRX and obj.y == topRY:
                    add_to_arr = True
                elif obj.x == topLX and obj.y == topLY:
                    add_to_arr = True
                elif obj.x == bottomLX and obj.y == bottomLY:
                    add_to_arr = True
                elif obj.x == bottomRX and obj.y == bottomRY:
                    add_to_arr = True

                # if obstacle do not add
                if obj.is_obstacle:
                    add_to_arr = False
                    
                if add_to_arr:
                    neighbours.append( obj )
        
        return neighbours