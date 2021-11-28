import config as ENV
import math
from algorithm.explorer import Explorer
from algorithm.algorithm import Algorithm

MOTION_DEFAULT   = 0
MOTION_STAIGHT_Y = 1
MOTION_STRAIGN_X = 2
MOTION_STRAIGN_POS_SLOPE = 3
MOTION_STRAIGN_NEG_SLOPE = 4

class ProcessMap():
    def __init__(self, map_entry, resolution=40 ):
        self.map_entry = map_entry
        self.map_id    = self.map_entry[0]
        self.file_uuid = self.map_entry[1]
        self.file_name = self.map_entry[2]
        self.file_date = self.map_entry[3]
        self.file_ext  = self.map_entry[4]
        self.file_width= int( self.map_entry[5] )
        self.file_height=int( self.map_entry[6] )
 
        self.file_map_image = self.get_map_src()

        """
        map_size    : determine the size of the map
        resolution  : determine how close the pixels are closer
        total_node_pixels : number od coordinates needed for the map
        """
        self.map_size  = ( self.file_width, self.file_height )
        self.resolution= resolution
        self.total_node_pixels = self.file_width * self.file_height
        self.proposed_path = []
        self.motion_path   = []
        self.path_available= False

    def get_map_src(self):
        return ENV.UPLOAD_FOLDER + '/' + self.file_uuid + self.file_ext

    def get_map_grid(self):
        return Explorer.get_map_grid( self.file_width, self.file_height, self.resolution )

    def get_known_obstacles(self):
        return Explorer.get_obstacles( self.file_map_image )

    def get_obstacle_pos(self, map_grid=None):
        obstacles_pos = []
        obstacles = self.get_known_obstacles()
        if len(obstacles) <= 0:
            return obstacles, obstacles_pos

        if map_grid is None:
            map_grid = self.get_map_grid()
        
        if len(map_grid) <= 0:
            return obstacles, obstacles_pos

        for i, row in enumerate(map_grid):
            obstacles_pos.append([])
            for obj in row:
                if Explorer.within_range( obj, obstacles, self.resolution ):
                    obj.is_obstacle = True
                    obstacles_pos[i].append([ obj.x, obj.y ])
        
        return obstacles, obstacles_pos

    def get_grid_map_pos_for_graph(self):
        map_grid_pos = []
        map_grid = self.get_map_grid()
        if map_grid is None:
            return map_grid_pos

        for i, row in enumerate(map_grid):
            map_grid_pos.append([])
            for obj in row:
                map_grid_pos[i].append([ obj.x, obj.y ])

        return map_grid_pos
        
    def get_obstacle_pos_for_graph(self, map_grid=None ):
        _, obstacles_pos = self.get_obstacle_pos( map_grid )
        return obstacles_pos

    def get_path(self, start_point, end_point ):
        start_node = None
        goal_node   = None

        print( start_point, end_point )

        map = self.get_map_grid()
        obstacles = self.get_known_obstacles()

        # define goal and obstacles
        for row in map:
            for obj in row:
                if start_point[0] == obj.x and start_point[1] == obj.y:
                    obj.is_start = True
                    start_node = obj
                elif end_point[0] == obj.x and end_point[1] == obj.y:
                    obj.is_goal  = True
                    goal_node = obj
                else:
                    if Explorer.within_range( obj, obstacles, self.resolution ):
                        obj.is_obstacle = True

        # set the neighbours of the node
        for row in map:
            for obj in row:
                neighbours = Explorer.get_neighbours( obj, map, self.resolution )
                obj.neighbours = neighbours
    
        if start_node is None or goal_node is None:
            return []

        algo = Algorithm( map, start_node, goal_node, self.resolution )
        algo.init()
        algo.exec()
        self.proposed_path = algo.get_generated_path()
        self.path_available= True
        return self.proposed_path

    def _calc_slope(self, p1, p2):
        if ( p1[0] - p2[0] == 0 ): return 0
        return (float)(p2[1] - p1[1]) / (p2[0] - p1[0])

    def _cal_angle_vector(self, x, y):
        return math.degrees(math.atan2(-y, x))

    def _cal_angle(self, p1, p2):
        return self._cal_angle_vector( p2[0] - p1[0], p2[1] - p1[1] )

    def get_planned_motion(self):
        if not self.path_available:
            return []

        completed = {}
        path = self.proposed_path[::-1]

        self.motion_path = {}
        curr_motion_index  = MOTION_DEFAULT
        prev_motion_index  = MOTION_DEFAULT
        action_index = 0

        prev_angle = 0

        if len(path) > 2:
            start = path[0]
            end   = path[len(path) - 1]
            
            index = 0
            cursor= 0
            pre_slope = 0
            distance  = 0
            end_reach = False

            curr_data = {}

            while not end_reach:

                coord1 = path[cursor]
                coord2 = path[index]
                slope = self._calc_slope( coord1, coord2 )
                angle = self._cal_angle( coord1, coord2 )

                #print(angle)

                if coord2[1] == coord1[1]:
                    #print(distance)
                    #print('straight y axis')
                    curr_motion_index = MOTION_STAIGHT_Y

                if coord2[0] == coord1[0]:
                    #print(distance)
                    #print('straight x axis')
                    curr_motion_index = MOTION_STRAIGN_X

                if pre_slope != slope:
                    if slope < 0:
                        #print('-1 slope')
                        curr_motion_index = MOTION_STRAIGN_NEG_SLOPE
                    else:
                        #print('+ slope')
                        curr_motion_index = MOTION_STRAIGN_POS_SLOPE

                    pre_slope = slope
                    # set new joint
                    cursor = index - 1
                    index = index - 1

                # if curr_motion_index != prev_motion_index:
                #     prev_motion_index = curr_motion_index

                #     print( curr_data )

                #     curr_data['distance'] = distance
                #     self.motion_path[action_index] = curr_data
                    
                #     action_index += 1
                #     distance = 0 # reset distance counter
                # else:
                #     # --- same motion
                #     self.motion_path.setdefault( action_index, {} )
                #     curr_data = {
                #         'angle':angle,
                #         'distance': 0,
                #     }

                #     print('same_motion')
                #     print( angle )
                #     print( distance )

                if prev_angle != angle:
                    prev_angle = angle # set the prev as current
                    print(curr_data)
                    distance = 0
                else:
                    #print('same angle')
                    distance+=1
                    curr_data = {
                        'angle': angle,
                        'distance': distance
                    }


                completed.setdefault(slope, 0)
                completed[slope] += 1

                index += 1
                if index == len(path):
                    end_reach = True

            print( completed )
            print( self.motion_path )


