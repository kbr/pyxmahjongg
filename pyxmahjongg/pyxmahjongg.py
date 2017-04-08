"""
py-xmahjongg
Author: Klaus Bremer

python rewrite of the original xmahjongg from 1988:
https://www.lcdf.org/xmahjongg/

This implementation uses the same layout-files as the original one but
just the dorothys tileset. Excerpt from the original documentation:

The default tileset was originally created in color by Dorothy Robinson
<mokuren@teleport.com> with Mark A. Holm <markh@aracnet.com>. The
publically available version was in black-and-white. Holm copyrighted
the tiles in 1988, giving permission to copy and distribute for
non-profit purposes. The significantly altered color version that comes
with xmahjongg was created by Eddie Kohler in 1993.

Because of the original licens it is permitted to use the tileset for
non-profit purposes. As a consequence any commercial uses of this
program and the used tileset are prohibited.
"""


import argparse
import collections
import os.path
import random
import string
import tkinter as tk
from tkinter import TclError

from PIL import Image, ImageTk


WINDOW_POSITION_X = 140
WINDOW_POSITION_Y = 80
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800

TILE_WIDTH = 64
TILE_HEIGHT = 80
TILE_X_BORDER = 10
TILE_Y_BORDER = 10
TILES_IMAGE_WIDTH = TILE_WIDTH * 21
TILEFACE_WIDTH = TILE_WIDTH - TILE_X_BORDER
TILEFACE_HEIGHT = TILE_HEIGHT - TILE_Y_BORDER
TILEMOVE_OFFSET = 100

BUTTONS_LINE_HEIGHT = 40

BOARD_PADDING_TOP = TILE_HEIGHT
BOARD_PADDING_LEFT = int(TILE_WIDTH * 1.2)
BOARD_DEFAULT_BACKGROUND = "#FFDF9F"
BOARD_BACKGROUNDS = {
    'candy': "#DF9CBB",
    'cocoa': "#995548",
    'default': BOARD_DEFAULT_BACKGROUND,
    'fog': "#B3CDDF",
    'lavender': "#E8D5EB",
    'mint': "#CAEBB5",
    'sand': "#D8CA97",
    'santal': "#D88E91",
    'silver': "#E7EAEA",
}

LAYOUT_HELP = """
Name of layout to play. The following layouts are available: arena,
arrow, boar, bridge, ceremonial, deepwell, default, dog, dragon,
farandole, hare, horse, hourglass, monkey, ox, papillon, ram, rat,
rooster, schoon, snake, theater, tiger, wedges. Default layout is
default.
"""

BACKGROUND_HELP = """
Sets the background-color of the board. Accepts an RGB value like RRGGBB
or a color name. Color names are: candy, cocoa, default, fog, lavender,
mint, sand, santal, silver. Default background-color is default.
"""

SOLVABLE_HELP = """
Boolean argument. Tests whether the board should be solvable. The
current implementation checks, that not more than two tiles of the same
kind are stacked. Default is True.
"""

APPLICATION_DESCRIPTION = """
Python rewrite of the original xmahjongg game for Unix from 1988 with
several rewrites thereafter: (https://www.lcdf.org/xmahjongg/). So far
just dorothys tileset is implemented. Because of the original licens it
is permitted to use the tileset for non-profit purposes. Therefore any
commercial uses of this program are prohibited.
"""

APPLICATION_NAME = 'py-xmahjongg'
__version__ = '0.2 20170222'


class Tile:

    def __init__(self, board, tile_data):
        self.__dict__.update(tile_data)
        self.board = board
        self.is_selected = False
        self.image_id = None

    @property
    def position(self):
        return self.row, self.col, self.level

    def draw_image(self):
        x = BOARD_PADDING_LEFT + self.col * TILEFACE_WIDTH // 2
        x -= self.level * TILE_X_BORDER
        y = BOARD_PADDING_TOP + self.row * TILEFACE_HEIGHT // 2
        y -= self.level * TILE_Y_BORDER
        if self.is_selected:
            img = self.selected_sprite_image
        else:
            img = self.sprite_image
        if self.image_id:
            self.board.delete(self.image_id)
        self.image_id = self.board.create_image(x, y, image=img, anchor=tk.NW)

    def toggle_state(self):
        self.is_selected = not self.is_selected

    def is_above(self, other):
        """
        Returns True if the tile is positioned above the other tile.
        """
        if self.level <= other.level:
            return False
        if abs(self.row - other.row) >= 2:
            return False
        if abs(self.col - other.col) >= 2:
            return False
        return True


class Board(tk.Canvas):

    def __init__(self, application, window, tile_positions, bg):
        super().__init__(window, bg=bg)
        self.application = application
        self.background_color = bg
        self.fname = os.path.abspath(os.path.join('images', 'dorothys.png'))
        self.tiles = {}
        self.removed_tiles = []
        self.selected_tile = None
        self.levels = max(int(item[2]) for item in tile_positions)
        self.tile_positions = tile_positions
        self.tile_data = self.get_tile_data()
        self.bind('<Button-1>', self.on_click)

    def on_click(self, event):
        """
        Handle a click on the board, may be hitting a tile.
        """
        tile = self.get_clicked_tile(event)
        if tile and self.tile_is_moveable(tile):
            if not self.selected_tile:
                self.selected_tile = tile
                tile.toggle_state()
            else:
                if tile is self.selected_tile:
                    self.selected_tile = None
                    tile.toggle_state()
                else:
                    if self.selected_tile.family == tile.family:
                        self.remove_tiles(tile)
            self.draw_tiles()

    def remove_tiles(self, tile):
        """
        Removes a pair of tiles from the board.
        """
        self.selected_tile.is_selected = False
        self.delete(tile.image_id)
        self.delete(self.selected_tile.image_id)
        del self.tiles[tile.position]
        del self.tiles[self.selected_tile.position]
        self.removed_tiles.append((self.selected_tile, tile))
        self.selected_tile = None

    def undo_move(self):
        """
        Undos the last move
        """
        if self.removed_tiles:
            first_tile, second_tile = self.removed_tiles.pop()
            self.tiles[first_tile.position] = first_tile
            self.tiles[second_tile.position] = second_tile
            self.draw_tiles()

    def tile_is_moveable(self, tile):
        """
        Returns True if the tile is moveable, otherwise False.
        Moveable means that there is no tile above the the given tile
        and that there is not tile to the left or to the right.
        """
        if tile.level < self.levels:
            for row in range(tile.row-1, tile.row+2):
                for col in range(tile.col-1, tile.col+2):
                    position = (row, col, tile.level + 1)
                    if position in self.tiles:
                        return False
        for col in (tile.col-2, tile.col+2):
            for row in range(tile.row-1, tile.row+2):
                position = (row, col, tile.level)
                if position in self.tiles:
                    break
            else:
                # if not break at least one side is free
                return True
        return False

    def get_possible_moves(self):
        """
        Returns number of possible moves left.
        """
        d = collections.defaultdict(int)
        for tile in self.tiles.values():
            if self.tile_is_moveable(tile):
                d[tile.family] += 1
        return sum(sum(range(i)) for i in d.values())

    def get_clicked_tile(self, event):
        """
        Returns the clicked tile-instance or None.
        """
        def get_indexes(value):
            upper = int(value) * 2
            if int(value) < int(round(value)):
                upper += 1
            lower = max(0, upper-1)
            return lower, upper

        x = event.x
        y = event.y
        for level in range(self.levels, -1, -1):
            xpos = x - BOARD_PADDING_LEFT + TILE_X_BORDER * level
            col = xpos / TILEFACE_WIDTH
            ypos = y - BOARD_PADDING_TOP + TILE_Y_BORDER * level
            row = ypos / TILEFACE_HEIGHT
            rows = get_indexes(row)
            cols = get_indexes(col)
            for row in rows:
                for col in cols:
                    position = (row, col, level)
                    if position in self.tiles:
                        return self.tiles[position]
        return None

    @staticmethod
    def _get_tile_names():
        """
        Returns a list of all family names for the tiles.
        """
        names = ['dot%s' % n for n in range(1,10)]
        names.extend(['north', 'west', 'south', 'east',
                      'red_dragon', 'gree_dragon'])
        names.extend(['sign%s' % n for n in range(1,10)])
        names.extend(['bar%s' % n for n in range(1,10)])
        names.extend(['season'] * 4)
        names.append('white_dragon')
        names.extend(['flower'] * 4)
        return names

    def _get_tile_data(self, names):
        """
        Returns a list of a dictionaries holding informations about a
        tile family and the according image-data. This list contains 42
        entries for the tile families and pictures.
        """
        x = 0
        y = 0
        tile_data = []
        img = Image.open(self.fname).convert('RGBA')
        for name in names:
            bottom = y + TILE_HEIGHT
            right = x + TILE_WIDTH
            cropped = img.crop((x, y, right, bottom))
            sprite_image = ImageTk.PhotoImage(image=cropped)
            ys = y + 2 * TILE_HEIGHT
            bottoms = ys + TILE_HEIGHT
            select_cropped = img.crop((x, ys, right, bottoms))
            selected_sprite_image = ImageTk.PhotoImage(image=select_cropped)
            args = {
                'selected_sprite_image': selected_sprite_image,
                'sprite_image': sprite_image,
                'sprite_x': x,
                'sprite_y': y,
                'family': name,
            }
            tile_data.append(args)
            x += TILE_WIDTH
            if x >= TILES_IMAGE_WIDTH:
                x = 0
                y += TILE_HEIGHT
        return tile_data

    @staticmethod
    def _multiply_tile_data(data):
        """
        Multiplies the entries of the tile-data four times to get four
        tiles of every family. Except the sping and flower families
        which are represented by four individual images each. Returns a
        list with the multiplied datas. The data are 144 dictionaries,
        one for each tile.
        """
        md = []
        for item in data:
            if item['family'] in ('season', 'flower'):
                md.append(item)
            else:
                md.extend([item for n in range(4)])
        return md

    def get_tile_data(self):
        """
        Returns a list of dictionaries with attributes for every tile.
        """
        names = self._get_tile_names()
        data = self._get_tile_data(names)
        tile_data = self._multiply_tile_data(data)
        return tile_data

    def draw_tiles(self):
        """
        Draw all tiles: first cols, the rows from lower to upper levels.
        """
        for position in self.tile_positions:
            try:
                self.tiles[position].draw_image()
            except KeyError:
                # happens for removed tiles
                pass
        self.application.update_tiles_left(len(self.tiles))
        self.application.update_possible_moves(self.get_possible_moves())

    def create_game(self):
        """
        Creates tile-objects from the tile_positions and tile_datas
        information and places them on the board.
        """
        def tile_sort(position):
            row, col, level = position
            return level, col, row

        self.delete(tk.ALL)  # delete all tile-images
        self.tiles = {}  # delete all tile-objects
        self.removed_tiles = []
        random.shuffle(self.tile_data)  # shuffle list of dictionaries
        self.tile_positions.sort(key=tile_sort)  # sort col, row, level
        for position, tile_data in zip(self.tile_positions, self.tile_data):
            row, col, level = position
            tile_data.update({'row': row, 'col': col, 'level': level})
            tile = Tile(self, tile_data)
            self.tiles[position] = tile

    def is_solvable(self):
        """
        Checks whether the board is solvable: no more than two tiles of
        the same family should be stacked. Return True if the board is
        solvable, otherwise False.
        """
        def sort_by_level(tile):
            return tile.level

        d = collections.defaultdict(list)
        for tile in self.tiles.values():
            d[tile.family].append(tile)
        for family in d.values():
            i = 0
            tiles = sorted(family, key=sort_by_level)
            for p, q in zip(tiles[:-1], tiles[1:]):
                if q.is_above(p):
                    i += 1
                    if i >= 3:
                        return False
        return True


class Application(tk.Frame):

    def __init__(self, master, width, height,
                 tile_positions, background_color, should_be_solvable):
        super().__init__(master)
        master.title(APPLICATION_NAME)
        self.should_be_solvable = should_be_solvable
        self.pack()
        self.canvas = tk.Canvas(self, width=width, height=height)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.create_buttons()
        self.create_text_fields(width)
        self.create_board(width, height, tile_positions, background_color)

    def create_buttons(self):
        self.btn_quit = tk.Button(self.canvas, text='Quit', command=self.quit)
        self.btn_quit.place(x=10, y=8, height=24, width=80)
        self.btn_new_game = tk.Button(
            self.canvas, text='New Game', command=self.new_game)
        self.btn_new_game.place(x=100, y=8, height=24, width=100)
        self.btn_undo = tk.Button(
            self.canvas, text='Undo', command=self.undo_move)
        self.btn_undo.place(x=210, y=8, height=24, width=80)

    def create_text_fields(self, width):
        self.tiles_left_field = self.canvas.create_text(
            width-40, 20, text='', fill="#800000")
        self.possible_moves_field = self.canvas.create_text(
            width-100, 20, text='', fill="#408000")

    def create_board(self, width, height, tile_positions, background_color):
        self.board = Board(self, self.canvas, tile_positions, background_color)
        self.board.place(x=0, y=BUTTONS_LINE_HEIGHT,
            width=width, height=height-BUTTONS_LINE_HEIGHT)
        self.new_game()

    def new_game(self):
        while True:
            self.board.create_game()
            if self.should_be_solvable:
                if self.board.is_solvable():
                    break
        self.board.draw_tiles()

    def undo_move(self):
        self.board.undo_move()

    def update_tiles_left(self, num):
        self.canvas.itemconfigure(self.tiles_left_field, text=str(num))

    def update_possible_moves(self, num):
        self.canvas.itemconfigure(self.possible_moves_field, text=str(num))


def read_layout(name='deepwell'):
    """
    Returns a list will all tile-positions for the given layout.
    The list must have 144 tuples with row, column, level.
    """
    fname = os.path.abspath(os.path.join('layouts', name))
    with open(fname) as f:
        return [tuple(map(int, line.strip().split()))
                for line in f if not line.startswith('#')]


def get_window_dimension(tile_positions):
    """
    Returns the width and height of the window to display.
    """
    rows = max(int(item[0]) for item in tile_positions)
    columns = max(int(item[1]) for item in tile_positions)
    layout_width = TILE_WIDTH + TILEFACE_WIDTH * columns // 2
    layout_height = TILE_HEIGHT + TILEFACE_HEIGHT * rows // 2
    window_width = layout_width + 2 * BOARD_PADDING_LEFT
    window_height = layout_height + 2 * BOARD_PADDING_TOP + BUTTONS_LINE_HEIGHT
    return window_width, window_height


def get_background_color(bg):
    """
    Returns the background-color for the board.
    """
    if bg not in BOARD_BACKGROUNDS and len(bg) == 6:
        for char in bg:
            if char not in string.hexdigits:
                break
        else:
            # may be valid color sequence
            return '#{}'.format(bg)
    return BOARD_BACKGROUNDS.get(bg, BOARD_DEFAULT_BACKGROUND)


def get_commandline_arguments():
    parser = argparse.ArgumentParser(description=APPLICATION_DESCRIPTION)
    parser.add_argument('-b', '--background',
                        nargs='?', default='default',
                        dest='background',
                        help=BACKGROUND_HELP)
    parser.add_argument('-l', '--layout',
                        nargs='?', default='default',
                        dest='layout',
                        help=LAYOUT_HELP)
    parser.add_argument('-s', '--solvable',
                        type=bool,
                        nargs='?', default=True,
                        dest='solvable',
                        help=SOLVABLE_HELP)
    args = parser.parse_args()
    return args


def main(args):
    print('\nrunning: {} v{}'.format(APPLICATION_NAME, __version__))
    tile_positions = read_layout(name=args.layout)
    background_color = get_background_color(bg=args.background)
    width, height = get_window_dimension(tile_positions)
    root = tk.Tk()
    root.geometry('{}x{}+{}+{}'.format(
        width, height, WINDOW_POSITION_X, WINDOW_POSITION_Y))
    try:
        app = Application(root, width, height, tile_positions,
                          background_color, args.solvable)
    except TclError as err:
        print('error: {}'.format(err))
    else:
        root.mainloop()
    print('exit {}\n'.format(APPLICATION_NAME))


if __name__ == '__main__':
    main(args=get_commandline_arguments())
