import numpy as np
import cv2
import matplotlib.pyplot as plt

class NodeObj():
    def __init__(self, x, y, r):
        self.x = x # x pos
        self.y = y # y pos
        self.r = r # r radius
        self.is_obstacle = False
        self.repulsion = 0

    def set_as_obstacle(self, is_obstacle):
        self.is_obstacle = is_obstacle

    def set_repulsion(self, repulsion):
        self.repulsion = repulsion


class Exploration():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cost = 0
        self.parent_node = None

    def set_score(self, score):
        self.score = score

    def set_parent_node(self, parent):
        self.parent_node = parent

class Algorithm():
    def __init__(self, start_pos, goal_pos, map_size ):
        self.__name__ = "Dijiskstra"
        self.start_pos = start_pos
        self.goal_pos  = goal_pos
        self.map_size  = map_size

        self.obstacles = []

    def set_obstacles(self, obstacles=[]):
        self.obstacles = obstacles

    def render_obstacles(self):
        pass
