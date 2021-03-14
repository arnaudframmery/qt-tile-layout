import random
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPalette, QFont

from QTileLayout import QTileLayout


possible_text = [
    'Hello',
    'Salut',
    'Hallo',
    'Hola',
    'Ciao',
    'Ola',
    'Hej',
    'Saluton',
    'Szia',
]

possible_colors = [
    (255, 153, 51),  # orange
    (153, 0, 153),   # purple
    (204, 204, 0),   # yellow
    (51, 102, 204),  # blue
    (0, 204, 102),   # green
    (153, 102, 51),  # brown
    (255, 51, 51),   # red
]


class MainWindow(QtWidgets.QMainWindow):
    """
    creates a window and spawns some widgets to be able to test the tile layout
    """

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.font = QFont('Latin', 15)
        self.font.setBold(True)

        row_number = 6
        column_number = 4
        vertical_span = 100
        horizontal_span = 150
        spacing = 5
        static_layout = True

        # create the tile layout
        self.tile_layout = QTileLayout(
            rowNumber=row_number,
            columnNumber=column_number,
            verticalSpan=vertical_span,
            horizontalSpan=horizontal_span,
            verticalSpacing=spacing,
            horizontalSpacing=spacing,
        )

        # allow the user to drag and drop tiles or not
        self.tile_layout.acceptDragAndDrop(True)
        # allow the user to resize tiles or not
        self.tile_layout.acceptResizing(True)

        # set the default cursor shape on the tiles
        self.tile_layout.setCursorIdle(QtCore.Qt.ArrowCursor)
        # set the cursor shape when the user can grab the tile
        self.tile_layout.setCursorGrab(QtCore.Qt.OpenHandCursor)
        # set the cursor shape when the user can resize the tile horizontally
        self.tile_layout.setCursorResizeHorizontal(QtCore.Qt.SizeHorCursor)
        # set the cursor shape when the user can resize the tile vertically
        self.tile_layout.setCursorResizeVertical(QtCore.Qt.SizeVerCursor)

        # set default tile color
        self.tile_layout.setColorIdle((240, 240, 240))
        # set tile color during resize
        self.tile_layout.setColorResize((211, 211, 211))
        # set tile color during drag and drop
        self.tile_layout.setColorDragAndDrop((211, 211, 211))

        # add widgets in the tile layout
        for i_row in range(row_number - 2):
            for i_column in range(column_number):
                self.tile_layout.addWidget(
                    widget=self.__spawnWidget(),
                    fromRow=i_row,
                    fromColumn=i_column,
                )
        self.tile_layout.addWidget(
            widget=self.__spawnWidget(),
            fromRow=row_number - 2,
            fromColumn=1,
            rowSpan=2,
            columnSpan=2
        )

        # remove a widget from the tile layout
        last_widget = self.__spawnWidget()
        self.tile_layout.addWidget(
            widget=last_widget,
            fromRow=row_number - 1,
            fromColumn=0,
            rowSpan=1,
            columnSpan=1
        )
        self.tile_layout.removeWidget(last_widget)

        # return the number of rows
        print(f'Row number: {self.tile_layout.rowCount()}')
        # return the number of columns
        print(f'Column number: {self.tile_layout.columnCount()}')
        # return the geometry of a specific tile
        print(f'One tile geometry: {self.tile_layout.tileRect(row_number - 1, 1)}')
        # return the tile height
        print(f'Tile height: {self.tile_layout.rowsMinimumHeight()}')
        # return the tile width
        print(f'Tile width: {self.tile_layout.columnsMinimumWidth()}')
        # return the vertical spacing between two tiles
        print(f'Layout vertical spacing: {self.tile_layout.verticalSpacing()}')
        # return the horizontal spacing between two tiles
        print(f'Layout horizontal spacing: {self.tile_layout.horizontalSpacing()}')
        # return the widgets currently in the layout
        print(f'Number of widget: {len(self.tile_layout.widgetList())}')

        # set the vertical spacing between two tiles
        self.tile_layout.setVerticalSpacing(5)
        # set the horizontal spacing between two tiles
        self.tile_layout.setHorizontalSpacing(5)
        # set the minimum tiles height
        self.tile_layout.setRowsMinimumHeight(100)
        # set the minimum tiles width
        self.tile_layout.setColumnsMinimumWidth(150)
        # set the tiles height
        self.tile_layout.setRowsHeight(100)
        # set the tiles width
        self.tile_layout.setColumnsWidth(150)

        # actions to do when a tile is resized
        self.tile_layout.tileResized.connect(self.__tileHasBeenResized)
        # actions to do when a tile is moved
        self.tile_layout.tileMoved.connect(self.__tileHasBeenMoved)

        # adds rows at the bottom of the layout
        self.tile_layout.addRows(1)
        # adds columns at the right of the layout
        self.tile_layout.addColumns(1)
        # removes rows from the layout bottom
        self.tile_layout.removeRows(1)
        # removes columns from the layout right
        self.tile_layout.removeColumns(1)

        # insert the layout in the window
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(self.tile_layout)

        if static_layout:
            self.setCentralWidget(self.central_widget)

        else:
            self.scroll = QtWidgets.QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setContentsMargins(0, 0, 0, 0)
            self.scroll.setWidget(self.central_widget)
            self.setCentralWidget(self.scroll)
            self.scroll.resizeEvent = self.__centralWidgetResize

            # if you are not in static layout mode, think to change the scrollArea minimum height and width if you
            # change tiles minimum height or width
            vertical_margins = self.tile_layout.contentsMargins().top() + self.tile_layout.contentsMargins().bottom()
            horizontal_margins = self.tile_layout.contentsMargins().left() + self.tile_layout.contentsMargins().right()
            self.scroll.setMinimumHeight(
                row_number * vertical_span + (row_number - 1) * spacing + vertical_margins + 2
            )
            self.scroll.setMinimumWidth(
                column_number * horizontal_span + (column_number - 1) * spacing + horizontal_margins + 2
            )

    def __spawnWidget(self):
        """spawns a little colored widget with text"""
        label = QtWidgets.QLabel(self)
        label.setText(random.choice(possible_text))
        label.setFont(self.font)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setAutoFillBackground(True)
        label.setPalette(self.__spawnColor())
        return label

    @staticmethod
    def __spawnColor():
        """spawns a random color"""
        palette = QPalette()
        palette.setColor(QPalette.Background, QtGui.QColor(*random.choice(possible_colors)))
        return palette

    @staticmethod
    def __tileHasBeenResized(widget, from_row, from_column, row_span, column_span):
        print(f'{widget} has been resized and is now at the position ({from_row}, {from_column}) '
              f'with a span of ({row_span}, {column_span})')

    @staticmethod
    def __tileHasBeenMoved(widget, from_row, from_column, to_row, to_column):
        print(f'{widget} has been moved from position ({from_row}, {from_column}) to ({to_row}, {to_column})')

    def __centralWidgetResize(self, a0):
        self.tile_layout.updateGlobalSize(a0)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
