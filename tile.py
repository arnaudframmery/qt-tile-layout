from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QVBoxLayout
import json


class Tile(QtWidgets.QWidget):
    """
    The basic component of a tileLayout
    """

    def __init__(self, tile_layout, from_row, from_column, row_span, column_span, vertical_span=100,
                 horizontal_span=100, *args, **kwargs):
        super(Tile, self).__init__(*args, **kwargs)
        self.tile_layout = tile_layout
        self.from_row = from_row
        self.from_column = from_column
        self.row_span = row_span
        self.column_span = column_span
        self.vertical_span = vertical_span
        self.horizontal_span = horizontal_span
        self.resize_margin = 5

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

    def updateSize(self, from_row=None, from_column=None, row_span=None, column_span=None, vertical_span=None,
                   horizontal_span=None):
        """changes the tile size"""
        self.from_row = from_row if from_row is not None else self.from_row
        self.from_column = from_column if from_column is not None else self.from_column
        self.row_span = row_span if row_span is not None else self.row_span
        self.column_span = column_span if column_span is not None else self.column_span
        self.vertical_span = vertical_span if vertical_span is not None else self.vertical_span
        self.horizontal_span = horizontal_span if horizontal_span is not None else self.horizontal_span
        self.__updateSizeLimit()

    def addWidget(self, widget):
        """adds a widget in the tile"""
        self.layout.addWidget(widget)
        self.widget = widget
        self.filled = True

    def getFromRow(self):
        """returns the tile from row"""
        return self.from_row

    def getFromColumn(self):
        """returns the tile from column"""
        return self.from_column

    def getRowSpan(self):
        """returns the tile row span"""
        return self.row_span

    def getColumnSpan(self):
        """returns the tile column span"""
        return self.column_span

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
            self.setCursor(QtGui.QCursor(self.tile_layout.cursor_idle))

        elif self.lock is None:

            west_condition = 0 <= event.pos().x() < self.resize_margin
            east_condition = self.width() >= event.pos().x() > self.width() - self.resize_margin
            north_condition = 0 <= event.pos().y() < self.resize_margin
            south_condition = self.height() >= event.pos().y() > self.height() - self.resize_margin

            if (west_condition or east_condition) and self.tile_layout.resizable:
                self.setCursor(QtGui.QCursor(self.tile_layout.cursor_resize_horizontal))

            elif (north_condition or south_condition) and self.tile_layout.resizable:
                self.setCursor(QtGui.QCursor(self.tile_layout.cursor_resize_vertical))

            elif self.tile_layout.drag_and_drop and self.rect().contains(event.pos()):
                self.setCursor(QtGui.QCursor(self.tile_layout.cursor_grab))

            else:
                self.setCursor(QtGui.QCursor(self.tile_layout.cursor_idle))

    def mousePressEvent(self, event):
        """actions to do when the mouse button is pressed"""
        if event.button() != Qt.LeftButton:
            return None

        if event.pos().x() < self.resize_margin and self.tile_layout.resizable:
            self.lock = (-1, 0)  # 'west'
        elif event.pos().x() > self.width() - self.resize_margin and self.tile_layout.resizable:
            self.lock = (1, 0)  # 'east'
        elif event.pos().y() < self.resize_margin and self.tile_layout.resizable:
            self.lock = (0, -1)  # 'north'
        elif event.pos().y() > self.height() - self.resize_margin and self.tile_layout.resizable:
            self.lock = (0, 1)  # 'south'

        if self.lock is not None:
            self.tile_layout.changeTilesColor('resize')

        elif self.filled and self.tile_layout.drag_and_drop:
            drag = self.__prepareDropData(event)
            self.__dragAndDropProcess(drag)
            self.tile_layout.changeTilesColor('idle')

    def mouseReleaseEvent(self, event):
        """actions to do when the mouse button is released"""
        if self.lock is None:
            return None

        x, y = event.pos().x(), event.pos().y()
        (dir_x, dir_y) = self.lock

        span = self.horizontal_span * (dir_x != 0) + self.vertical_span * (dir_y != 0)
        tile_span = self.column_span * (dir_x != 0) + self.row_span * (dir_y != 0)
        spacing = self.tile_layout.verticalSpacing() * (dir_x != 0) + self.tile_layout.horizontalSpacing() * (
                    dir_y != 0)

        tile_number = int(
            (x * (dir_x != 0) + y * (dir_y != 0) + (span / 2) - span * tile_span * ((dir_x + dir_y) == 1)) // (
                        span + spacing)
        )

        self.tile_layout.resizeTile(self.lock, self.from_row, self.from_column, tile_number)
        self.tile_layout.changeTilesColor('idle')
        self.lock = None

    def dragEnterEvent(self, event):
        """checks if a tile can be drop on this one"""
        if self.tile_layout.drag_and_drop and self.__isDropPossible(event):
            event.acceptProposedAction()

    def dropEvent(self, event):
        """actions to do when a tile is dropped on this one"""
        drop_data = json.loads(event.mimeData().text())
        widget = self.tile_layout.getWidgetToDrop()

        self.tile_layout.addWidget(
            widget,
            self.from_row - drop_data['row_offset'],
            self.from_column - drop_data['column_offset'],
            drop_data['row_span'],
            drop_data['column_span']
        )
        self.tile_layout.tileMoved.emit(
            widget,
            drop_data['from_row'],
            drop_data['from_column'],
            self.from_row - drop_data['row_offset'],
            self.from_column - drop_data['column_offset'],
        )

        event.acceptProposedAction()

    def __prepareDropData(self, event):
        """prepares data for the drag and drop process"""
        drag = QDrag(self)

        drop_data = QMimeData()
        data = {
            'from_row': self.from_row,
            'from_column': self.from_column,
            'row_span': self.row_span,
            'column_span': self.column_span,
            'row_offset': event.pos().y() // (self.vertical_span + self.tile_layout.verticalSpacing()),
            'column_offset': event.pos().x() // (self.horizontal_span + self.tile_layout.horizontalSpacing()),
        }
        data_to_text = json.dumps(data)
        drop_data.setText(data_to_text)
        drag_icon = self.widget.grab()

        drag.setPixmap(drag_icon)
        drag.setMimeData(drop_data)
        drag.setHotSpot(event.pos() - self.rect().topLeft())

        return drag

    def __dragAndDropProcess(self, drag):
        """manages the drag and drop process"""
        previous_row_span = self.row_span
        previous_column_span = self.column_span

        self.tile_layout.setWidgetToDrop(self.widget)
        self.tile_layout.removeWidget(self.widget)
        self.setVisible(False)
        self.tile_layout.changeTilesColor('drag_and_drop')

        if drag.exec_() != 2:
            self.__removeWidget()
            self.tile_layout.addWidget(
                self.tile_layout.getWidgetToDrop(),
                self.from_row,
                self.from_column,
                previous_row_span,
                previous_column_span
            )

        self.setVisible(True)

    def __isDropPossible(self, event):
        """checks if this tile can accept the drop"""
        drop_data = json.loads(event.mimeData().text())
        return self.tile_layout.isAreaEmpty(
            self.from_row - drop_data['row_offset'],
            self.from_column - drop_data['column_offset'],
            drop_data['row_span'],
            drop_data['column_span']
        )

    def __removeWidget(self):
        """removes the tile widget"""
        self.layout.removeWidget(self.widget)
        self.widget = None
        self.filled = False

    def __updateSizeLimit(self):
        """refreshs the tile size limit"""
        self.setFixedHeight(
            self.row_span * self.vertical_span + (self.row_span - 1) * self.tile_layout.verticalSpacing()
        )
        self.setFixedWidth(
            self.column_span * self.horizontal_span + (self.column_span - 1) * self.tile_layout.horizontalSpacing()
        )
