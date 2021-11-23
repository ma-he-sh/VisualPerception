from queue import PriorityQueue
from algorithm.node import Node

class Algorithm():
    def __init__(self, map, start, goal, resolution ):
        self.map = map
        self.start = start
        self.goal  = goal
        self.resolution = resolution
        self.pos   = 0
        self.visited_list = {}
        self.closed_list  = {}
        self.g_scores = None
        self.path_found = False
        self.cursor = 0

        self.queue = PriorityQueue()

    def init(self):
        self.queue.put( ( self.cursor, self.pos, self.start ) )
        self.visited_list = {self.start}
        self.g_scores = { Node:float("inf") for xi in self.map for Node in xi }
        self.g_scores[ self.start ] = 0

    def exec(self, plt):
        while not self.queue.empty():

            # get the current node
            curr_node = self.queue.get()[2]

            # check if goal is already reached
            if curr_node.is_goal:
                # inform that goal has been found
                self.path_found = True
                return self.path_found

            # increament the g_score
            new_g_score = self.g_scores[ curr_node ] + curr_node.g_cost

            for neighbour in curr_node.neighbours:
                if new_g_score < self.g_scores[neighbour]:
                    self.g_scores[neighbour] = new_g_score + neighbour.g_cost

                    # if the neighbout is not visted
                    if neighbour not in self.visited_list:
                        self.closed_list[neighbour] = curr_node
                        self.visited_list.add( neighbour )
                        # mark as visiting
                        #plt.plot( neighbour.x, neighbour.y, color="r", marker="s" )

                        self.cursor += 1
                        self.queue.put( ( self.g_scores[neighbour], self.cursor, neighbour ) )

            if curr_node not in ( self.start, self.goal ):
                # mark as visited
                #plt.plot( neighbour.x, neighbour.y, color="g", marker="s" )
                pass

        return self.path_found

    def generate_path(self, plt ):
        curr_cost=0
        # trace the path
        curr_node=self.goal
        while curr_node in self.closed_list:
            if curr_node not in ( self.start, self.goal ):
                curr_cost += curr_node.g_cost
            curr_node = self.closed_list[curr_node]
            plt.plot( curr_node.x, curr_node.y, color="r", marker="s" )
            plt.pause(0.05)

    def run(self, i ):
        print("run--->")
        pass