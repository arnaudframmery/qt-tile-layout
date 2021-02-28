from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QVBoxLayout
import json


class Tile(QtWidgets.QWidget):
    """
    The basic component of a tileLayout
    """

    def __init__(self, tile_layout, from_row, from_column, row_span, column_span, vertical_spacing, horizontal_spacing,
                 vertical_span=100, horizontal_span=100, *args, **kwargs):
        super(Tile, self).__init__(*args, **kwargs)
        self.tile_layout = tile_layout
        self.from_row = from_row
        self.from_column = from_column
        self.row_span = row_span
        self.column_span = column_span
        self.vertical_spacing = vertical_spacing
        self.horizontal_spacing = horizontal_spacing
        self.vertical_span = vertical_span
        self.horizontal_span = horizontal_span
        self.resize_margin = 5

        self.filled = False
        self.widget = None
        self.lock = None
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.update_size_limit()
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setLayout(self.layout)

    def update_size_limit(self):
        """refreshs the tile size limit"""
        self.setFixedHeight(self.row_span * self.vertical_span + (self.row_span - 1) * self.vertical_spacing)
        self.setFixedWidth(self.column_span * self.horizontal_span + (self.column_span - 1) * self.horizontal_spacing)

    def update_size(self, from_row=None, from_column=None, row_span=None, column_span=None):
        """changes the tile size"""
        self.from_row = from_row if from_row is not None else self.from_row
        self.from_column = from_column if from_column is not None else self.from_column
        self.row_span = row_span if row_span is not None else self.row_span
        self.column_span = column_span if column_span is not None else self.column_span
        self.update_size_limit()

    def add_widget(self, widget):
        """adds a widget in the tile"""
        widget.setMouseTracking(True)
        self.layout.addWidget(widget)
        self.widget = widget
        self.filled = True

    def get_widget(self):
        """returns the widget in the tile"""
        return self.widget

    def get_row_span(self):
        """returns the tile row span"""
        return self.row_span

    def get_column_span(self):
        """returns the tile column span"""
        return self.column_span

    def is_filled(self):
        """returns True if there is a widget in the tile, else False"""
        return self.filled

    def remove_widget(self):
        """removes the tile widget"""
        self.layout.removeWidget(self.widget)
        self.widget = None
        self.filled = False

    def split_tile(self):
        """splits the tile: therefore the row span and column span become 1"""
        tile_positions = [
            (self.from_row + row, self.from_column + column)
            for row in range(self.row_span)
            for column in range(self.column_span)
        ]
        for (row, column) in tile_positions[1:]:
            self.tile_layout.create_tile(row, column, update_tile_map=True)
        self.row_span = 1
        self.column_span = 1
        self.update_size_limit()

    def mouseMoveEvent(self, event):
        """actions to do when the mouse is moved"""
        if not self.filled:
            return None
        if self.lock is None:
            if (event.pos().x() < self.resize_margin or event.pos().x() > self.width() - self.resize_margin) and self.tile_layout.resizable:
                self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            elif (event.pos().y() < self.resize_margin or event.pos().y() > self.height() - self.resize_margin) and self.tile_layout.resizable:
                self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
            elif self.tile_layout.drag_and_drop:
                self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
            else:
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        elif self.lock == (-1, 0):
            None
        elif self.lock == (1, 0):
            None
        elif self.lock == (0, -1):
            None
        elif self.lock == (0, 1):
            None

    def mouseReleaseEvent(self, event):
        """actions to do when the mouse button is released"""
        if self.lock is None:
            return None

        x, y = event.pos().x(), event.pos().y()
        (dir_x, dir_y) = self.lock
        span = self.horizontal_span*(dir_x != 0) + self.vertical_span*(dir_y != 0)
        tile_span = self.column_span*(dir_x != 0) + self.row_span*(dir_y != 0)
        spacing = self.vertical_spacing*(dir_x != 0) + self.horizontal_spacing*(dir_y != 0)

        tile_number = int(
            (x*(dir_x != 0) + y*(dir_y != 0) + (span/2) - span*tile_span*((dir_x + dir_y) == 1))
            // (span + spacing)
        )

        self.tile_layout.resize_tile(self.lock, self.from_row, self.from_column, tile_number)
        self.lock = None

    def mousePressEvent(self, event):
        """actions to do when the mouse button is pressed"""
        if event.pos().x() < self.resize_margin and self.tile_layout.resizable:
            self.lock = (-1, 0)  # 'west'
        elif event.pos().x() > self.width() - self.resize_margin and self.tile_layout.resizable:
            self.lock = (1, 0)   # 'east'
        elif event.pos().y() < self.resize_margin and self.tile_layout.resizable:
            self.lock = (0, -1)  # 'north'
        elif event.pos().y() > self.height() - self.resize_margin and self.tile_layout.resizable:
            self.lock = (0, 1)   # 'south'
        elif event.button() == Qt.LeftButton and self.filled and self.tile_layout.drag_and_drop:

            drag = QDrag(self)
            mime_data = QMimeData()
            data = {
                'from_row': self.from_row,
                'from_column': self.from_column,
                'row_span': self.row_span,
                'column_span': self.column_span,
            }
            data_to_text = json.dumps(data)
            mime_data.setText(data_to_text)
            drag.setMimeData(mime_data)
            drag.setHotSpot(event.pos() - self.rect().topLeft())

            if drag.exec_() == 2:
                self.split_tile()
                self.remove_widget()

    def dragEnterEvent(self, event):
        """checks if a tile can be drop on this one"""
        if not self.filled and self.tile_layout.drag_and_drop:
            event.acceptProposedAction()

    def dropEvent(self, event):
        """actions to do when a tile is dropped on this one"""
        data = json.loads(event.mimeData().text())
        dragged_tile = self.tile_layout.get_tile(data['from_row'], data['from_column'])

        self.add_widget(dragged_tile.get_widget())
        event.acceptProposedAction()
