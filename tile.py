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

        self.__update_size_limit()
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setLayout(self.layout)

    def update_size(self, from_row=None, from_column=None, row_span=None, column_span=None):
        """changes the tile size"""
        self.from_row = from_row if from_row is not None else self.from_row
        self.from_column = from_column if from_column is not None else self.from_column
        self.row_span = row_span if row_span is not None else self.row_span
        self.column_span = column_span if column_span is not None else self.column_span
        self.__update_size_limit()

    def add_widget(self, widget):
        """adds a widget in the tile"""
        widget.setMouseTracking(True)
        self.layout.addWidget(widget)
        self.widget = widget
        self.filled = True

    def get_row_span(self):
        """returns the tile row span"""
        return self.row_span

    def get_column_span(self):
        """returns the tile column span"""
        return self.column_span

    def is_filled(self):
        """returns True if there is a widget in the tile, else False"""
        return self.filled

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
            self.lock = (1, 0)   # 'east'
        elif event.pos().y() < self.resize_margin and self.tile_layout.resizable:
            self.lock = (0, -1)  # 'north'
        elif event.pos().y() > self.height() - self.resize_margin and self.tile_layout.resizable:
            self.lock = (0, 1)   # 'south'

        elif self.filled and self.tile_layout.drag_and_drop:
            drag = self.__prepare_drop_data(event)
            self.__drag_and_drop_process(drag)

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
            (x*(dir_x != 0) + y*(dir_y != 0) + (span/2) - span*tile_span*((dir_x + dir_y) == 1)) // (span + spacing)
        )

        self.tile_layout.resize_tile(self.lock, self.from_row, self.from_column, tile_number)
        self.lock = None

    def dragEnterEvent(self, event):
        """checks if a tile can be drop on this one"""
        if self.tile_layout.drag_and_drop and self.__is_drop_possible(event):
            event.acceptProposedAction()

    def dropEvent(self, event):
        """actions to do when a tile is dropped on this one"""
        drop_data = json.loads(event.mimeData().text())

        tiles_to_merge = [
            (self.from_row + row - drop_data['row_offset'], self.from_column + column - drop_data['column_offset'])
            for row in range(drop_data['row_span'])
            for column in range(drop_data['column_span'])
        ]
        self.tile_layout.merge_tiles(
            self,
            self.from_row - drop_data['row_offset'],
            self.from_column - drop_data['column_offset'],
            drop_data['row_span'],
            drop_data['column_span'],
            tiles_to_merge
        )

        self.add_widget(self.tile_layout.get_widget_to_drop())
        event.acceptProposedAction()

    def __prepare_drop_data(self, event):
        """prepares data for the drag and drop process"""
        drag = QDrag(self)

        drop_data = QMimeData()
        data = {
            'from_row': self.from_row,
            'from_column': self.from_column,
            'row_span': self.row_span,
            'column_span': self.column_span,
            'row_offset': event.pos().y() // (self.vertical_span + self.vertical_spacing),
            'column_offset': event.pos().x() // (self.horizontal_span + self.horizontal_spacing),
        }
        data_to_text = json.dumps(data)
        drop_data.setText(data_to_text)
        drag_icon = self.widget.grab()

        drag.setPixmap(drag_icon)
        drag.setMimeData(drop_data)
        drag.setHotSpot(event.pos() - self.rect().topLeft())

        return drag

    def __drag_and_drop_process(self, drag):
        """manages the drag and drop process"""
        previous_row_span = self.row_span
        previous_column_span = self.column_span

        self.tile_layout.set_widget_to_drop(self.widget)
        tiles_to_split = [
            (self.from_row + row, self.from_column + column)
            for row in range(self.row_span)
            for column in range(self.column_span)
        ]

        new_tile = self.tile_layout.hard_split_tiles(self.from_row, self.from_column, tiles_to_split)
        self.setVisible(False)

        if drag.exec_() != 2:
            self.tile_layout.merge_tiles(
                new_tile, self.from_row, self.from_column, previous_row_span, previous_column_span, tiles_to_split[1:]
            )
            new_tile.add_widget(self.tile_layout.get_widget_to_drop())

        self.__remove_widget()
        self.setVisible(True)

    def __is_drop_possible(self, event):
        """checks if this tile can accept the drop"""
        drop_data = json.loads(event.mimeData().text())
        return self.tile_layout.is_empty(
            self.from_row - drop_data['row_offset'],
            self.from_column - drop_data['column_offset'],
            drop_data['row_span'],
            drop_data['column_span']
        )

    def __remove_widget(self):
        """removes the tile widget"""
        self.widget.setMouseTracking(True)
        self.layout.removeWidget(self.widget)
        self.widget = None
        self.filled = False

    def __update_size_limit(self):
        """refreshs the tile size limit"""
        self.setFixedHeight(self.row_span * self.vertical_span + (self.row_span - 1) * self.vertical_spacing)
        self.setFixedWidth(self.column_span * self.horizontal_span + (self.column_span - 1) * self.horizontal_spacing)
