import random
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPalette, QFont

from QTileLayout import QTileLayout
from test import Label, possible_text, possible_colors


class MainWindow(QtWidgets.QMainWindow):
    """
    creates a window and spawns some widgets in two tile layout which are linked together
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

        # create the tile layouts
        self.tile_layout_1 = QTileLayout(
            rowNumber=row_number,
            columnNumber=column_number,
            verticalSpan=vertical_span,
            horizontalSpan=horizontal_span,
            verticalSpacing=spacing,
            horizontalSpacing=spacing,
        )
        self.tile_layout_2 = QTileLayout(
            rowNumber=row_number,
            columnNumber=column_number,
            verticalSpan=vertical_span + 50,
            horizontalSpan=horizontal_span - 50,
            verticalSpacing=spacing,
            horizontalSpacing=spacing,
        )
        self.tile_layout_3 = QTileLayout(
            rowNumber=row_number,
            columnNumber=column_number,
            verticalSpan=vertical_span,
            horizontalSpan=horizontal_span - 50,
            verticalSpacing=spacing,
            horizontalSpacing=spacing,
        )

        # add widgets in the tile layouts
        for i_row in range(row_number - 2):
            for i_column in range(column_number):
                self.tile_layout_1.addWidget(
                    widget=self.__spawnWidget(),
                    fromRow=i_row,
                    fromColumn=i_column,
                )
                self.tile_layout_2.addWidget(
                    widget=self.__spawnWidget(),
                    fromRow=i_row,
                    fromColumn=i_column,
                )
                self.tile_layout_3.addWidget(
                    widget=self.__spawnWidget(),
                    fromRow=i_row,
                    fromColumn=i_column,
                )

        # link the layouts together
        self.tile_layout_1.linkLayout(self.tile_layout_2)
        self.tile_layout_1.linkLayout(self.tile_layout_3)

        # impossible to drop on the second layout if drag and drop is not allowed on it (to test with False)
        self.tile_layout_2.acceptDragAndDrop(True)

        # actions to do when a tile is moved
        self.tile_layout_1.tileMoved.connect(self.__tileHasBeenMoved)
        self.tile_layout_2.tileMoved.connect(self.__tileHasBeenMoved)
        self.tile_layout_3.tileMoved.connect(self.__tileHasBeenMoved)

        # insert the layouts in the window
        self.central_widget = QtWidgets.QWidget()
        self.central_layout = QtWidgets.QHBoxLayout()
        self.central_widget.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(self.central_layout)
        self.left_widget = QtWidgets.QWidget()
        self.middle_widget = QtWidgets.QWidget()
        self.right_widget = QtWidgets.QWidget()
        self.central_layout.addWidget(self.left_widget)
        self.central_layout.addWidget(self.middle_widget)
        self.central_layout.addWidget(self.right_widget)
        self.left_widget.setLayout(self.tile_layout_1)
        self.middle_widget.setLayout(self.tile_layout_2)
        self.right_widget.setLayout(self.tile_layout_3)

        self.setCentralWidget(self.central_widget)

    def __spawnWidget(self):
        """spawns a little colored widget with text"""
        label = Label(self)
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
    def __tileHasBeenMoved(widget, from_layout_id, to_layout_id, from_row, from_column, to_row, to_column):
        print(f'{widget} has been moved from position ({from_row}, {from_column}) in layout {from_layout_id} to ({to_row}, {to_column}) in layout {to_layout_id}')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
