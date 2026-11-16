#!/bin/python3

"""
This is a python script to generate a random maze for gazebo simulation. 

Executing this script (./generate_maze) will create a new file named tp4_maze.sdf that will contains the description of a maze for gazebo simulation.
"""

import random as random


class Cell():
    """
        This class handle cells of the maze grid. A Cell has:
        x : (int) the x position of the cell in the grid
        y : (int) the y position of the cell in the grid
        state : (int) the state of a cell (wall, visited...)
    """

        
    def __init__(self, x:int=0, y:int=0):
        """ Constructor of the class. When created a cell is set as a wall
        Args:
            x (int, optional): x position of the cell in the grid. Defaults to 0.
            y (int, optional): y position of the cell in the grid. Defaults to 0.
            """
        self.mask_wall:int = 0x01
        self.mask_visited:int = 0x02

        self.x:int = x
        self.y:int = y

        self.state:int = self.mask_wall
    
    def __str__(self) -> str:
        """To convert a Cell into a string

        Returns:
            str: The cell values
        """
        if self.is_visited() and self.is_wall():
            return "x"
        elif self.is_visited() and not self.is_wall():
            return " "
        return "."
    
    def __repr__(self) -> str:
        """To convert a Cell into a string (when printing list)

        Returns:
            str: The cell values
        """
        return f"(x:{self.x},y:{self.y})"
    
    def set_as_visited(self):
        """ Function to set the state of the cell as visited
        """
        self.state = self.state | self.mask_visited
        
    def is_visited(self) -> bool:
        """ Function to test if the cell has been visited or not

        Returns:
            bool: True if the cell has been visited, False otherwise
        """
        return (self.state & self.mask_visited)!=0

    def set_as_wall(self, value=True):
        """ Function to set the state of the cell has a wall

        Args:
            value (bool, optional): True if the cell is a wall, False otherwise. Defaults to True.
        """
        if value:
            self.state = self.state | self.mask_wall
        else:
            self.state = self.state & (~self.mask_wall)
            
    def __eq__(self, other) -> bool:
        """ Override the == operator

        Args:
            other (Cell): The other cell to compare

        Returns:
            bool: True if the two cells have the same coordinates, False otherwise
        """
        return self.x == other.x and self.y == other.y

    def is_wall(self) -> bool:
        """ Function to test if a cell is a wall or not

        Returns:
            bool: True if the cell is a wall, False otherwise
        """
        return (self.state & self.mask_wall)!=0
    
    def to_sdf_link(self, size_x:float, size_y:float, size_z:float, width:float, height:float) -> str:
        """ Function to convert the cell into an sdf link

        Args:
            size_x (float): The x size of a cell (in meter)
            size_y (float): The y size of a cell (in meter)
            size_z (float): The z size of a cell (in meter)
            width (float): The total x size of the maze (in meter)
            height (float): The total y size of the maze (in meter)

        Returns:
            str: the sdf string corresponding to the cell
        """
        
        # Create a link corresponding to the cell
        sdf =  f"\t<link name=\"cell_{self.x}_{self.y}\">\n"
        # Set the pose of the link according to the coordinates of the cell and the size of a grid cell
        sdf += f"\t\t<pose>{self.x*size_x-width/2.0} {self.y*size_y-height/2.0} {size_z/2.0} 0 0 0</pose>\n"
        # Add an mass to the cell in the sdf file (should be heavy no to move when the robot hits the wall)
        sdf += f"\t\t<inertial><mass>100</mass></inertial>\n"
        # Add a collision and visual shapes (a cell will be representated has a box)
        sdf += f"\t\t<collision name=\"collision_{self.x}_{self.y}\"><geometry><box><size>{size_x} {size_y} {size_z}</size></box></geometry></collision>\n"
        sdf += f"\t\t<visual name=\"visual_{self.x}_{self.y}\"><geometry><box><size>{size_x} {size_y} {size_z}</size></box></geometry></visual>\n"
        # Close the link
        sdf += f"\t</link>\n"
        return sdf
        
class Maze():
    """ Class to handle a maze (a list of cell)
    """
    def __init__(self, width:int, height:int):
        """ Constructor of the class

        Args:
            width (int): Number of x cells
            height (int): Number of y cells
        """
        self.width:int = width
        self.height:int = height
        self.maze:list[Cell] = list()
        self.wall_list:list[Cell] = list() # this is a member of the class for testing purpose
        
        # init the list of cells
        self.init()
            
    def init(self):
        """ Function to init the list of cells according to width and height
        """
        # clear the maze if it already exists
        self.maze = []
        self.wall_list = []
        # loop over the y cells (the columns)
        for x in range(0, self.width):
            row = []
            for y in range(0, self.height):
                row.append(Cell(x=x, y=y))
            self.maze.append(row)

    def __str__(self) -> str:
        """ Function to convert a maze into a string

        Returns:
            str: the maze values as string
        """
        txt = "   "
        for x in range(self.width):
            txt += f"{x:2} "
        txt += "\n"
        for y in range(self.height):
            txt += f"{y:2} "
            for x in range(self.width):
                
                added_flag:bool = False
                for c in self.wall_list:
                    if c == self.maze[x][y]:
                        txt += " ? "
                        added_flag = True
                        break
                if not added_flag:
                    txt += f" {self.maze[x][y]} "
                
            txt += "\n"
        return txt
    
    def __repr__(self) -> str:
        """ Function to convert a maze into a string (for list, debug)
        Returns:
            str: the maze values as string
        """
        return self.__str__()
    
    def add_surroundings(self, cell:Cell):
        """_summary_

        Args:
            wall_list (list[Cell]): _description_
            cell (Cell): _description_
        """
        # search around the cell, all the surondings cells that are not visited and are not already in the wall_list, are added in the wall_list
        for x in [-1, 1]:
            new_x = x+cell.x
            if self.width-1 > new_x >= 1 and not self.maze[new_x][cell.y].is_visited():
                if self.maze[new_x][cell.y] not in self.wall_list:
                    self.maze[new_x][cell.y].set_as_wall()
                    self.wall_list.append(self.maze[new_x][cell.y])
        for y in [-1, 1]:
            new_y = y+cell.y
            if self.height-1 > new_y >= 1 and not self.maze[cell.x][new_y].is_visited():
                if self.maze[cell.x][new_y] not in self.wall_list:
                    self.maze[cell.x][new_y].set_as_wall()
                    self.wall_list.append(self.maze[cell.x][new_y])

    def build(self):
        """ Function to build the maze. The algorithm can be found here : https://en.wikipedia.org/wiki/Maze_generation_algorithm (Iterative randomized Prim's algorithm (without stack, without sets)): 
        """
        
        # init all the cells as walls
        self.init()
        
        # start to build the maze for the center
        start_x:int = int(self.width/2)
        start_y:int = int(self.height/2)

        # the starting point should be a visited free space
        self.maze[start_x][start_y].set_as_wall(False)
        self.maze[start_x][start_y].set_as_visited()
        # Add the surroundings of the starting cell in the wall_list
        self.add_surroundings(self.maze[start_x][start_y])
                
        # loop over the wall list, until we still have walls to test
        while len(self.wall_list) != 0:
            i = 0
            if len(self.wall_list) > 1:
                # the wall_list contains several walls, take one randomly
                i = random.randrange(0, len(self.wall_list)-1)
            # remove the considered wall from the list and get it as the current tested cell
            cell = self.wall_list.pop(i)
            # set the current cell as visited
            self.maze[cell.x][cell.y].set_as_visited()
            
            # check the surrounding the current cell and count the number of visited cell
            nb_visited_around:int = 0
            for dx in [-1, 1]:
                if 1 <= cell.x + dx < self.width-1:
                    if not self.maze[cell.x+dx][cell.y].is_wall():
                        nb_visited_around += 1
            for dy in [-1, 1]:
                if 1 <= cell.y + dy < self.height-1:
                    if not self.maze[cell.x][cell.y+dy].is_wall():
                        nb_visited_around += 1
            
            if nb_visited_around == 1:
                # only one cell has been visited around the current one, the current should be a free space, and it sourroundings should be added in the wall_list
                self.maze[cell.x][cell.y].set_as_wall(False)
                self.add_surroundings(self.maze[cell.x][cell.y])
                
        # close the maze
        for x in range(0, self.width):
            self.maze[x][0].set_as_wall(True)
            self.maze[x][0].set_as_visited()
            self.maze[x][self.height-1].set_as_wall(True)
            self.maze[x][self.height-1].set_as_visited()
        for y in range(0, self.height):
            self.maze[0][y].set_as_wall(True)
            self.maze[0][y].set_as_visited()
            self.maze[self.width-1][y].set_as_wall(True)
            self.maze[self.width-1][y].set_as_visited()
            
        # add an exit to the maze
        self.add_exit()
            
    def add_exit(self):
        """ Function to add an exit to the maze
        """
        while True:
            # the loop will break when an exit has been found
            # the exit if searched randomly on the limit of the maze
            
            # randomly take the side of the exit (top, bottom, left or right)
            side = random.randint(0,3)
            match side:
                # for the correponding side, get a random cell
                case 0:
                    x = 0
                    dx = 1
                    dy = 0
                    y = random.randint(1, self.height-2)
                case 1:
                    x = self.width-1
                    dx = -1
                    dy = 0
                    y = random.randint(1, self.height-2)
                case 2:
                    x = random.randint(1, self.width-2)
                    dx = 0
                    dy = 1
                    y = 0
                case 3:
                    x = random.randint(1, self.width-2)
                    dx = 0
                    dy = -1
                    y = self.height-1
            # check if the cell can be an exit (has a free cell before)
            if not self.maze[x+dx][y+dy].is_wall():
                # if it can be an exit, mark it as a free cell and break the loop
                self.maze[x][y].set_as_wall(False)
                break
            
    def to_sdf_model(self, size_x:float, size_y:float, size_z:float) -> str:
        """ Function to convert the maze into a sdf model (each cell will be a box)

        Args:
            size_x (float): the x size of a box
            size_y (float): the y size of a box
            size_z (float): the z size of a box

        Returns:
            str: The sdf model corresponding to the maze 
        """
        
        # the name of the model
        model_name:str = "maze"
        
        # sdf header
        sdf = f"<?xml version='1.0'?>\n<sdf version='1.4'>\n<model name=\"{model_name}\">\n<static>true</static>\n"
        
        # add all the cells
        for cells in self.maze:
            for cell in cells:
                if cell.is_wall():
                    sdf += cell.to_sdf_link(size_x, size_y, size_z, self.width*size_x, self.height*size_y)
                    sdf += f"\n"
        
        # sdf footer
        sdf += f"</model>\n</sdf>\n"
        return sdf 

def main():
    size_x = 1.0
    size_y = 1.0
    size_z = 0.5
    nb_x = 10
    nb_y = 10
     
    filename = "tp4_maze"
    
    maze = Maze(nb_x, nb_y)
    maze.build()
    
    with open(f"{filename}.sdf", "w") as sdf_file:
        sdf_file.write(maze.to_sdf_model(size_x, size_y, size_z))


if __name__=="__main__":
    main()