class Node():
    def __init__(self, index, x, y, r):
        self.index = index
        self.x = x
        self.y = y
        self.r = r      # radius or the resolutin
        self.pos         = [x, y]
        self.visited     = False
        self.is_start    = False
        self.is_goal     = False
        self.is_obstacle = False
        self.g_cost = 1
        self.parent = None
        self.neighbours  = []
    
    def reset_gcost(self):
        self.g_cost = 1

    def get_neigbours(self):
        return self.neighbours