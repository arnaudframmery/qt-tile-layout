from PyQt5 import QtWidgets

from tile import Tile


class TileLayout(QtWidgets.QGridLayout):

    def __init__(self, column_number, row_number, *args, **kwargs):
        super(TileLayout, self).__init__(*args, **kwargs)
        self.setSpacing(5)
        self.row_number = row_number
        self.column_number = column_number
        self.tile_map = []

        for i in range(self.row_number):
            self.setRowMinimumHeight(i, 100)
        self.setRowStretch(self.row_number, 1)
        for i in range(self.column_number):
            self.setColumnMinimumWidth(i, 100)
        self.setColumnStretch(self.column_number, 1)

        for i_row in range(self.row_number):
            self.tile_map.append([])
            for i_column in range(self.column_number):
                tile = self.create_tile(i_row, i_column)
                self.tile_map[-1].append(tile)

    def add_widget(self, widget, from_row, from_column, row_span=1, column_span=1):
        if row_span > 1 or column_span > 1:
            tile_positions = [
                (from_row + row, from_column + column)
                for row in range(row_span)
                for column in range(column_span)
            ]
            for (row, column) in tile_positions:
                self.delete_tile(row, column)
            tile = self.create_tile(from_row, from_column, row_span, column_span, update_tile_map=True)

        else:
            tile = self.tile_map[from_row][from_column]

        tile.add_widget(widget)

    def create_tile(self, from_row, from_column, row_span=1, column_span=1, update_tile_map=False):
        tile = Tile(self, from_row, from_column, row_span, column_span, self.verticalSpacing(), self.horizontalSpacing())
        self.addWidget(tile, from_row, from_column, row_span, column_span)

        if update_tile_map:
            tile_positions = [
                (from_row + row, from_column + column)
                for row in range(row_span)
                for column in range(column_span)
            ]
            for (row, column) in tile_positions:
                self.tile_map[row][column] = tile

        return tile

    def expand_tile(self, direction, from_row, from_column, tile_number):  # TODO: refacto
        tile = self.tile_map[from_row][from_column]
        row_span = tile.get_row_span()
        column_span = tile.get_column_span()
        tiles_to_merge = []
        increase = True

        if direction == 'west':
            if tile_number < 0:
                tile_number, tiles_to_merge = self.get_tile_number_available(
                    'west',
                    from_row,
                    from_column,
                    tile_number
                )
            elif tile_number > 0:
                increase = False
                tile_number = tile_number if tile_number < column_span else column_span - 1
                tiles_to_merge = [
                    (from_row + row, from_column + column)
                    for row in range(row_span)
                    for column in range(tile_number)
                ]
            column_span += -tile_number
            from_column += tile_number

        elif direction == 'east':
            if tile_number > 0:
                tile_number, tiles_to_merge = self.get_tile_number_available(
                    'east',
                    from_row,
                    from_column,
                    tile_number
                )
            elif tile_number < 0:
                increase = False
                tile_number = tile_number if -tile_number < column_span else -column_span + 1
                tiles_to_merge = [
                    (from_row + row, from_column + column_span - column - 1)
                    for row in range(row_span)
                    for column in range(-tile_number)
                ]
            column_span += tile_number

        elif direction == 'north':
            if tile_number < 0:
                tile_number, tiles_to_merge = self.get_tile_number_available(
                    'north',
                    from_row,
                    from_column,
                    tile_number
                )
            elif tile_number > 0:
                increase = False
                tile_number = tile_number if tile_number < row_span else row_span - 1
                tiles_to_merge = [
                    (from_row + row, from_column + column)
                    for row in range(tile_number)
                    for column in range(column_span)
                ]
            row_span += -tile_number
            from_row += tile_number

        elif direction == 'south':
            if tile_number > 0:
                tile_number, tiles_to_merge = self.get_tile_number_available(
                    'south',
                    from_row,
                    from_column,
                    tile_number
                )
            elif tile_number < 0:
                increase = False
                tile_number = tile_number if -tile_number < row_span else -row_span + 1
                tiles_to_merge = [
                    (from_row + row_span - row - 1, from_column + column)
                    for row in range(-tile_number)
                    for column in range(column_span)
                ]
            row_span += tile_number

        print(tiles_to_merge, increase)
        print(from_row, from_column, row_span, column_span)
        if tiles_to_merge and increase:
            self.merge_tiles(tile, from_row, from_column, row_span, column_span, tiles_to_merge)
        elif tiles_to_merge:
            self.split_tiles(tile, from_row, from_column, row_span, column_span, tiles_to_merge)

    def get_tile_number_available(self, direction, from_row, from_column, tile_number):  # TODO: refacto
        tile = self.tile_map[from_row][from_column]
        row_span = tile.get_row_span()
        column_span = tile.get_column_span()
        tile_number_available = 0
        tiles_to_merge = []

        if direction == 'west':
            tile_number = max(tile_number, -from_column)
            for column in range(-tile_number):
                tiles_to_check = []
                for row in range(row_span):
                    tiles_to_check.append((from_row + row, from_column - column - 1))
                    if self.tile_map[from_row + row][from_column - column - 1].is_filled():
                        return tile_number_available, self.flatten_list(tiles_to_merge)
                tile_number_available -= 1
                tiles_to_merge.append(tiles_to_check)

        elif direction == 'east':
            tile_number = min(tile_number, self.column_number - from_column - column_span)
            for column in range(tile_number):
                tiles_to_check = []
                for row in range(row_span):
                    tiles_to_check.append((from_row + row, from_column + column_span + column))
                    if self.tile_map[from_row + row][from_column + column_span + column].is_filled():
                        return tile_number_available, self.flatten_list(tiles_to_merge)
                tile_number_available += 1
                tiles_to_merge.append(tiles_to_check)

        elif direction == 'north':
            tile_number = max(tile_number, -from_row)
            for row in range(-tile_number):
                tiles_to_check = []
                for column in range(column_span):
                    tiles_to_check.append((from_row - row - 1, from_column + column))
                    if self.tile_map[from_row - row - 1][from_column + column].is_filled():
                        return tile_number_available, self.flatten_list(tiles_to_merge)
                tile_number_available -= 1
                tiles_to_merge.append(tiles_to_check)

        elif direction == 'south':
            tile_number = min(tile_number, self.row_number - from_row - row_span)
            for row in range(tile_number):
                tiles_to_check = []
                for column in range(column_span):
                    tiles_to_check.append((from_row + row_span + row, from_column + column))
                    if self.tile_map[from_row + row_span + row][from_column + column].is_filled():
                        return tile_number_available, self.flatten_list(tiles_to_merge)
                tile_number_available += 1
                tiles_to_merge.append(tiles_to_check)

        return tile_number_available, self.flatten_list(tiles_to_merge)

    def get_tile(self, row, column):
        return self.tile_map[row][column]

    def delete_tile(self, row, column):
        self.removeWidget(self.tile_map[row][column])

    def merge_tiles(self, tile, from_row, from_column, row_span, column_span, tiles_to_merge):
        for row, column in tiles_to_merge:
            self.delete_tile(row, column)
            self.tile_map[row][column] = tile

        self.removeWidget(tile)
        self.addWidget(tile, from_row, from_column, row_span, column_span)
        tile.update_size(from_row, from_column, row_span, column_span)

    def split_tiles(self, tile, from_row, from_column, row_span, column_span, tiles_to_split):
        for row, column in tiles_to_split:
            self.create_tile(row, column, update_tile_map=True)

        self.removeWidget(tile)
        self.addWidget(tile, from_row, from_column, row_span, column_span)
        tile.update_size(from_row, from_column, row_span, column_span)

    @staticmethod
    def flatten_list(to_flatten):
        return [item for a_list in to_flatten for item in a_list]
