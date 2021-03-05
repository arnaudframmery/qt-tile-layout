# qt-tile-layout

A tile layout for PyQt

![](showoff.gif)

# Create and use a tile layout

Let's create a tile layout with 8 rows and 5 columns.  
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

