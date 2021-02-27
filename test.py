from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPalette
import sys

from tile_layout import TileLayout


class MainWindow(QtWidgets.QMainWindow):
    """
    creates a window and spawns some widgets to be able to test the tile layout
    """

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.palette = QPalette()
        self.palette.setColor(QPalette.Background, QtGui.QColor(0, 225, 225))

        row_number = 6
        column_number = 4

        # create the tile layout
        self.tile_layout = TileLayout(
            row_number=row_number,
            column_number=column_number,
            vertical_spawn=100,
            horizontal_span=150,
        )

        # add widgets in the tile layout
        for i_row in range(row_number - 2):
            for i_column in range(column_number):
                self.tile_layout.add_widget(
                    widget=self.spawn_widget(),
                    from_row=i_row,
                    from_column=i_column,
                )
        self.tile_layout.add_widget(
            widget=self.spawn_widget(),
            from_row=row_number - 2,
            from_column=1,
            row_span=2,
            column_span=2
        )

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.tile_layout)
        self.setCentralWidget(self.central_widget)

    def spawn_widget(self):
        """spawns a little color widget"""
        label = QtWidgets.QLabel(self)
        label.setText(f'Label')
        label.setAutoFillBackground(True)
        label.setPalette(self.palette)
        return label


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
