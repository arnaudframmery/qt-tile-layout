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
            vertical_spawn=100,
            horizontal_span=150,
        )

        # allows the user to drag and drop tiles or not
        self.tile_layout.accept_drag_and_drop(True)
        # allows the user to resize tiles or not
        self.tile_layout.accept_resizing(True)

        # sets the default cursor shape on the tiles
        self.tile_layout.set_cursor_idle(QtCore.Qt.ArrowCursor)
        # sets the cursor shape when the user can grab the tile
        self.tile_layout.set_cursor_grab(QtCore.Qt.OpenHandCursor)
        # sets the cursor shape when the user can resize the tile horizontally
        self.tile_layout.set_cursor_resize_horizontal(QtCore.Qt.SizeHorCursor)
        # sets the cursor shape when the user can resize the tile vertically
        self.tile_layout.set_cursor_resize_vertical(QtCore.Qt.SizeVerCursor)

        # add widgets in the tile layout
        for i_row in range(row_number - 2):
            for i_column in range(column_number):
                self.tile_layout.add_widget(
                    widget=self.__spawn_widget(),
                    from_row=i_row,
                    from_column=i_column,
                )
        self.tile_layout.add_widget(
            widget=self.__spawn_widget(),
            from_row=row_number - 2,
            from_column=1,
            row_span=2,
            column_span=2
        )

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.tile_layout)
        self.setCentralWidget(self.central_widget)

    def __spawn_widget(self):
        """spawns a little colored widget with text"""
        label = QtWidgets.QLabel(self)
        label.setText(random.choice(possible_text))
        label.setFont(self.font)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setAutoFillBackground(True)
        label.setPalette(self.__spawn_color())
        return label

    @staticmethod
    def __spawn_color():
        """spawns a random color"""
        palette = QPalette()
        palette.setColor(QPalette.Background, QtGui.QColor(*random.choice(possible_colors)))
        return palette


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
