import cv2
import numpy as np
from _modules.node import Node
from _modules.algorithm import Algorithm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

map_name = "./b3898d0e-ea1c-434b-b9b5-f354cead4217.jpg"

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

if __name__ == "__main__":
    start = [0, 0]
    goal  = [1600, 1040]

    map_size = ( 1080, 1920 )
    resolution=40

    total_node_pixels = map_size[0] * map_size[1] # 1px based scaling
    #print( total_node_pixels )

    map = Explorer.get_map_grid( map_size[0], map_size[1], resolution )
    #print( len( map ) )

    # get the obstacle location
    obstacles = Explorer.get_obstacles( map_name )
    print( obstacles )

    #fig, ax = plt.subplots( figsize=(20, 20) )
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    #ax.set_aspect("equal")
    ax.set_aspect('auto')

    start_node = None
    goal_node  = None
    # define goals and obstacles
    for row in map:
        for obj in row:
            if start[0] == obj.x and start[1] == obj.y:
                obj.is_start = True
                start_node = obj
                plt.plot( obj.x, obj.y, color="r", marker="s" )
            elif goal[0] == obj.x and goal[1] == obj.y:
                obj.is_goal  = True
                goal_node = obj
                plt.plot( obj.x, obj.y, color="g", marker="p" )
            else:
                if Explorer.within_range( obj, obstacles, resolution ):
                    obj.is_obstacle = True
                    plt.plot( obj.x, obj.y, color="y", marker="p" )

    # set the neighbours of the node
    for row in map:
        for obj in row:
            neighbours = Explorer.get_neighbours( obj, map, resolution )
            obj.neighbours = neighbours

    algo = Algorithm( map, start_node, goal_node, resolution )
    algo.init()

    path_found = algo.exec( plt ) # exec
    algo.generate_path(plt)
    
    plt.show()

    pass
