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
    def __init__(self, map_entry, resolution=40, additional_obs=[] ):
        self.map_entry = map_entry
        self.map_id    = self.map_entry[0]
        self.file_uuid = self.map_entry[1]
        self.file_name = self.map_entry[2]
        self.file_date = self.map_entry[3]
        self.file_ext  = self.map_entry[4]
        self.file_width= int( self.map_entry[5] )
        self.file_height=int( self.map_entry[6] )
        self.additional_obs = additional_obs
 
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

        # add new found obstacles
        if len(self.additional_obs) > 0:
            for obs in self.additional_obs:
                obstacles.append(obs)

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
        path_found = algo.exec_code()
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

    def _cal_distance(self, p1, p2):
        return math.sqrt( math.pow( ( p2[0] - p1[0] ), 2 ) + math.pow( (p2[1] - p1[1]), 2 ) )

    def _cal_angle_diff(self, prev_angle, new_angle ):
        print( "here>>", prev_angle, new_angle )
        if prev_angle == 0:
            diff = new_angle
        else:
            if prev_angle > 0:
                # already left turned
                if new_angle > 0:
                    print( 'prev_angle > 0 new_angle > 0' )
                    diff = ( new_angle - prev_angle )
                else:
                    print('prev_angle < 0 new_angle < 0')
                    diff = ( 0 - prev_angle ) + ( new_angle )
                    if diff > 180:
                        diff = 360 - diff
                    elif diff < -180:
                        diff = 360 + diff
            else:
                print('here', new_angle, prev_angle)
                # already right turned
                if new_angle > 0:
                    print( 'prev_angle < 0 new_angle > 0' )
                    diff = ( new_angle  - prev_angle)
                else:
                    print( 'prev_angle > 0 new_angle < 0' )
                    diff = ( 0 - prev_angle ) + ( new_angle )
                    if diff > 180:
                        diff = 360 - diff
                    elif diff < -180:
                        diff = 360 + diff

        print( 'diff=', diff )
        return diff
        

    def get_planned_motion(self):
        if not self.path_available:
            return []

        path = self.proposed_path[::-1]

        if len(path) > 2:
            end_node  = path[len(path) - 1]

            curr_angle = 0
            total_distance= 0
            distance      = 0

            visited_node = [] # visited node
            visiting_node = path[0]

            index = 0
            end_reached = False
            while not end_reached:
                cursor_node = path[index]

                slope = self._calc_slope( visiting_node, cursor_node )
                angle = self._cal_angle( visiting_node, cursor_node )

                if curr_angle != angle:
                    #node_points.append( visiting_node )
                    #print('node_found')
                    curr_angle = angle

                    # store change point
                    visited_node.append( visiting_node )

                total_distance += 1
                index += 1

                if cursor_node == end_node:
                    end_reached = True
                else:
                    visiting_node = cursor_node

            visited_node.append( end_node )

            init_angle = 0
            curr_node = visited_node[0]
            for i, x in enumerate(visited_node):
                next_node = visited_node[i]

                angle    = self._cal_angle( curr_node, next_node )
                distance = self._cal_distance( curr_node, next_node )
                slope    = self._calc_slope(  curr_node, next_node)

                angle_diff = self._cal_angle_diff( init_angle, angle )

                turn_dir = '_no_turn'
                if angle_diff > 0:
                    turn_dir = "_right"
                elif angle_diff < 0:
                    turn_dir = "_left"
                elif angle_diff == 0:
                    turn_dir = "_no_turn"

                self.motion_path.append({
                    'from'  : curr_node,
                    'to'    : next_node,
                    'angle' : angle_diff,
                    'distance' : distance,
                    'turn'  : turn_dir
                })
                print( 'distance=', distance, ' angle=', angle, ' slope=', slope )

                curr_node = next_node
                init_angle = angle

            #print( visited_node )
            #print( self.motion_path )
        return self.motion_path

            
