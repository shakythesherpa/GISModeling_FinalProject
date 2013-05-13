#==============================================================================#
# Name:         GIS Modeling and Problem Solving Final Project
# Purpose:      Implementing Langton's Ant using Cellular Automata and Agent Based Model
# Author:      Shaky Sherpa
# Created:     05/05/2013
# Attribution:  The work is based partly on codes from Allen Downey and Gordon Green

#==============================================================================#
"""Importing all the necessary modules"""

import numpy as np
import math
import sys
from Tkinter import END
from CellWorld import CellWorld
from World import Animal, Interpreter
from World import World


#==============================================================================#
"""This part of the code is to draw the grid cells"""

# The user can create a cell by clicking or dragging

class CellWorld(World):
    """Contains cells and animals that move between cells."""
    def __init__(self, canvas_size=500, cell_size=10, interactive=False):
        World.__init__(self)
        self.title('GIS Modling and Problem Solving Final Project')
        self.canvas_size = canvas_size
        self.cell_size = cell_size
        self.cells = {}

        if interactive:
            self.make_canvas()
            self.make_control()

    def make_canvas(self):
        """Creates the GUI."""
        self.canvas = self.ca(width=self.canvas_size,
                              height=self.canvas_size,
                              bg='black',
                              scale = [self.cell_size, self.cell_size])

    def make_control(self):
       """Allow the user to draw the cells manually."""

       self.row([0,1,0])
       self.la(text='Cell size: ')
       self.cell_size_en = self.en(width=10, text=str(self.cell_size))
       self.bu(text='resize', command=self.rescale)
       self.endrow()

    def bind(self):
        """Creates bindings for the canvas."""
        self.canvas.bind('<ButtonPress-1>', self.click)
        self.canvas.bind('<B1-Motion>', self.click)

    def click(self, event):
        """Event handler for clicks and drags.

        It creates a new cell or toggles an existing cell.
        """

        x, y = self.canvas.invert([event.x, event.y])
        i, j = int(math.floor(x)), int(math.floor(y))

        # toggle the cell if it exists else we create it otherwise
        cell = self.get_cell(i,j)
        if cell:
            cell.toggle()
        else:
            self.make_cell(x, y)

    def make_cell(self, i, j):
        """Creates and returns a new cell at i,j."""
        cell = Cell(self, i, j)
        self.cells[i,j] = cell
        return cell

    def cell_bounds(self, i, j):
        """Return the bounds of the cell with indices i, j."""
        p1 = [i, j]
        p2 = [i+1, j]
        p3 = [i+1, j+1]
        p4 = [i, j+1]
        bounds = [p1, p2, p3, p4]
        return bounds

    def get_cell(self, i, j, default=None):
        """Gets the cell at i, j or returns the default value."""
        cell = self.cells.get((i,j), default)
        return cell

    four_neighbors = [(1,0), (-1,0), (0,1), (0,-1)]
    eight_neighbors = four_neighbors + [(1,1), (1,-1), (-1,1), (-1,-1)]

    def get_four_neighbors(self, cell, default=None):
        """Return the four Von Neumann neighbors of a cell."""
        return self.get_neighbors(cell, default, CellWorld.four_neighbors)

    def get_eight_neighbors(self, cell, default=None):
        """Returns the eight Moore neighbors of a cell."""
        return self.get_neighbors(cell, default, CellWorld.eight_neighbors)

    def get_neighbors(self, cell, default=None, deltas=[(0,0)]):
        """Return the neighbors of a cell."""

        i, j = cell.indices
        cells = [self.get_cell(i+di, j+dj, default) for di, dj in deltas]
        return cells

    def rescale(self):
        """Event handler that rescales the world.

        Reads the new scale from the GUI,
        changes the canvas transform, and redraws the world.
        """
        cell_size = self.cell_size_en.get()
        cell_size = int(cell_size)
        self.canvas.transforms[0].scale = [cell_size, cell_size]
        self.redraw()

    def redraw(self):
        """Clears the canvas and redraws all cells and animals."""
        self.canvas.clear()
        for cell in self.cells.itervalues():
            cell.draw()
        for animal in self.animals:
            animal.draw()


class Cell(object):
    """A rectangular region in CellWorld"""
    def __init__(self, world, i, j):
        self.world = world
        self.indices = i, j
        self.bounds = self.world.cell_bounds(i, j)

        # color that is used for a marked cell
        self.marked_options = dict(fill='white', outline='gray80')

        # color that is used for an unmarked cell
        self.unmarked_options = dict(fill='black', outline='gray80')

        self.marked = False
        self.draw()

    def draw(self):
        """Draw the cell."""
        if self.marked:
            options = self.marked_options
        else:
            options = self.unmarked_options

        # bounds returns all four corners and then it is
        # passed to Canvas.rectangle
        coords = self.bounds[::2]
        self.item = self.world.canvas.rectangle(coords, **options)

    def undraw(self):
        """Delete any items with this cell's tag."""
        self.item.delete()
        self.item = None

    def get_config(self, option):
        """Gets the configuration of this cell."""
        return self.item.cget(option)

    def config(self, **options):
        """Configure this cell with the given options."""
        self.item.config(**options)

    def mark(self):
        """Marks this cell."""
        self.marked = True
        self.config(**self.marked_options)

    def unmark(self):
        """Unmarks this cell."""
        self.marked = False
        self.config(**self.unmarked_options)

    def is_marked(self):
        """Checks whether this cell is marked."""
        return self.marked

    def toggle(self):
        """Toggles the state of this cell."""
        if self.is_marked():
            self.unmark()
        else:
            self.mark()

#========================================================================#

"""This part of code is to run the Model"""

#The Langton's ant model follows the following set of rules.

#1. The ant starts out on a grid containing black and white cells
#2. If the ant is on a black square, it turns right??and moves forward one unit.
#3. If the ant is on a white square, it turns left??and moves forward one unit.
#4. When the ant leaves a square, it inverts the color of the last cell


class AntWorld(CellWorld):
    """Provides a grid of cells that Turmites occupy."""

    def __init__(self, canvas_size=600, cell_size=10):
        CellWorld.__init__(self, canvas_size, cell_size)
        self.title('GIS Modeling and Problem Solving Final Project- Shaky Sherpa')

        # the interpreter executes user-provided code
        self.inter = Interpreter(self, globals())
        self.setup()

    def setup(self):
        """Makes the GUI."""
        self.row()
        self.make_canvas()

        # right frame
        self.col([0,0,1,0])

        self.row([1,1,1])
        self.bu(text='Shaky Ant', command=self.make_turmite)
        self.endrow()

        # make the run and stop buttons
        self.row([1,1,1,1], pady=30)
        self.bu(text='Run', command=self.run)
        self.bu(text='Stop', command=self.stop)
        self.bu(text='Clear', command=self.clear)
        self.bu(text='Slow', command=self.step)

        self.endrow()

    def make_turmite(self):
        """Makes a turmite."""
        turmite = Turmite(self)
        return turmite

    def clear(self):
        """Removes all the animals and all the cells."""
        for animal in self.animals:
            animal.undraw()
        for cell in self.cells.values():
            cell.undraw()
        self.animals = []
        self.cells = {}



class Turmite(Animal):
    """
    Attributes:
        dir: direction, one of [0, 1, 2, 3]
    """

    def __init__(self, world):
        Animal.__init__(self, world)
        self.dir = 0
        self.draw()

    def draw(self):
        """Draw the Turmite."""
        # get the bounds of the cell
        cell = self.get_cell()
        bounds = self.world.cell_bounds(self.x, self.y)

        # draw a triangle inside the cell, pointing in the
        # appropriate direction
        bounds = rotate(bounds, self.dir)
        mid = vmid(bounds[1], bounds[2])
        self.tag = self.world.canvas.polygon([bounds[0], mid, bounds[3]],
                                             fill='red')

    def fd(self, dist=1):
        """Moves forward."""
        if self.dir==0:
            self.x += dist
        elif self.dir==1:
            self.y += dist
        elif self.dir==2:
            self.x -= dist
        else:
            self.y -=dist
        self.redraw()

    def bk(self, dist=1):
        """Moves back."""
        self.fd(-dist)

    def rt(self):
        """Turns right."""
        self.dir = (self.dir-1) % 4
        self.redraw()

    def lt(self):
        """Turns left."""
        self.dir = (self.dir+1) % 4
        self.redraw()

    def get_cell(self):
        """get the cell this ant is on (creating one if necessary)"""
        x, y, world = self.x, self.y, self.world
        return world.get_cell(x,y) or world.make_cell(x,y)

    def step(self):
        """Implements the rules for Langton's Ant.

        (see http://mathworld.wolfram.com/LangtonsAnt.html)
        """
        cell = self.get_cell()
        if cell.is_marked():
            self.lt()
        else:
            self.rt()
        cell.toggle()
        self.fd()



# these are functions that perfrom the vector operations

def vadd(p1, p2):
    """Adds vectors p1 and p2 (returns a new vector)."""
    return [x+y for x,y in zip(p1, p2)]

def vscale(p, s):
    """Multiplies p by a scalar (returns a new vector)."""
    return [x*s for x in p]

def vmid(p1, p2):
    """Returns a new vector that is the pointwise average of p1 and p2."""
    return vscale(vadd(p1, p2), 0.5)

def rotate(v, n=1):
    """Rotates the elements of a sequence by (n) places.
    Returns a new list.
    """
    n %= len(v)
    return v[n:] + v[:n]


if __name__ == '__main__':
    world = CellWorld(interactive=True)
    world.bind()
    world.mainloop()
    world = AntWorld()
    world.mainloop()

