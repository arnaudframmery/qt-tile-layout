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
            verticalSpan=vertical_span,
            horizontalSpan=horizontal_span,
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

        # link the layouts together
        self.tile_layout_1.linkLayout(self.tile_layout_2)

        # impossible to drop on the second layout if drag and drop is not allowed on it (to test with False)
        self.tile_layout_2.acceptDragAndDrop(True)

        # insert the layouts in the window
        self.central_widget = QtWidgets.QWidget()
        self.central_layout = QtWidgets.QHBoxLayout()
        self.central_widget.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(self.central_layout)
        self.left_widget = QtWidgets.QWidget()
        self.right_widget = QtWidgets.QWidget()
        self.central_layout.addWidget(self.left_widget)
        self.central_layout.addWidget(self.right_widget)
        self.left_widget.setLayout(self.tile_layout_1)
        self.right_widget.setLayout(self.tile_layout_2)

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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
