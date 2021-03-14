# qt-tile-layout

A tile layout for PyQt where you can put any widget in a tile. The user is then able to drag and drop the tiles and resize them !

![](showoff.gif)

# Quick example

Just launch the ```test.py``` script to have a first look (be sure to have installed PyQt5).
You can have an overview of how to use the different methods in this script.  

Moreover, you can change the value of ```static_layout``` variable to ```False``` to experiment a tile layout where the tile sizes are dynamics with the parent widget size (like a classic layout)

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
    vertical_spacing=5,
    horizontal_spacing=5,
)
```

We can now add a widget in a specific position: it's the same as the grid layout

```python
layout.addWidget(
    widget=QtWidgets.QLabel('Hello world'),
    from_row=3,
    from_column=2,
    row_span=1,
    column_span=2
)
```

Finally, if you put your layout into a window, you will be able to drag and drop the above widget and resize its  

# Documentation

```TileLayout(int from_row, int from_column, int row_span, int column_span)```

_Constructs a new tile layout_

##### Methods:

- ```acceptDragAndDrop(bool value)```

_Allows or not the drag and drop of tiles in the layout_  
&nbsp;
  
- ```acceptResizing(bool value)```

_Allows or not the resizing of tiles in the layout_  
&nbsp;

- ```addcolumns(int column_number)```

_Adds columns at the right of the layout_  
&nbsp;

- ```addRows(int row_number)```

_Adds rows at the bottom of the layout_  
&nbsp;

- ```addWidget(QWidget widget, int from_row, int from_column, int row_span, int column_span)```

_Adds the given widget to the layout, spanning multiple rows/columns. The tile will start at fromRow, fromColumn spanning rowSpan rows and columnSpan columns_  
&nbsp;

- ```columnCount() -> int```

_Returns the number of column in the layout_  
&nbsp;

- ```columnsMinimumwidth() -> int```

_Returns the minimal tile width of span one_  
&nbsp;

- ```horizontalSpacing() -> int```

_Returns the horizontal spacing between two tiles_  
&nbsp;

- ```removecolumns(int column_number)```

_Removes columns at the right of the layout, raises an error if a widget is in the target area_  
&nbsp;

- ```removeRows(int row_number)```

_Adds rows at the bottom of the layout, raises an error if a widget is in the target area_  
&nbsp;

- ```removeWidget(QWidget widget)```

_Removes the given widget from the layout_  
&nbsp;

- ```rowCount() -> int```

_Returns the number of row in the layout_  
&nbsp;

- ```rowsMinimumHeight() -> int```

_Returns the minimal tile height of span one_  
&nbsp;

- ```setColorDragAndDrop(tuple color)```

_Sets the RGB color of the tiles during drag and drop_  
&nbsp;

- ```setColorIdle(tuple color)```

_Sets the default RGB color of the tiles_  
&nbsp;

- ```setColorResize(tuple color)```

_Sets the RGB color of the tiles during resizing_  
&nbsp;

- ```setColumnsWidth(int width)```

_Sets the tiles width (in pixels) of span one_  
&nbsp;

- ```setColumnsMinimumWidth(int width)```

_Sets the minimum tiles width (in pixels) of span one_  
&nbsp;

- ```setCursorGrab(QtCore.Qt.CursorShape value)```

_Changes the cursor shape when it is possible to drag a tile_  
&nbsp;

- ```setCursorIdle(QtCore.Qt.CursorShape value)```

_Changes the cursor shape when it is over a tile_  
&nbsp;

- ```setCursorResizeHorizontal(QtCore.Qt.CursorShape value)```

_Changes the cursor shape when it is possible to resize a tile horizontally_  
&nbsp;

- ```setCursorResizeVertical(QtCore.Qt.CursorShape value)```

_Changes the cursor shape when it is possible to resize a tile vertically_  
&nbsp;

- ```setHorizontalSpacing(int spacing)```

_Changes the horizontal spacing between two tiles_  
&nbsp;

- ```setRowsHeight(int height)```

_Sets the tiles height (in pixels) of span one_  
&nbsp;

- ```setRowsMinimumHeight(int height)```

_Sets the minimum tiles height (in pixels) of span one_  
&nbsp;

- ```setVerticalSpacing(int spacing)```

_Changes the vertical spacing between two tiles_  
&nbsp;

- ```tileRect(int row, int column) -> QRect```

_Returns the geometry of the tile at (row, column)_  
&nbsp;

- ```verticalSpacing() -> int```

_Returns the vertical spacing between two tiles_  
&nbsp;

- ```widgetList() -> list```

_Returns the widgets that are currently in the layout_  
&nbsp;

##### Signals:

- ```tileMoved(QWidget widget, int from_row, int from_column, int to_row, int to_column)```

_Emits when a tile is moved successfully_  
&nbsp;

- ```tileResized(QWidget widget, int from_row, int from_column, int row_span, int column_span)```

_Emits when a tile is resized successfully_  
&nbsp;

# Last word

Feel free to use this layout and to notice me if there are some bugs or useful features to add