from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget

from .tile import Tile


class QTileLayout(QtWidgets.QGridLayout):
    """
    A layout where the user can drag and drop widgets and resize them
    """

    tileResized = QtCore.pyqtSignal(QWidget, int, int, int, int)
    tileMoved = QtCore.pyqtSignal(QWidget, int, int, int, int)

    def __init__(self, row_number, column_number, vertical_span, horizontal_span, vertical_spacing=5,
                 horizontal_spacing=5, *args, **kwargs):
        super(QTileLayout, self).__init__(*args, **kwargs)

        # geometric parameters
        super().setVerticalSpacing(vertical_spacing)
        super().setHorizontalSpacing(horizontal_spacing)
        self.row_number = row_number
        self.column_number = column_number
        self.vertical_span = vertical_span
        self.horizontal_span = horizontal_span
        self.min_vertical_span = vertical_span
        self.min_horizontal_span = horizontal_span

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
        self.color_map = {
            'drag_and_drop': (211, 211, 211),
            'idle': (240, 240, 240),
            'resize': (211, 211, 211),
        }

        self.setRowStretch(self.row_number, 1)
        self.setColumnStretch(self.column_number, 1)
        self.__createTileMap()

    def addWidget(self, widget: QWidget, from_row: int, from_column: int, row_span: int = 1, column_span: int = 1):
        """adds a widget in the layout: works like the addWidget method in a gridLayout"""
        assert widget not in self.widget_tile_couple['widget']
        assert self.isAreaEmpty(from_row, from_column, row_span, column_span)

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
            self.__mergeTiles(tile, from_row, from_column, row_span, column_span, tiles_to_merge[1:])

        widget.setMouseTracking(True)
        tile.addWidget(widget)

    def removeWidget(self, widget: QWidget):
        """removes the given widget"""
        assert widget in self.widget_tile_couple['widget']

        index = self.widget_tile_couple['widget'].index(widget)
        tile = self.widget_tile_couple['tile'][index]

        from_row = tile.getFromRow()
        from_column = tile.getFromColumn()
        row_span = tile.getRowSpan()
        column_span = tile.getColumnSpan()
        tiles_to_split = [
            (from_row + row, from_column + column)
            for row in range(row_span)
            for column in range(column_span)
        ]

        widget.setMouseTracking(False)
        self.hardSplitTiles(from_row, from_column, tiles_to_split)
        self.widget_tile_couple['widget'].pop(index)
        self.widget_tile_couple['tile'].pop(index)
        self.changeTilesColor('idle')

    def addRows(self, row_number: int):
        """adds rows at the bottom of the layout"""
        assert row_number > 0
        self.setRowStretch(self.row_number, 0)

        for i_row in range(self.row_number, self.row_number + row_number):
            self.tile_map.append([])
            for i_column in range(self.column_number):
                tile = self.__createTile(i_row, i_column)
                self.tile_map[-1].append(tile)

        self.row_number += row_number
        self.setRowStretch(self.row_number, 1)

    def addColumns(self, column_number: int):
        """adds columns at the right of the layout"""
        assert column_number > 0
        self.setColumnStretch(self.column_number, 0)

        for i_row in range(self.row_number):
            for i_column in range(self.column_number, self.column_number + column_number):
                tile = self.__createTile(i_row, i_column)
                self.tile_map[i_row].append(tile)

        self.column_number += column_number
        self.setColumnStretch(self.column_number, 1)

    def removeRows(self, row_number: int):
        """removes rows from the layout bottom"""
        assert self.isAreaEmpty(self.row_number - row_number, 0, row_number, self.column_number)

        for row in range(self.row_number - row_number, self.row_number):
            for column in range(self.column_number):
                super().removeWidget(self.tile_map[row][column])

            self.setRowMinimumHeight(row, 0)
            self.setRowStretch(row, 0)

        self.row_number -= row_number
        self.tile_map = self.tile_map[:self.row_number]

    def removeColumns(self, column_number: int):
        """removes columns from the layout right"""
        assert self.isAreaEmpty(0, self.column_number - column_number, self.row_number, column_number)

        for column in range(self.column_number - column_number, self.column_number):
            for row in range(self.row_number):
                super().removeWidget(self.tile_map[row][column])

            self.setColumnMinimumWidth(column, 0)
            self.setColumnStretch(column, 0)

        self.column_number -= column_number
        self.tile_map = [a_row[:self.column_number] for a_row in self.tile_map]

    def acceptDragAndDrop(self, value: bool):
        """is the user allowed to drag and drop tiles ?"""
        self.drag_and_drop = value

    def acceptResizing(self, value: bool):
        """is the user allowed to resize tiles ?"""
        self.resizable = value

    def setCursorIdle(self, value: QtCore.Qt.CursorShape):
        """the default cursor shape on the tiles"""
        self.cursor_idle = value

    def setCursorGrab(self, value: QtCore.Qt.CursorShape):
        """the cursor shape when the user can grab the tile"""
        self.cursor_grab = value

    def setCursorResizeHorizontal(self, value: QtCore.Qt.CursorShape):
        """the cursor shape when the user can resize the tile horizontally"""
        self.cursor_resize_horizontal = value

    def setCursorResizeVertical(self, value: QtCore.Qt.CursorShape):
        """the cursor shape when the user can resize the tile vertically"""
        self.cursor_resize_vertical = value

    def setColorIdle(self, color: tuple):
        """the default tile color"""
        self.color_map['idle'] = color
        self.changeTilesColor('idle')

    def setColorResize(self, color: tuple):
        """the tile color during resizing"""
        self.color_map['resize'] = color

    def setColorDragAndDrop(self, color: tuple):
        """the tile color during drag and drop"""
        self.color_map['drag_and_drop'] = color

    def rowCount(self) -> int:
        """Returns the number of rows"""
        return self.row_number

    def columnCount(self) -> int:
        """Returns the number of columns"""
        return self.column_number

    def tileRect(self, row: int, column: int) -> QRect:
        """Returns the geometry of the tile at (row, column)"""
        return self.tile_map[row][column].rect()

    def rowsMinimumHeight(self) -> int:
        """Returns the minimum height"""
        return self.min_vertical_span

    def columnsMinimumWidth(self) -> int:
        """Returns the minimum width"""
        return self.min_horizontal_span

    def setRowsMinimumHeight(self, height: int):
        """Sets the minimum tiles height"""
        self.min_vertical_span = height
        if self.min_vertical_span > self.vertical_span:
            self.vertical_span = self.min_vertical_span
            self.__updateAllTiles()

    def setColumnsMinimumWidth(self, width: int):
        """Sets the minimum tiles width"""
        self.min_horizontal_span = width
        if self.min_horizontal_span > self.horizontal_span:
            self.horizontal_span = self.min_horizontal_span
            self.__updateAllTiles()

    def setRowsHeight(self, height: int):
        """Sets the tiles height"""
        assert self.min_vertical_span <= height
        self.vertical_span = height
        self.__updateAllTiles()

    def setColumnsWidth(self, width: int):
        """Sets the tiles width"""
        assert self.min_horizontal_span <= width
        self.horizontal_span = width
        self.__updateAllTiles()

    def setVerticalSpacing(self, spacing: int):
        """Sets the vertical spacing between two tiles"""
        super().setVerticalSpacing(spacing)
        self.__updateAllTiles()

    def setHorizontalSpacing(self, spacing: int):
        """Sets the horizontal spacing between two tiles"""
        super().setHorizontalSpacing(spacing)
        self.__updateAllTiles()

    def widgetList(self) -> list:
        """Returns the widgets currently in the layout"""
        return self.widget_tile_couple['widget']

    def resizeTile(self, direction, from_row, from_column, tile_number):
        """called when a tile is resized"""
        tile = self.tile_map[from_row][from_column]
        row_span = tile.getRowSpan()
        column_span = tile.getColumnSpan()
        increase = True
        (dir_x, dir_y) = direction

        # increase tile size
        if tile_number*(dir_x + dir_y) > 0:
            tile_number, tiles_to_merge = self.__getTilesToMerge(direction, from_row, from_column, tile_number)
        # decrease tile size
        else:
            tile_number, tiles_to_merge = self.__getTilesToSplit(direction, from_row, from_column, tile_number)
            increase = False

        column_span += tile_number*dir_x
        from_column += tile_number*(dir_x == -1)
        row_span += tile_number*dir_y
        from_row += tile_number*(dir_y == -1)

        if tiles_to_merge:
            if increase:
                self.__mergeTiles(tile, from_row, from_column, row_span, column_span, tiles_to_merge)
            else:
                self.__splitTiles(tile, from_row, from_column, row_span, column_span, tiles_to_merge)
            index = self.widget_tile_couple['tile'].index(tile)
            widget = self.widget_tile_couple['widget'][index]
            self.tileResized.emit(widget, from_row, from_column, row_span, column_span)

    def hardSplitTiles(self, from_row, from_column, tiles_to_split):
        """splits the tiles and return the new one at (from_row, from_column)"""
        assert (from_row, from_column) in tiles_to_split
        tiles_to_recycle = set()

        for row, column in tiles_to_split:
            tiles_to_recycle.add(self.tile_map[row][column])
            self.__createTile(row, column, update_tile_map=True)

        for tile in tiles_to_recycle:
            super().removeWidget(tile)

        tile = self.tile_map[from_row][from_column]
        super().addWidget(tile, from_row, from_column)
        return tile

    def isAreaEmpty(self, from_row, from_column, row_span, column_span):
        """checks if the given space is free from widgets"""
        if ((from_row + row_span > self.row_number) or (from_column + column_span > self.column_number) or
                (from_row < 0) or (from_column < 0)):
            return False
        else:
            return all([not self.tile_map[from_row + row][from_column + column].isFilled()
                        for row in range(row_span) for column in range(column_span)])

    def getWidgetToDrop(self):
        """gets the widget that the user is dragging"""
        widget = self.widget_to_drop
        self.widget_to_drop = None
        return widget

    def setWidgetToDrop(self, widget):
        """sets the widget that the user is dragging"""
        self.widget_to_drop = widget

    def changeTilesColor(self, color_choice):
        """changes the color of all tiles"""
        palette = QPalette()
        palette.setColor(QPalette.Background, QtGui.QColor(*self.color_map[color_choice]))
        for row in range(self.row_number):
            for column in range(self.column_number):
                if not self.tile_map[row][column].isFilled():
                    self.tile_map[row][column].changeColor(palette)

    def updateGlobalSize(self, new_size: QtGui.QResizeEvent):
        """update the size of the layout"""
        vertical_margins = self.contentsMargins().top() + self.contentsMargins().bottom()
        vertical_span = int(
            (new_size.size().height() - (self.row_number - 1)*self.verticalSpacing() - vertical_margins)
            // self.row_number
        )

        horizontal_margins = self.contentsMargins().left() + self.contentsMargins().right()
        horizontal_span = int(
            (new_size.size().width() - (self.column_number - 1)*self.horizontalSpacing() - horizontal_margins)
            // self.column_number
        )

        self.vertical_span = max(vertical_span, self.min_vertical_span)
        self.horizontal_span = max(horizontal_span, self.min_horizontal_span)
        self.__updateAllTiles()

    def __mergeTiles(self, tile, from_row, from_column, row_span, column_span, tiles_to_merge):
        """merges the tiles_to_merge with tile"""
        for row, column in tiles_to_merge:
            super().removeWidget(self.tile_map[row][column])
            self.tile_map[row][column] = tile

        super().removeWidget(tile)
        super().addWidget(tile, from_row, from_column, row_span, column_span)
        tile.updateSize(from_row, from_column, row_span, column_span)

    def __splitTiles(self, tile, from_row, from_column, row_span, column_span, tiles_to_split):
        """splits the tiles_to_split from tile"""
        for row, column in tiles_to_split:
            self.__createTile(row, column, update_tile_map=True)

        super().removeWidget(tile)
        super().addWidget(tile, from_row, from_column, row_span, column_span)
        tile.updateSize(from_row, from_column, row_span, column_span)

    def __createTile(self, from_row, from_column, row_span=1, column_span=1, update_tile_map=False):
        """creates a tile: a tile is basically a place holder that can contain a widget or not"""
        tile = Tile(
            self,
            from_row,
            from_column,
            row_span,
            column_span,
            self.vertical_span,
            self.horizontal_span,
        )
        super().addWidget(tile, from_row, from_column, row_span, column_span)

        if update_tile_map:
            tile_positions = [
                (from_row + row, from_column + column)
                for row in range(row_span)
                for column in range(column_span)
            ]
            for (row, column) in tile_positions:
                self.tile_map[row][column] = tile

        return tile

    def __getTilesToSplit(self, direction, from_row, from_column, tile_number):
        """finds the tiles to split when a tile is decreased"""
        tile = self.tile_map[from_row][from_column]
        row_span = tile.getRowSpan()
        column_span = tile.getColumnSpan()
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

    def __getTilesToMerge(self, direction, from_row, from_column, tile_number):
        """finds the tiles to merge when a tile is increased"""
        tile = self.tile_map[from_row][from_column]
        row_span = tile.getRowSpan()
        column_span = tile.getColumnSpan()
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
                    if self.tile_map[from_row + row][from_column + column_delta].isFilled():
                        return tile_number_available, self.__flattenList(tiles_to_merge)
                tile_number_available += dir_x
                tiles_to_merge.append(tiles_to_check)

        # north or south
        else:
            for row in range(tile_number*dir_y):
                tiles_to_check = []
                row_delta = (row_span + row)*(dir_y == 1) + (-row - 1)*(dir_y == -1)
                for column in range(column_span):
                    tiles_to_check.append((from_row + row_delta, from_column + column))
                    if self.tile_map[from_row + row_delta][from_column + column].isFilled():
                        return tile_number_available, self.__flattenList(tiles_to_merge)
                tile_number_available += dir_y
                tiles_to_merge.append(tiles_to_check)

        return tile_number_available, self.__flattenList(tiles_to_merge)

    def __createTileMap(self):
        """Creates a map to be able to locate each tile on the grid"""
        for i_row in range(self.row_number):
            self.tile_map.append([])
            for i_column in range(self.column_number):
                tile = self.__createTile(i_row, i_column)
                self.tile_map[-1].append(tile)

    def __updateAllTiles(self):
        """Forces the tiles to update their geometry"""
        for row in range(self.row_number):
            for column in range(self.column_number):
                self.tile_map[row][column].updateSize(
                    vertical_span=self.vertical_span,
                    horizontal_span=self.horizontal_span
                )

    @staticmethod
    def __flattenList(to_flatten):
        """returns a 1D list given a 2D list"""
        return [item for a_list in to_flatten for item in a_list]
