# qt-tile-layout

![PyPI](https://img.shields.io/pypi/v/pyqt5-tile-layout)

A tile layout for PyQt where you can put any widget in a tile. The user is then able to drag and drop the tiles and resize them

![](https://github.com/arnaudframmery/qt-tile-layout/blob/main/showoff.gif?raw=true)

# Quick example

Just launch the ```test.py``` script to have a first look (be sure to have installed PyQt5 from the `requirements.txt` file).
You can have an overview of how to use the different methods in this script.  

Moreover, you can change the value of ```static_layout``` variable to ```False``` to experiment a tile layout where the tile sizes are dynamics with the parent widget size (like a classic layout)

If you are interested about drag and drop widgets between several QTileLayouts, check the ```testLink.py``` script.

# Create and use a tile layout

First, you have to install the PyPi package:

```shell script
pip install pyqt5-tile-layout
```

And import the QTileLayout:

```python
from QTileLayout import QTileLayout
```

Then, let's create a tile layout with 8 rows and 5 columns.  
We also give the vertical and horizontal spawn in pixel:

```python
layout = QTileLayout(
    rowNumber=8,
    columnNumber=5,
    verticalSpawn=100,
    horizontalSpan=150,
    verticalSpacing=5,
    horizontalSpacing=5,
)
```

We can now add a widget in a specific position: it's the same as the grid layout:

```python
layout.addWidget(
    widget=QtWidgets.QLabel('Hello world'),
    fromRow=3,
    fromColumn=2,
    rowSpan=1,
    columnSpan=2,
)
```

Finally, if you put your layout into a window, you will be able to drag and drop the above widget and resize its  

# Documentation

```QTileLayout(int fromRow, int fromColumn, int rowSpan, int columnSpan, int verticalSpacing, int horizontalSpacing)```

_Constructs a new tile layout_

##### Methods:

- ```acceptDragAndDrop(bool value)```

_Allows or not the drag and drop of tiles in the layout_  
&nbsp;
  
- ```acceptResizing(bool value)```

_Allows or not the resizing of tiles in the layout_  
&nbsp;

- ```activateFocus(bool focus)```

_Activates or not the widget focus after drag & drop or resize. This feature can lead to unexpected behaviours in some cases, please set focus on false if you notice any of them_  
&nbsp;

- ```addcolumns(int columnNumber)```

_Adds columns at the right of the layout_  
&nbsp;

- ```addRows(int rowNumber)```

_Adds rows at the bottom of the layout_  
&nbsp;

- ```addWidget(QWidget widget, int fromRow, int fromColumn, int rowSpan, int columnSpan)```

_Adds the given widget to the layout, spanning multiple rows/columns. The tile will start at fromRow, fromColumn spanning rowSpan rows and columnSpan columns_  
&nbsp;

- ```columnCount() -> int```

_Returns the number of column in the layout_  
&nbsp;

- ```columnsMinimumwidth() -> int```

_Returns the minimal tile width of span one_  
&nbsp;

- ```getId() -> str```

_Returns the layout id_  
&nbsp;

- ```horizontalSpacing() -> int```

_Returns the horizontal spacing between two tiles_  
&nbsp;

- ```linkLayout(QTileLayout layout)```

_Allows the drag and drop between several layouts (see testLink.py)_  
&nbsp;

- ```removecolumns(int columnNumber)```

_Removes columns at the right of the layout, raises an error if a widget is in the target area_  
&nbsp;

- ```removeRows(int rowNumber)```

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

- ```setColorEmptyCheck(tuple color)```

_Sets the RGB color of the tiles where the dragged tile fits during drag and drop_  
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

- ```unLinkLayout(QTileLayout layout)```

_Forbids the drag and drop between several layouts (see testLink.py)_  
&nbsp;

- ```verticalSpacing() -> int```

_Returns the vertical spacing between two tiles_  
&nbsp;

- ```widgetList() -> list```

_Returns the widgets that are currently in the layout_  
&nbsp;

##### Signals:

- ```tileMoved(QWidget widget, str fromLayoutId, str toLayoutId, int fromRow, int fromColumn, int toRow, int toColumn)```

_Emits when a tile is moved successfully. When the source layout is not the same than the destination one, the signal is emitted from the destination layout_  
&nbsp;

- ```tileResized(QWidget widget, int fromRow, int fromColumn, int rowSpan, int columnSpan)```

_Emits when a tile is resized successfully_  
&nbsp;

# Last word

Feel free to use this layout and to notice me if there are some bugs or useful features to add