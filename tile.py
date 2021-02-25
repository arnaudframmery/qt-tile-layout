from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QVBoxLayout
import json


class Tile(QtWidgets.QWidget):

    def __init__(self, tile_layout, from_row, from_column, row_span, column_span, vertical_spacing, horizontal_spacing, *args, **kwargs):
        super(Tile, self).__init__(*args, **kwargs)
        self.tile_layout = tile_layout
        self.from_row = from_row
        self.from_column = from_column
        self.row_span = row_span
        self.column_span = column_span
        self.vertical_spacing = vertical_spacing
        self.horizontal_spacing = horizontal_spacing
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
        self.setFixedHeight(self.row_span * 100 + (self.row_span - 1) * self.vertical_spacing)
        self.setFixedWidth(self.column_span * 100 + (self.column_span - 1) * self.horizontal_spacing)

    def add_widget(self, widget):
        widget.setMouseTracking(True)
        self.layout.addWidget(widget)
        self.widget = widget
        self.filled = True

    def get_widget(self):
        return self.widget

    def get_row_span(self):
        return self.row_span

    def update_size(self, from_row=None, from_column=None, row_span=None, column_span=None):
        self.from_row = from_row if from_row is not None else self.from_row
        self.from_column = from_column if from_column is not None else self.from_column
        self.row_span = row_span if row_span is not None else self.row_span
        self.column_span = column_span if column_span is not None else self.column_span
        self.update_size_limit()

    def get_column_span(self):
        return self.column_span

    def is_filled(self):
        return self.filled

    def remove_widget(self):
        self.layout.removeWidget(self.widget)
        self.widget = None
        self.filled = False

    def split_tile(self):
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
        if self.lock is None:
            if event.pos().x() < self.resize_margin or event.pos().x() > self.width() - self.resize_margin:
                self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            elif event.pos().y() < self.resize_margin or event.pos().y() > self.height() - self.resize_margin:
                self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
            else:
                self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        elif self.lock == 'west':
            None
        elif self.lock == 'east':
            None
        elif self.lock == 'north':
            None
        elif self.lock == 'south':
            None

    def mouseReleaseEvent(self, event):
        x, y = event.pos().x(), event.pos().y()

        if self.lock == 'west':
            tile_number = int((x + (100 / 2)) // (100 + self.vertical_spacing))
            self.tile_layout.expand_tile(
                'west',
                self.from_row,
                self.from_column,
                tile_number
            )

        elif self.lock == 'east':
            tile_number = int((x - 100 * self.column_span + (100 / 2)) // (100 + self.vertical_spacing))
            self.tile_layout.expand_tile(
                'east',
                self.from_row,
                self.from_column,
                tile_number
            )

        elif self.lock == 'north':
            tile_number = int((y + (100 / 2)) // (100 + self.horizontal_spacing))
            self.tile_layout.expand_tile(
                'north',
                self.from_row,
                self.from_column,
                tile_number
            )

        elif self.lock == 'south':
            tile_number = int((y - 100 * self.row_span + (100 / 2)) // (100 + self.horizontal_spacing))
            self.tile_layout.expand_tile(
                'south',
                self.from_row,
                self.from_column,
                tile_number
            )

        self.lock = None

    def mousePressEvent(self, event):
        if event.pos().x() < self.resize_margin:
            self.lock = 'west'
        elif event.pos().x() > self.width() - self.resize_margin:
            self.lock = 'east'
        elif event.pos().y() < self.resize_margin:
            self.lock = 'north'
        elif event.pos().y() > self.height() - self.resize_margin:
            self.lock = 'south'
        elif event.button() == Qt.LeftButton and self.filled:

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
        if not self.filled:
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = json.loads(event.mimeData().text())
        dragged_tile = self.tile_layout.get_tile(data['from_row'], data['from_column'])

        self.add_widget(dragged_tile.get_widget())
        event.acceptProposedAction()
