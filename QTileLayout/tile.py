from json import JSONDecodeError
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QMimeData, QByteArray
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QVBoxLayout
import json


class Tile(QtWidgets.QWidget):
    """
    The basic component of a tileLayout
    """

    def __init__(self, tileLayout, fromRow, fromColumn, rowSpan, columnSpan, verticalSpan, horizontalSpan, *args,
                 **kwargs):
        super(Tile, self).__init__(*args, **kwargs)
        self.tileLayout = tileLayout
        self.fromRow = fromRow
        self.fromColumn = fromColumn
        self.rowSpan = rowSpan
        self.columnSpan = columnSpan
        self.verticalSpan = verticalSpan
        self.horizontalSpan = horizontalSpan
        self.resizeMargin = 5

        self.filled = False
        self.widget = None
        self.lock = None
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.__updateSizeLimit()
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setLayout(self.layout)

    def updateSize(self, fromRow=None, fromColumn=None, rowSpan=None, columnSpan=None, verticalSpan=None,
                   horizontalSpan=None):
        """changes the tile size"""
        self.fromRow = fromRow if fromRow is not None else self.fromRow
        self.fromColumn = fromColumn if fromColumn is not None else self.fromColumn
        self.rowSpan = rowSpan if rowSpan is not None else self.rowSpan
        self.columnSpan = columnSpan if columnSpan is not None else self.columnSpan
        self.verticalSpan = verticalSpan if verticalSpan is not None else self.verticalSpan
        self.horizontalSpan = horizontalSpan if horizontalSpan is not None else self.horizontalSpan
        self.__updateSizeLimit()

    def addWidget(self, widget):
        """adds a widget in the tile"""
        self.layout.addWidget(widget)
        self.widget = widget
        self.filled = True

    def getFromRow(self):
        """returns the tile from row"""
        return self.fromRow

    def getFromColumn(self):
        """returns the tile from column"""
        return self.fromColumn

    def getRowSpan(self):
        """returns the tile row span"""
        return self.rowSpan

    def getColumnSpan(self):
        """returns the tile column span"""
        return self.columnSpan

    def isFilled(self):
        """returns True if there is a widget in the tile, else False"""
        return self.filled

    def changeColor(self, color):
        """Changes the tile background color"""
        self.setAutoFillBackground(True)
        self.setPalette(color)

    def mouseMoveEvent(self, event):
        """actions to do when the mouse is moved"""
        if not self.filled:
            self.setCursor(QtGui.QCursor(self.tileLayout.cursorIdle))

        elif self.lock is None:

            westCondition = 0 <= event.pos().x() < self.resizeMargin
            eastCondition = self.width() >= event.pos().x() > self.width() - self.resizeMargin
            northCondition = 0 <= event.pos().y() < self.resizeMargin
            southCondition = self.height() >= event.pos().y() > self.height() - self.resizeMargin

            if (westCondition or eastCondition) and self.tileLayout.resizable:
                self.setCursor(QtGui.QCursor(self.tileLayout.cursorResizeHorizontal))

            elif (northCondition or southCondition) and self.tileLayout.resizable:
                self.setCursor(QtGui.QCursor(self.tileLayout.cursorResizeVertical))

            elif self.tileLayout.dragAndDrop and self.rect().contains(event.pos()):
                self.setCursor(QtGui.QCursor(self.tileLayout.cursorGrab))

            else:
                self.setCursor(QtGui.QCursor(self.tileLayout.cursorIdle))

    def mousePressEvent(self, event):
        """actions to do when the mouse button is pressed"""
        if event.button() != Qt.LeftButton:
            return None

        if event.pos().x() < self.resizeMargin and self.tileLayout.resizable:
            self.lock = (-1, 0)  # 'west'
        elif event.pos().x() > self.width() - self.resizeMargin and self.tileLayout.resizable:
            self.lock = (1, 0)  # 'east'
        elif event.pos().y() < self.resizeMargin and self.tileLayout.resizable:
            self.lock = (0, -1)  # 'north'
        elif event.pos().y() > self.height() - self.resizeMargin and self.tileLayout.resizable:
            self.lock = (0, 1)  # 'south'

        if self.lock is not None:
            self.tileLayout.changeTilesColor('resize')

        elif self.filled and self.tileLayout.dragAndDrop:
            drag = self.__prepareDropData(event)
            self.__dragAndDropProcess(drag)
            self.tileLayout.changeTilesColor('idle')

    def mouseReleaseEvent(self, event):
        """actions to do when the mouse button is released"""
        if self.lock is None:
            return None

        x, y = event.pos().x(), event.pos().y()
        (dirX, dirY) = self.lock

        span = self.horizontalSpan * (dirX != 0) + self.verticalSpan * (dirY != 0)
        tileSpan = self.columnSpan * (dirX != 0) + self.rowSpan * (dirY != 0)
        spacing = self.tileLayout.verticalSpacing() * (dirX != 0) + self.tileLayout.horizontalSpacing() * (
                    dirY != 0)

        tileNumber = int(
            (x * (dirX != 0) + y * (dirY != 0) + (span / 2) - span * tileSpan * ((dirX + dirY) == 1)) // (
                        span + spacing)
        )

        self.tileLayout.resizeTile(self.lock, self.fromRow, self.fromColumn, tileNumber)
        self.tileLayout.changeTilesColor('idle')
        self.lock = None

    def dragEnterEvent(self, event):
        """checks if a tile can be drop on this one"""
        if self.tileLayout.dragAndDrop and event.mimeData().hasFormat('TileData') and self.__isDropPossible(event):
            event.acceptProposedAction()

    def dropEvent(self, event):
        """actions to do when a tile is dropped on this one"""
        dropData = json.loads(event.mimeData().data('TileData').data())
        widget = self.tileLayout.getWidgetToDrop()

        self.tileLayout.addWidget(
            widget,
            self.fromRow - dropData['row_offset'],
            self.fromColumn - dropData['column_offset'],
            dropData['row_span'],
            dropData['column_span']
        )
        self.tileLayout.tileMoved.emit(
            widget,
            dropData['from_row'],
            dropData['from_column'],
            self.fromRow - dropData['row_offset'],
            self.fromColumn - dropData['column_offset'],
        )

        event.acceptProposedAction()

    def __prepareDropData(self, event):
        """prepares data for the drag and drop process"""
        drag = QDrag(self)

        dropData = QMimeData()
        data = {
            'id': self.tileLayout.id,
            'from_row': self.fromRow,
            'from_column': self.fromColumn,
            'row_span': self.rowSpan,
            'column_span': self.columnSpan,
            'row_offset': event.pos().y() // (self.verticalSpan + self.tileLayout.verticalSpacing()),
            'column_offset': event.pos().x() // (self.horizontalSpan + self.tileLayout.horizontalSpacing()),
        }
        dataToText = json.dumps(data)
        dropData.setData('TileData', QByteArray(dataToText.encode()))
        dragIcon = self.widget.grab()

        drag.setPixmap(dragIcon)
        drag.setMimeData(dropData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())

        return drag

    def __dragAndDropProcess(self, drag):
        """manages the drag and drop process"""
        previousRowSpan = self.rowSpan
        previousColumnSpan = self.columnSpan

        self.tileLayout.setWidgetToDrop(self.widget)
        self.tileLayout.removeWidget(self.widget)
        self.setVisible(False)
        self.tileLayout.changeTilesColor('drag_and_drop')

        if drag.exec_() != 2:
            self.__removeWidget()
            self.tileLayout.addWidget(
                self.tileLayout.getWidgetToDrop(),
                self.fromRow,
                self.fromColumn,
                previousRowSpan,
                previousColumnSpan
            )

        self.setVisible(True)

    def __isDropPossible(self, event):
        """checks if this tile can accept the drop"""
        try:
            dropData = json.loads(event.mimeData().data('TileData').data())
        except JSONDecodeError:
            return False

        if dropData['id'] != self.tileLayout.id:
            return False

        return self.tileLayout.isAreaEmpty(
            self.fromRow - dropData['row_offset'],
            self.fromColumn - dropData['column_offset'],
            dropData['row_span'],
            dropData['column_span'],
            color=True
        )

    def __removeWidget(self):
        """removes the tile widget"""
        self.layout.removeWidget(self.widget)
        self.widget = None
        self.filled = False

    def __updateSizeLimit(self):
        """refreshes the tile size limit"""
        self.setFixedHeight(
            self.rowSpan * self.verticalSpan + (self.rowSpan - 1) * self.tileLayout.verticalSpacing()
        )
        self.setFixedWidth(
            self.columnSpan * self.horizontalSpan + (self.columnSpan - 1) * self.tileLayout.horizontalSpacing()
        )
