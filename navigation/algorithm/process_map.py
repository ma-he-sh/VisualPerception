import config as ENV
from algorithm.explorer import Explorer
from algorithm.algorithm import Algorithm

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
        return algo.get_generated_path()
