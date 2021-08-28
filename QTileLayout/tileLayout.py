from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget
import uuid

from .tile import Tile


class QTileLayout(QtWidgets.QGridLayout):
    """
    A layout where the user can drag and drop widgets and resize them
    """

    tileResized = QtCore.pyqtSignal(QWidget, int, int, int, int)
    tileMoved = QtCore.pyqtSignal(QWidget, int, int, int, int)

    def __init__(self, rowNumber, columnNumber, verticalSpan, horizontalSpan, verticalSpacing=5, horizontalSpacing=5,
                 *args, **kwargs):
        super(QTileLayout, self).__init__(*args, **kwargs)

        # geometric parameters
        super().setVerticalSpacing(verticalSpacing)
        super().setHorizontalSpacing(horizontalSpacing)
        self.rowNumber = rowNumber
        self.columnNumber = columnNumber
        self.verticalSpan = verticalSpan
        self.horizontalSpan = horizontalSpan
        self.minVerticalSpan = verticalSpan
        self.minHorizontalSpan = horizontalSpan

        # logic parameters
        self.dragAndDrop = True
        self.resizable = True
        self.focus = False
        self.widgetToDrop = None
        self.tileMap = []
        self.widgetTileCouple = {'widget': [], 'tile': []}
        self.id = str(uuid.uuid4())
        self.linkedLayout = {self.id: self}

        # design parameters
        self.cursorIdle = QtCore.Qt.ArrowCursor
        self.cursorGrab = QtCore.Qt.OpenHandCursor
        self.cursorResizeHorizontal = QtCore.Qt.SizeHorCursor
        self.cursorResizeVertical = QtCore.Qt.SizeVerCursor
        self.colorMap = {
            'drag_and_drop': (211, 211, 211),
            'idle': (240, 240, 240),
            'resize': (211, 211, 211),
            'empty_check': (150, 150, 150),
        }

        self.setRowStretch(self.rowNumber, 1)
        self.setColumnStretch(self.columnNumber, 1)
        self.__createTileMap()

    def addWidget(self, widget: QWidget, fromRow: int, fromColumn: int, rowSpan: int = 1, columnSpan: int = 1):
        """adds a widget in the layout: works like the addWidget method in a gridLayout"""
        assert widget not in self.widgetTileCouple['widget']
        assert self.isAreaEmpty(fromRow, fromColumn, rowSpan, columnSpan)

        tile = self.tileMap[fromRow][fromColumn]
        self.widgetTileCouple['widget'].append(widget)
        self.widgetTileCouple['tile'].append(tile)

        # if the widget is on more than 1 tile, the tiles must be merged
        if rowSpan > 1 or columnSpan > 1:
            tilesToMerge = [
                (fromRow + row, fromColumn + column)
                for row in range(rowSpan)
                for column in range(columnSpan)
            ]
            self.__mergeTiles(tile, fromRow, fromColumn, rowSpan, columnSpan, tilesToMerge[1:])

        widget.setMouseTracking(True)
        tile.addWidget(widget)

    def removeWidget(self, widget: QWidget):
        """removes the given widget"""
        assert widget in self.widgetTileCouple['widget']

        index = self.widgetTileCouple['widget'].index(widget)
        tile = self.widgetTileCouple['tile'][index]

        fromRow = tile.getFromRow()
        fromColumn = tile.getFromColumn()
        rowSpan = tile.getRowSpan()
        columnSpan = tile.getColumnSpan()
        tilesToSplit = [
            (fromRow + row, fromColumn + column)
            for row in range(rowSpan)
            for column in range(columnSpan)
        ]

        widget.setMouseTracking(False)
        self.hardSplitTiles(fromRow, fromColumn, tilesToSplit)
        self.widgetTileCouple['widget'].pop(index)
        self.widgetTileCouple['tile'].pop(index)
        self.changeTilesColor('idle')

    def addRows(self, rowNumber: int):
        """adds rows at the bottom of the layout"""
        assert rowNumber > 0
        self.setRowStretch(self.rowNumber, 0)

        for row in range(self.rowNumber, self.rowNumber + rowNumber):
            self.tileMap.append([])
            for column in range(self.columnNumber):
                tile = self.__createTile(row, column)
                self.tileMap[-1].append(tile)

        self.rowNumber += rowNumber
        self.setRowStretch(self.rowNumber, 1)

    def addColumns(self, columnNumber: int):
        """adds columns at the right of the layout"""
        assert columnNumber > 0
        self.setColumnStretch(self.columnNumber, 0)

        for row in range(self.rowNumber):
            for column in range(self.columnNumber, self.columnNumber + columnNumber):
                tile = self.__createTile(row, column)
                self.tileMap[row].append(tile)

        self.columnNumber += columnNumber
        self.setColumnStretch(self.columnNumber, 1)

    def removeRows(self, rowNumber: int):
        """removes rows from the layout bottom"""
        assert self.isAreaEmpty(self.rowNumber - rowNumber, 0, rowNumber, self.columnNumber)

        for row in range(self.rowNumber - rowNumber, self.rowNumber):
            for column in range(self.columnNumber):
                super().removeWidget(self.tileMap[row][column])
                self.tileMap[row][column].deleteLater()
            self.setRowMinimumHeight(row, 0)
            self.setRowStretch(row, 0)

        self.rowNumber -= rowNumber
        self.tileMap = self.tileMap[:self.rowNumber]

    def removeColumns(self, columnNumber: int):
        """removes columns from the layout right"""
        assert self.isAreaEmpty(0, self.columnNumber - columnNumber, self.rowNumber, columnNumber)

        for column in range(self.columnNumber - columnNumber, self.columnNumber):
            for row in range(self.rowNumber):
                super().removeWidget(self.tileMap[row][column])
                self.tileMap[row][column].deleteLater()

            self.setColumnMinimumWidth(column, 0)
            self.setColumnStretch(column, 0)

        self.columnNumber -= columnNumber
        self.tileMap = [row[:self.columnNumber] for row in self.tileMap]

    def acceptDragAndDrop(self, value: bool):
        """is the user allowed to drag and drop tiles ?"""
        self.dragAndDrop = value

    def acceptResizing(self, value: bool):
        """is the user allowed to resize tiles ?"""
        self.resizable = value

    def setCursorIdle(self, value: QtCore.Qt.CursorShape):
        """the default cursor shape on the tiles"""
        self.cursorIdle = value

    def setCursorGrab(self, value: QtCore.Qt.CursorShape):
        """the cursor shape when the user can grab the tile"""
        self.cursorGrab = value

    def setCursorResizeHorizontal(self, value: QtCore.Qt.CursorShape):
        """the cursor shape when the user can resize the tile horizontally"""
        self.cursorResizeHorizontal = value

    def setCursorResizeVertical(self, value: QtCore.Qt.CursorShape):
        """the cursor shape when the user can resize the tile vertically"""
        self.cursorResizeVertical = value

    def setColorIdle(self, color: tuple):
        """the default tile color"""
        self.colorMap['idle'] = color
        self.changeTilesColor('idle')

    def setColorResize(self, color: tuple):
        """the tile color during resizing"""
        self.colorMap['resize'] = color

    def setColorDragAndDrop(self, color: tuple):
        """the tile color during drag and drop"""
        self.colorMap['drag_and_drop'] = color

    def setColorEmptyCheck(self, color: tuple):
        """the tile color, if empty, during drag and drop"""
        self.colorMap['empty_check'] = color

    def rowCount(self) -> int:
        """Returns the number of rows"""
        return self.rowNumber

    def columnCount(self) -> int:
        """Returns the number of columns"""
        return self.columnNumber

    def tileRect(self, row: int, column: int) -> QRect:
        """Returns the geometry of the tile at (row, column)"""
        return self.tileMap[row][column].rect()

    def rowsMinimumHeight(self) -> int:
        """Returns the minimum height"""
        return self.minVerticalSpan

    def columnsMinimumWidth(self) -> int:
        """Returns the minimum width"""
        return self.minHorizontalSpan

    def setRowsMinimumHeight(self, height: int):
        """Sets the minimum tiles height"""
        self.minVerticalSpan = height
        if self.minVerticalSpan > self.verticalSpan:
            self.verticalSpan = self.minVerticalSpan
            self.__updateAllTiles()

    def setColumnsMinimumWidth(self, width: int):
        """Sets the minimum tiles width"""
        self.minHorizontalSpan = width
        if self.minHorizontalSpan > self.horizontalSpan:
            self.horizontalSpan = self.minHorizontalSpan
            self.__updateAllTiles()

    def setRowsHeight(self, height: int):
        """Sets the tiles height"""
        assert self.minVerticalSpan <= height
        self.verticalSpan = height
        self.__updateAllTiles()

    def setColumnsWidth(self, width: int):
        """Sets the tiles width"""
        assert self.minHorizontalSpan <= width
        self.horizontalSpan = width
        self.__updateAllTiles()

    def setVerticalSpacing(self, spacing: int):
        """Sets the vertical spacing between two tiles"""
        super().setVerticalSpacing(spacing)
        self.__updateAllTiles()

    def setHorizontalSpacing(self, spacing: int):
        """Sets the horizontal spacing between two tiles"""
        super().setHorizontalSpacing(spacing)
        self.__updateAllTiles()

    def activateFocus(self, focus: bool):
        """Activates or not the widget focus after drag & drop or resize"""
        self.focus = focus

    def widgetList(self) -> list:
        """Returns the widgets currently in the layout"""
        return self.widgetTileCouple['widget']

    def linkLayout(self, layout: QtWidgets.QLayout):
        """Links this layout with another one to allow drag and drop between them"""
        assert isinstance(layout, QTileLayout)
        assert layout.id not in self.linkedLayout
        assert self.id not in layout.linkedLayout
        self.linkedLayout[layout.id] = layout
        layout.linkedLayout[self.id] = self

    def unLinkLayout(self, layout: QtWidgets.QLayout):
        """Unlinks this layout with another one to forbid drag and drop between them"""
        assert isinstance(layout, QTileLayout)
        assert layout.id != self.id
        assert layout.id in self.linkedLayout
        assert self.id in layout.linkedLayout
        self.linkedLayout.pop(layout.id)
        layout.linkedLayout.pop(self.id)

    def highlightTiles(self, direction, fromRow, fromColumn, tileNumber):
        """highlights tiles that will be merged during resizing"""
        tile = self.tileMap[fromRow][fromColumn]
        tilesToMerge, increase, fromRow, fromColumn, rowSpan, columnSpan = self.__getTilesToBeResized(
            tile, direction, fromRow, fromColumn, tileNumber
        )

        if tilesToMerge:
            self.changeTilesColor('empty_check', (fromRow, fromColumn), (rowSpan, columnSpan))

    def resizeTile(self, direction, fromRow, fromColumn, tileNumber):
        """called when a tile is resized"""
        tile = self.tileMap[fromRow][fromColumn]
        tilesToMerge, increase, fromRow, fromColumn, rowSpan, columnSpan = self.__getTilesToBeResized(
            tile, direction, fromRow, fromColumn, tileNumber
        )

        if tilesToMerge:
            if increase:
                self.__mergeTiles(tile, fromRow, fromColumn, rowSpan, columnSpan, tilesToMerge)
            else:
                self.__splitTiles(tile, fromRow, fromColumn, rowSpan, columnSpan, tilesToMerge)
            index = self.widgetTileCouple['tile'].index(tile)
            widget = self.widgetTileCouple['widget'][index]
            self.tileResized.emit(widget, fromRow, fromColumn, rowSpan, columnSpan)

    def hardSplitTiles(self, fromRow, fromColumn, tilesToSplit):
        """splits the tiles and return the new one at (fromRow, fromColumn)"""
        assert (fromRow, fromColumn) in tilesToSplit
        tilesToRecycle = set()

        for row, column in tilesToSplit:
            tilesToRecycle.add(self.tileMap[row][column])
            self.__createTile(row, column, updateTileMap=True)

        for tile in tilesToRecycle:
            super().removeWidget(tile)
            tile.deleteLater()

        tile = self.tileMap[fromRow][fromColumn]
        super().addWidget(tile, fromRow, fromColumn)
        return tile

    def isAreaEmpty(self, fromRow, fromColumn, rowSpan, columnSpan, color=''):
        """checks if the given space is free from widgets"""
        if isinstance(color, str) and color in self.colorMap.keys():
            self.changeTilesColor(color)
        if ((fromRow + rowSpan > self.rowNumber) or (fromColumn + columnSpan > self.columnNumber) or
                (fromRow < 0) or (fromColumn < 0)):
            isEmpty = False
        else:
            isEmpty = all([not self.tileMap[fromRow + row][fromColumn + column].isFilled()
                           for row in range(rowSpan) for column in range(columnSpan)])
        if isEmpty and isinstance(color, str) and color in self.colorMap.keys():
            self.changeTilesColor('empty_check', (fromRow, fromColumn), (rowSpan, columnSpan))
        return isEmpty

    def getWidgetToDrop(self):
        """gets the widget that the user is dragging"""
        widget = self.widgetToDrop
        self.widgetToDrop = None
        return widget

    def setWidgetToDrop(self, widget):
        """sets the widget that the user is dragging"""
        self.widgetToDrop = widget

    def changeTilesColor(self, colorChoice, from_tile=(0, 0), to_tile=None):
        """changes the color of all tiles"""
        palette = QPalette()
        palette.setColor(QPalette.Background, QtGui.QColor(*self.colorMap[colorChoice]))
        palette_idle = QPalette()
        palette_idle.setColor(QPalette.Background, QtGui.QColor(*self.colorMap['idle']))
        if to_tile is None:
            to_tile = (self.rowNumber, self.columnNumber)
        for row in range(from_tile[0], from_tile[0] + to_tile[0]):
            for column in range(from_tile[1], from_tile[1] + to_tile[1]):
                if not self.tileMap[row][column].isFilled():
                    self.tileMap[row][column].changeColor(palette)
                else:
                    self.tileMap[row][column].changeColor(palette_idle)

    def updateGlobalSize(self, newSize: QtGui.QResizeEvent):
        """update the size of the layout"""
        verticalMargins = self.contentsMargins().top() + self.contentsMargins().bottom()
        verticalSpan = int(
            (newSize.size().height() - (self.rowNumber - 1) * self.verticalSpacing() - verticalMargins)
            // self.rowNumber
        )

        horizontalMargins = self.contentsMargins().left() + self.contentsMargins().right()
        horizontalSpan = int(
            (newSize.size().width() - (self.columnNumber - 1) * self.horizontalSpacing() - horizontalMargins)
            // self.columnNumber
        )

        self.verticalSpan = max(verticalSpan, self.minVerticalSpan)
        self.horizontalSpan = max(horizontalSpan, self.minHorizontalSpan)
        self.__updateAllTiles()

    def __mergeTiles(self, tile, fromRow, fromColumn, rowSpan, columnSpan, tilesToMerge):
        """merges the tilesToMerge with tile"""
        for row, column in tilesToMerge:
            super().removeWidget(self.tileMap[row][column])
            self.tileMap[row][column].deleteLater()
            self.tileMap[row][column] = tile

        super().removeWidget(tile)
        super().addWidget(tile, fromRow, fromColumn, rowSpan, columnSpan)
        tile.updateSize(fromRow, fromColumn, rowSpan, columnSpan)

    def __splitTiles(self, tile, fromRow, fromColumn, rowSpan, columnSpan, tilesToSplit):
        """splits the tilesToSplit from tile"""
        for row, column in tilesToSplit:
            self.__createTile(row, column, updateTileMap=True)

        super().removeWidget(tile)
        super().addWidget(tile, fromRow, fromColumn, rowSpan, columnSpan)
        tile.updateSize(fromRow, fromColumn, rowSpan, columnSpan)

    def __createTile(self, fromRow, fromColumn, rowSpan=1, columnSpan=1, updateTileMap=False):
        """creates a tile: a tile is basically a place holder that can contain a widget or not"""
        tile = Tile(
            self,
            fromRow,
            fromColumn,
            rowSpan,
            columnSpan,
            self.verticalSpan,
            self.horizontalSpan,
        )
        super().addWidget(tile, fromRow, fromColumn, rowSpan, columnSpan)

        if updateTileMap:
            tilePositions = [
                (fromRow + row, fromColumn + column)
                for row in range(rowSpan)
                for column in range(columnSpan)
            ]
            for (row, column) in tilePositions:
                self.tileMap[row][column] = tile

        return tile

    def __getTilesToBeResized(self, tile, direction, fromRow, fromColumn, tileNumber):
        """recovers the tiles that will be merged or split during resizing"""
        rowSpan = tile.getRowSpan()
        columnSpan = tile.getColumnSpan()
        increase = True
        (dirX, dirY) = direction

        # increase tile size
        if tileNumber * (dirX + dirY) > 0:
            tileNumber, tilesToMerge = self.__getTilesToMerge(direction, fromRow, fromColumn, tileNumber)
        # decrease tile size
        else:
            tileNumber, tilesToMerge = self.__getTilesToSplit(direction, fromRow, fromColumn, tileNumber)
            increase = False

        columnSpan += tileNumber * dirX
        fromColumn += tileNumber * (dirX == -1)
        rowSpan += tileNumber * dirY
        fromRow += tileNumber * (dirY == -1)

        return tilesToMerge, increase, fromRow, fromColumn, rowSpan, columnSpan

    def __getTilesToSplit(self, direction, fromRow, fromColumn, tileNumber):
        """finds the tiles to split when a tile is decreased"""
        tile = self.tileMap[fromRow][fromColumn]
        rowSpan = tile.getRowSpan()
        columnSpan = tile.getColumnSpan()
        (dirX, dirY) = direction

        tileNumber = (
            tileNumber
            if -tileNumber * (dirX + dirY) < columnSpan * (dirX != 0) + rowSpan * (dirY != 0)
            else (1 - columnSpan) * dirX + (1 - rowSpan) * dirY
        )
        tilesToMerge = [
            (
                fromRow + row + (rowSpan - 2 * row - 1) * (dirY == 1),
                fromColumn + column + (columnSpan - 2 * column - 1) * (dirX == 1)
            )
            for row in range(-tileNumber * dirY + rowSpan * (dirX != 0))
            for column in range(-tileNumber * dirX + columnSpan * (dirY != 0))
        ]

        return tileNumber, tilesToMerge

    def __getTilesToMerge(self, direction, fromRow, fromColumn, tileNumber):
        """finds the tiles to merge when a tile is increased"""
        tile = self.tileMap[fromRow][fromColumn]
        rowSpan = tile.getRowSpan()
        columnSpan = tile.getColumnSpan()
        tileNumberAvailable = 0
        tilesToMerge = []
        (dirX, dirY) = direction

        tileNumber = (
            max(tileNumber, -fromColumn * (dirX != 0) - fromRow * (dirY != 0))
            if (dirX + dirY == -1)
            else min(
                tileNumber,
                ((self.columnNumber - fromColumn - columnSpan) * (dirX != 0)
                 + (self.rowNumber - fromRow - rowSpan) * (dirY != 0))
            )
        )

        # west or east
        if dirX != 0:
            for column in range(tileNumber * dirX):
                tilesToCheck = []
                columnDelta = (columnSpan + column) * (dirX == 1) + (-column - 1) * (dirX == -1)
                for row in range(rowSpan):
                    tilesToCheck.append((fromRow + row, fromColumn + columnDelta))
                    if self.tileMap[fromRow + row][fromColumn + columnDelta].isFilled():
                        return tileNumberAvailable, self.__flattenList(tilesToMerge)
                tileNumberAvailable += dirX
                tilesToMerge.append(tilesToCheck)

        # north or south
        else:
            for row in range(tileNumber * dirY):
                tilesToCheck = []
                rowDelta = (rowSpan + row) * (dirY == 1) + (-row - 1) * (dirY == -1)
                for column in range(columnSpan):
                    tilesToCheck.append((fromRow + rowDelta, fromColumn + column))
                    if self.tileMap[fromRow + rowDelta][fromColumn + column].isFilled():
                        return tileNumberAvailable, self.__flattenList(tilesToMerge)
                tileNumberAvailable += dirY
                tilesToMerge.append(tilesToCheck)

        return tileNumberAvailable, self.__flattenList(tilesToMerge)

    def __createTileMap(self):
        """Creates a map to be able to locate each tile on the grid"""
        for row in range(self.rowNumber):
            self.tileMap.append([])
            for column in range(self.columnNumber):
                tile = self.__createTile(row, column)
                self.tileMap[-1].append(tile)

    def __updateAllTiles(self):
        """Forces the tiles to update their geometry"""
        for row in range(self.rowNumber):
            for column in range(self.columnNumber):
                self.tileMap[row][column].updateSize(
                    verticalSpan=self.verticalSpan,
                    horizontalSpan=self.horizontalSpan
                )

    @staticmethod
    def __flattenList(toFlatten):
        """returns a 1D list given a 2D list"""
        return [item for aList in toFlatten for item in aList]
