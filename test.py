import random
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPalette, QFont

from tile_layout import TileLayout


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

        # create the tile layout
        self.tile_layout = TileLayout(
            row_number=row_number,
            column_number=column_number,
            vertical_span=100,
            horizontal_span=150,
            vertical_spacing=5,
            horizontal_spacing=5,
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

        # add widgets in the tile layout
        for i_row in range(row_number - 2):
            for i_column in range(column_number):
                self.tile_layout.addWidget(
                    widget=self.__spawnWidget(),
                    from_row=i_row,
                    from_column=i_column,
                )
        self.tile_layout.addWidget(
            widget=self.__spawnWidget(),
            from_row=row_number - 2,
            from_column=1,
            row_span=2,
            column_span=2
        )

        # remove a widget from the tile layout
        last_widget = self.__spawnWidget()
        self.tile_layout.addWidget(
            widget=last_widget,
            from_row=row_number - 1,
            from_column=0,
            row_span=1,
            column_span=1
        )
        self.tile_layout.removeWidget(last_widget)

        # return the number of rows
        print(f'Row number: {self.tile_layout.rowCount()}')
        # return the number of columns
        print(f'Column number: {self.tile_layout.columnCount()}')
        # return the geometry of a specific tile
        print(f'One tile geometry: {self.tile_layout.tileRect(row_number - 1, 1)}')
        # return the tile height
        print(f'Tile height: {self.tile_layout.rowMinimumHeight()}')
        # return the tile width
        print(f'Tile width: {self.tile_layout.columnMinimumWidth()}')
        # return the vertical spacing between two tiles
        print(f'Layout vertical spacing: {self.tile_layout.verticalSpacing()}')
        # return the horizontal spacing between two tiles
        print(f'Layout horizontal spacing: {self.tile_layout.horizontalSpacing()}')

        # set the vertical spacing between two tiles
        self.tile_layout.setVerticalSpacing(5)
        # set the horizontal spacing between two tiles
        self.tile_layout.setHorizontalSpacing(5)
        # set the vertical span between two tiles
        self.tile_layout.setVerticalSpan(100)
        # set the horizontal span between two tiles
        self.tile_layout.setHorizontalSpan(150)

        # insert the layout in the window
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.tile_layout)
        self.setCentralWidget(self.central_widget)

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


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
