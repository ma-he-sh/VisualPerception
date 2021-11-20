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

    fig, ax = plt.subplots( figsize=(20, 20) )
    ax.set_aspect("equal")

    start_node = None
    goal_node  = None
    # define goals and obstacles
    for row in map:
        for obj in row:
            if start[0] == obj.x and start[1] == obj.y:
                obj.is_start = True
                start_node = obj
                #plt.plot( obj.x, obj.y, color="r", marker="s" )
            elif goal[0] == obj.x and goal[1] == obj.y:
                obj.is_goal  = True
                goal_node = obj
                #plt.plot( obj.x, obj.y, color="g", marker="s" )
            else:
                #plt.plot( obj.x, obj.y, color="b", marker="s" )
                pass

    # set the neighbours of the node
    for row in map:
        for obj in row:
            neighbours = Explorer.get_neighbours( obj, map, resolution )
            obj.neighbours = neighbours

    algo = Algorithm( map, start_node, goal_node, resolution )
    algo.init()

    fig, ax = plt.subplots( figsize=(20, 20) )
    ax.set_aspect("equal")
    #ani = FuncAnimation( fig, algo.run, frames=range( 1, map_size[0] * map_size[1] ), interval=1000, repeat=True )

    path_found = algo.exec( plt ) # exec
    algo.generate_path(plt)
    
    plt.show()

    pass