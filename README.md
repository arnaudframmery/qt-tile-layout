# qt-tile-layout

A tile layout for PyQt

![](showoff.gif)

# Quick example

Just launch the ```test.py``` script to have a first look (be sure to have installed PyQt5)

# Create and use a tile layout

First of all, the import statement

```python
from tile_layout import TileLayout
```

Then, let's create a tile layout with 8 rows and 5 columns.  
We also give the vertical and horizontal spawn in pixel

```python
layout = TileLayout(
    row_number=8,
    column_number=5,
    vertical_spawn=100,
    horizontal_span=150,
)
```

We can now add a widget in a specific position: it's the same as the grid layout

```python
layout.add_widget(
    widget=QtWidgets.QLabel('Hello world'),
    from_row=3,
    from_column=4,
    row_span=1,
    column_span=2
)
```

Finally, if you put your layout into a window, you will be able to drag and drop the above widget and resize its  

# Documentation

### TileLayout(int from_row, int from_column, int row_span, int column_span)

_Constructs a new tile layout._

##### Methods:

- accept_drag_and_drop(bool value)

_Allows or not the drag and drop of tiles in the layout_

- accept_resizing(bool value)

_Allows or not the resizing of tiles in the layout_

- add_widget(QWidget widget, int from_row, int from_column, int row_span, int column_span)

_Adds the given widget to the layout, spanning multiple rows/columns. The tile will start at fromRow, fromColumn spanning rowSpan rows and columnSpan columns_

- set_cursor_grab(QtCore.Qt.CursorShape value)

_Changes the cursor shape when it is possible to drag a tile_

- set_cursor_idle(QtCore.Qt.CursorShape value)

_Changes the cursor shape when it is over a tile_

- set_cursor_resize_horizontal(QtCore.Qt.CursorShape value)

_Changes the cursor shape when it is possible to resize a tile horizontally_

- set_cursor_resize_vertical(QtCore.Qt.CursorShape value)

_Changes the cursor shape when it is possible to resize a tile vertically_  

# Last word

Feel free to use this layout and to notice me if there are some bugs or useful features to add