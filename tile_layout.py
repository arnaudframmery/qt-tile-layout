from PyQt5 import QtWidgets, QtCore

from tile import Tile


class TileLayout(QtWidgets.QGridLayout):
    """
    A layout where the user can drag and drop widgets and resize them
    """

    def __init__(self, row_number, column_number, vertical_span, horizontal_span, vertical_spacing=5,
                 horizontal_spacing=5, *args, **kwargs):
        super(TileLayout, self).__init__(*args, **kwargs)

        # geometric parameters
        self.setVerticalSpacing(vertical_spacing)
        self.setHorizontalSpacing(horizontal_spacing)
        self.row_number = row_number
        self.column_number = column_number
        self.vertical_span = vertical_span
        self.horizontal_span = horizontal_span

        # logic parameters
        self.drag_and_drop = True
        self.resizable = True
        self.widget_to_drop = None
        self.tile_map = []
        self.widget_tile_couple = {'widget': [], 'tile': []}

        # design parameters
        self.cursor_idle = QtCore.Qt.ArrowCursor
        self.cursor_grab = QtCore.Qt.OpenHandCursor
        self.cursor_resize_horizontal = QtCore.Qt.SizeHorCursor
        self.cursor_resize_vertical = QtCore.Qt.SizeVerCursor

        self.__set_grid_minimal_size()
        self.__create_tile_map()

    def add_widget(self, widget, from_row, from_column, row_span=1, column_span=1):  # TODO: add assertions
        """adds a widget in the layout: works like the addWidget method in a gridLayout"""
        assert widget not in self.widget_tile_couple['widget']

        tile = self.tile_map[from_row][from_column]
        self.widget_tile_couple['widget'].append(widget)
        self.widget_tile_couple['tile'].append(tile)

        # if the widget is on more than 1 tile, the tiles must be merged
        if row_span > 1 or column_span > 1:
            tiles_to_merge = [
                (from_row + row, from_column + column)
                for row in range(row_span)
                for column in range(column_span)
            ]
            self.__merge_tiles(tile, from_row, from_column, row_span, column_span, tiles_to_merge[1:])

        widget.setMouseTracking(True)
        tile.add_widget(widget)

    def remove_widget(self, widget):
        """removes the given widget"""
        assert widget in self.widget_tile_couple['widget']

        index = self.widget_tile_couple['widget'].index(widget)
        tile = self.widget_tile_couple['tile'][index]

        from_row = tile.get_from_row()
        from_column = tile.get_from_column()
        row_span = tile.get_row_span()
        column_span = tile.get_column_span()
        tiles_to_split = [
            (from_row + row, from_column + column)
            for row in range(row_span)
            for column in range(column_span)
        ]

        widget.setMouseTracking(False)
        self.hard_split_tiles(from_row, from_column, tiles_to_split)
        self.widget_tile_couple['widget'].pop(index)
        self.widget_tile_couple['tile'].pop(index)

    def accept_drag_and_drop(self, value):
        """is the user allowed to drag and drop tiles ?"""
        self.drag_and_drop = value

    def accept_resizing(self, value):
        """is the user allowed to resize tiles ?"""
        self.resizable = value

    def set_cursor_idle(self, value):
        """the default cursor shape on the tiles"""
        self.cursor_idle = value

    def set_cursor_grab(self, value):
        """the cursor shape when the user can grab the tile"""
        self.cursor_grab = value

    def set_cursor_resize_horizontal(self, value):
        """the cursor shape when the user can resize the tile horizontally"""
        self.cursor_resize_horizontal = value

    def set_cursor_resize_vertical(self, value):
        """the cursor shape when the user can resize the tile vertically"""
        self.cursor_resize_vertical = value

    def row_count(self):
        """Returns the number of rows"""
        return self.row_number

    def column_count(self):
        """Returns the number of columns"""
        return self.column_number

    def tile_rect(self, row, column):
        """Returns the geometry of the tile at (row, column)"""
        return self.tile_map[row][column].rect()

    def row_minimum_height(self, row=None):
        """Returns the minimum height"""
        return self.vertical_span

    def column_minimum_width(self, column=None):
        """Returns the minimum width"""
        return self.horizontal_span

    def vertical_spacing(self):
        """Returns the vertical spacing between two tiles"""
        return self.verticalSpacing()

    def horizontal_spacing(self):
        """Returns the horizontal spacing between two tiles"""
        return self.horizontalSpacing()

    def set_vertical_spacing(self, spacing):
        """Sets the vertical spacing between two tiles"""
        self.setVerticalSpacing(spacing)
        self.__set_grid_minimal_size()
        self.__update_all_tiles()

    def set_horizontal_spacing(self, spacing):
        """Sets the horizontal spacing between two tiles"""
        self.setHorizontalSpacing(spacing)
        self.__set_grid_minimal_size()
        self.__update_all_tiles()

    def resize_tile(self, direction, from_row, from_column, tile_number):
        """called when a tile is resized"""
        tile = self.tile_map[from_row][from_column]
        row_span = tile.get_row_span()
        column_span = tile.get_column_span()
        increase = True
        (dir_x, dir_y) = direction

        # increase tile size
        if tile_number*(dir_x + dir_y) > 0:
            tile_number, tiles_to_merge = self.__get_tiles_to_merge(direction, from_row, from_column, tile_number)
        # decrease tile size
        else:
            tile_number, tiles_to_merge = self.__get_tiles_to_split(direction, from_row, from_column, tile_number)
            increase = False

        column_span += tile_number*dir_x
        from_column += tile_number*(dir_x == -1)
        row_span += tile_number*dir_y
        from_row += tile_number*(dir_y == -1)

        if tiles_to_merge and increase:
            self.__merge_tiles(tile, from_row, from_column, row_span, column_span, tiles_to_merge)
        elif tiles_to_merge:
            self.__split_tiles(tile, from_row, from_column, row_span, column_span, tiles_to_merge)

    def hard_split_tiles(self, from_row, from_column, tiles_to_split):
        """splits the tiles and return the new one at (from_row, from_column)"""
        assert (from_row, from_column) in tiles_to_split
        tiles_to_recycle = set()

        for row, column in tiles_to_split:
            tiles_to_recycle.add(self.tile_map[row][column])
            self.__create_tile(row, column, update_tile_map=True)

        for tile in tiles_to_recycle:
            self.removeWidget(tile)

        tile = self.tile_map[from_row][from_column]
        self.addWidget(tile, from_row, from_column)
        return tile

    def is_empty(self, from_row, from_column, row_span, column_span):
        """checks if the given space is free from widgets"""
        if ((from_row + row_span > self.row_number) or (from_column + column_span > self.column_number) or
                (from_row < 0) or (from_column < 0)):
            return False
        else:
            return all([not self.tile_map[from_row + row][from_column + column].is_filled()
                        for row in range(row_span) for column in range(column_span)])

    def get_widget_to_drop(self):
        """gets the widget that the user is dragging"""
        widget = self.widget_to_drop
        self.widget_to_drop = None
        return widget

    def set_widget_to_drop(self, widget):
        """sets the widget that the user is dragging"""
        self.widget_to_drop = widget

    def __merge_tiles(self, tile, from_row, from_column, row_span, column_span, tiles_to_merge):
        """merges the tiles_to_merge with tile"""
        for row, column in tiles_to_merge:
            self.removeWidget(self.tile_map[row][column])
            self.tile_map[row][column] = tile

        self.removeWidget(tile)
        self.addWidget(tile, from_row, from_column, row_span, column_span)
        tile.update_size(from_row, from_column, row_span, column_span)

    def __split_tiles(self, tile, from_row, from_column, row_span, column_span, tiles_to_split):
        """splits the tiles_to_split from tile"""
        for row, column in tiles_to_split:
            self.__create_tile(row, column, update_tile_map=True)

        self.removeWidget(tile)
        self.addWidget(tile, from_row, from_column, row_span, column_span)
        tile.update_size(from_row, from_column, row_span, column_span)

    def __create_tile(self, from_row, from_column, row_span=1, column_span=1, update_tile_map=False):
        """creates a tile: a tile is basically a place holder that can contain a widget or not"""
        tile = Tile(
            self,
            from_row,
            from_column,
            row_span,
            column_span,
            self.vertical_span,
            self.horizontal_span
        )
        self.addWidget(tile, from_row, from_column, row_span, column_span)

        if update_tile_map:
            tile_positions = [
                (from_row + row, from_column + column)
                for row in range(row_span)
                for column in range(column_span)
            ]
            for (row, column) in tile_positions:
                self.tile_map[row][column] = tile

        return tile

    def __get_tiles_to_split(self, direction, from_row, from_column, tile_number):
        """finds the tiles to split when a tile is decreased"""
        tile = self.tile_map[from_row][from_column]
        row_span = tile.get_row_span()
        column_span = tile.get_column_span()
        (dir_x, dir_y) = direction

        tile_number = (
            tile_number
            if -tile_number*(dir_x + dir_y) < column_span*(dir_x != 0) + row_span*(dir_y != 0)
            else (1 - column_span)*dir_x + (1 - row_span)*dir_y
        )
        tiles_to_merge = [
            (
                from_row + row + (row_span - 2*row - 1)*(dir_y == 1),
                from_column + column + (column_span - 2*column - 1)*(dir_x == 1)
            )
            for row in range(-tile_number*dir_y + row_span*(dir_x != 0))
            for column in range(-tile_number*dir_x + column_span*(dir_y != 0))
        ]

        return tile_number, tiles_to_merge

    def __get_tiles_to_merge(self, direction, from_row, from_column, tile_number):
        """finds the tiles to merge when a tile is increased"""
        tile = self.tile_map[from_row][from_column]
        row_span = tile.get_row_span()
        column_span = tile.get_column_span()
        tile_number_available = 0
        tiles_to_merge = []
        (dir_x, dir_y) = direction

        tile_number = (
            max(tile_number, -from_column*(dir_x != 0) - from_row*(dir_y != 0))
            if (dir_x + dir_y == -1)
            else min(
                tile_number,
                ((self.column_number - from_column - column_span)*(dir_x != 0)
                 + (self.row_number - from_row - row_span)*(dir_y != 0))
            )
        )

        # west or east
        if dir_x != 0:
            for column in range(tile_number*dir_x):
                tiles_to_check = []
                column_delta = (column_span + column)*(dir_x == 1) + (-column - 1)*(dir_x == -1)
                for row in range(row_span):
                    tiles_to_check.append((from_row + row, from_column + column_delta))
                    if self.tile_map[from_row + row][from_column + column_delta].is_filled():
                        return tile_number_available, self.flatten_list(tiles_to_merge)
                tile_number_available += dir_x
                tiles_to_merge.append(tiles_to_check)

        # north or south
        else:
            for row in range(tile_number*dir_y):
                tiles_to_check = []
                row_delta = (row_span + row)*(dir_y == 1) + (-row - 1)*(dir_y == -1)
                for column in range(column_span):
                    tiles_to_check.append((from_row + row_delta, from_column + column))
                    if self.tile_map[from_row + row_delta][from_column + column].is_filled():
                        return tile_number_available, self.flatten_list(tiles_to_merge)
                tile_number_available += dir_y
                tiles_to_merge.append(tiles_to_check)

        return tile_number_available, self.flatten_list(tiles_to_merge)

    def __create_tile_map(self):
        """Creates a map to be able to locate each tile on the grid"""
        for i_row in range(self.row_number):
            self.tile_map.append([])
            for i_column in range(self.column_number):
                tile = self.__create_tile(i_row, i_column)
                self.tile_map[-1].append(tile)

    def __set_grid_minimal_size(self):
        """Sets the grid/tiles minimum size"""
        for i in range(self.row_number):
            self.setRowMinimumHeight(i, self.vertical_span)
        self.setRowStretch(self.row_number, 1)
        for i in range(self.column_number):
            self.setColumnMinimumWidth(i, self.horizontal_span)
        self.setColumnStretch(self.column_number, 1)

    def __update_all_tiles(self):
        """Forces the tiles to update their geometry"""
        for row in range(self.row_number):
            for column in range(self.column_number):
                self.tile_map[row][column].update_size(
                    vertical_span=self.vertical_span,
                    horizontal_span=self.horizontal_span
                )

    @staticmethod
    def flatten_list(to_flatten):
        """returns a 1D list given a 2D list"""
        return [item for a_list in to_flatten for item in a_list]
