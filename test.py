from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPalette
import sys

from tile_layout import TileLayout


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.row_number = 6
        self.column_number = 4
        self.tile_layout = TileLayout(self.column_number, self.row_number)

        self.palette = QPalette()
        self.palette.setColor(QPalette.Background, QtGui.QColor(0, 225, 225))

        for i_row in range(self.row_number - 2):
            for i_column in range(self.column_number):
                self.tile_layout.add_widget(self.spawn_widget(), i_row, i_column, 1, 1)
        self.tile_layout.add_widget(self.spawn_widget(), self.row_number - 2, 1, 2, 2)

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.tile_layout)
        self.setCentralWidget(self.central_widget)

    def spawn_widget(self):
        label = QtWidgets.QLabel(self)
        label.setText(f'Label')
        label.setAutoFillBackground(True)
        label.setPalette(self.palette)
        return label


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
