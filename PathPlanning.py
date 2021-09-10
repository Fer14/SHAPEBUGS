import math
import time, sys
from bresenham import bresenham
from enum import Enum

class Direction(Enum):
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3

class State(Enum):
    STRAIGHT_LINE = 0
    SURROUND = 1
    BEST_SURROUNDED = 2


class PathPlanning:

    def __init__(self, start, goal, map):
        self.start = start
        self.goal = goal
        self.current_pos = start
        self.map = map
    
    
    def finished(self):
        return self.current_pos == self.goal
    
    
    def next_step(self):
        # Placeholder
        return self.current_pos
    
    
    def distance(self, p0, p1):
        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
    
    
    def neighbors(self, p):
        return [(p[0]-1, p[1]), (p[0]+1, p[1]), (p[0], p[1]-1), (p[0], p[1]+1)]
    
    
    def corner_neighbors(self, p):
        return [(p[0]-1, p[1]-1), (p[0]-1, p[1]+1), (p[0]+1, p[1]-1), (p[0]+1, p[1]+1)]
    
    
    def closest_neighbor(self, p):
        min_dist = math.inf
        closest_neighbor = None
        for n in self.neighbors(p):
            if self.distance(n, self.goal) < min_dist:
                min_dist = self.distance(n, self.goal)
                closest_neighbor = n
        return closest_neighbor


class Bug(PathPlanning):
    
    def __init__(self, start, goal, map):
        super().__init__(start, goal, map)
        self.line = list(bresenham(start[0], start[1], goal[0], goal[1]))
        self.last_wall = Direction.RIGHT
        self.current_state = State.STRAIGHT_LINE
        self.left_hit = False
    
    
    def straight_line(self):
        if self.map[self.line[0][1]][self.line[0][0]] == 255:
            self.current_pos = self.line[0]
            self.line.pop(0)
        else:
            self.current_state = State.SURROUND
            if self.map[self.current_pos[1]][self.current_pos[0] + 1] == 0:
                self.last_wall = Direction.RIGHT
            elif self.map[self.current_pos[1]][self.current_pos[0] - 1] == 0:
                self.last_wall = Direction.LEFT
            elif self.map[self.current_pos[1] + 1][self.current_pos[0]] == 0:
                self.last_wall = Direction.DOWN
            elif self.map[self.current_pos[1] - 1][self.current_pos[0]] == 0:
                self.last_wall = Direction.UP
            else:
                # It touched in a corner
                if self.map[self.current_pos[1] + 1][self.current_pos[0] + 1] == 0:
                    self.current_pos = (self.current_pos[0] + 1, self.current_pos[1])
                    self.last_wall = Direction.DOWN
                elif self.map[self.current_pos[1] + 1][self.current_pos[0] - 1] == 0:
                    self.current_pos = (self.current_pos[0], self.current_pos[1] + 1)
                    self.last_wall = Direction.LEFT
                elif self.map[self.current_pos[1] - 1][self.current_pos[0] - 1] == 0:
                    self.current_pos = (self.current_pos[0] - 1, self.current_pos[1])
                    self.last_wall = Direction.UP
                elif self.map[self.current_pos[1] - 1][self.current_pos[0] + 1] == 0:
                    self.current_pos = (self.current_pos[0], self.current_pos[1] - 1)
                    self.last_wall = Direction.RIGHT
                else:
                    # This never happens
                    pass
    
    
    def surround(self):
        x, y = self.current_pos
        if self.last_wall == Direction.RIGHT:
            if self.map[y][x + 1] == 255:
                self.current_pos = (x + 1, y)
                self.last_wall = Direction.DOWN
                self.left_hit = True
            else:
                self.last_wall = Direction.UP
        elif self.last_wall == Direction.UP:
            if self.map[y - 1][x] == 255:
                self.current_pos = (x, y - 1)
                self.last_wall = Direction.RIGHT
                self.left_hit = True
            else:
                self.last_wall = Direction.LEFT
        elif self.last_wall == Direction.LEFT:
            if self.map[y][x - 1] == 255:
                self.current_pos = (x - 1, y)
                self.last_wall = Direction.UP
                self.left_hit = True
            else:
                self.last_wall = Direction.DOWN
        elif self.last_wall == Direction.DOWN:
            if self.map[y + 1][x] == 255:
                self.current_pos = (x, y + 1)
                self.last_wall = Direction.LEFT
                self.left_hit = True
            else:
                self.last_wall = Direction.RIGHT


class Bug1(Bug):
    
    def __init__(self, start, goal, map):
        super().__init__(start, goal, map)
        self.hit_point = self.start
        self.surroundings = {}
    
    
    def next_step(self):
        if self.current_state == State.STRAIGHT_LINE:
            if self.map[self.line[0][1]][self.line[0][0]] == 255:
                self.current_pos = self.line[0]
                self.line.pop(0)
            else:
                self.straight_line()
                self.hit_point = self.current_pos
                self.left_hit = False
        
        elif self.current_state == State.SURROUND:
            self.surround()
            self.surroundings[self.current_pos] = self.distance(self.current_pos, self.goal)
            
            if self.current_pos == self.hit_point and self.left_hit:
                self.current_state = State.BEST_SURROUNDED
        
        elif self.current_state == State.BEST_SURROUNDED:
            self.current_pos = min(self.surroundings, key=self.surroundings.get)
            self.current_state = State.STRAIGHT_LINE
            self.line = list(bresenham(self.current_pos[0], self.current_pos[1], self.goal[0], self.goal[1]))
            
        
        return self.current_pos


class Bug2(Bug):
    
    def __init__(self, start, goal, map):
        super().__init__(start, goal, map)
    
    
    def next_step(self):
        if self.current_state == State.STRAIGHT_LINE:
            self.straight_line()
        
        elif self.current_state == State.SURROUND:
            self.surround()
            
            if (self.current_pos in self.line) and self.left_hit:
                while self.line[0] != self.current_pos:
                    self.line.pop(0)
                self.current_state = State.STRAIGHT_LINE
        
        return self.current_pos



class ValueIteration(PathPlanning):
    
    def __init__(self, start, goal, map):
        super().__init__(start, goal, map)
        self.neighbors_graph = {}
        self.generate_neighbors()
        self.distances = {}
        self.generate_distances()
        self.dist_goal_start = self.distances[self.start]
    
    
    def generate_distances(self):
        for key in self.neighbors_graph.keys():
            self.distances[key] = math.inf
        self.distances[(self.goal[0],self.goal[1])] = 0
        
        queue = [self.goal]
        
        # Breadth first approach
        while queue:
            current = queue.pop(0)
            
            for neighbor in self.neighbors_graph[current]:
                is_corner_neighbor = (((current[0] - neighbor[0]) * (current[1] - neighbor[1])) != 0)
                dist = self.distances[current]
                if is_corner_neighbor:
                    dist += math.sqrt(2)
                else:
                    dist += 1
                
                if dist < self.distances[neighbor] and dist < self.distances[self.start]:
                    queue.append(neighbor)
                    self.distances[neighbor] = dist
    
    
    def generate_neighbors(self):
        # for each point
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                # if it is not a border
                if self.map[y][x] != 0:
                    neighbors = []
                    # for each of its neighbors
                    for i in range(-1,2):
                        if x+i >= 0 and x+i < len(self.map[0]):
                            for j in range(-1,2):
                                if y+j >= 0 and y+j < len(self.map):
                                    # if they are not borders or the same node
                                    if i != 0 or j != 0:
                                        if self.map[y+j][x+i] != 0:
                                            neighbors.append((x+i, y+j))
                    self.neighbors_graph[(x,y)] = neighbors
    
    
    def next_step(self):
        min_dist = math.inf
        min_neigh = None
        for neighbor in self.neighbors_graph[self.current_pos]:
            dist = self.distances[neighbor]
            if dist < min_dist:
                min_dist = dist
                min_neigh = neighbor
        self.current_pos = min_neigh
        return min_neigh
    
    
    def distance_map(self):
        dist_map = {}
        dist_mul = self.dist_goal_start/254
        for key in self.distances.keys():
            if self.distances[key] > self.dist_goal_start:
                dist_map[key] = 255
            else:
                dist_map[key] = self.distances[key]//dist_mul
        return dist_map
