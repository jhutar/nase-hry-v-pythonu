import os

TITLE = 'Map maker'
WIDTH = 1280
HEIGHT = 640
SIZE = 64


class Highlight():
    pos = (SIZE / 2, SIZE / 2)
    i = 0
    old_pos = (SIZE / 2, SIZE / 2)

    def erase(self):
        rect = Rect((self.old_pos[0] - 32, self.old_pos[1] - 32), (SIZE, SIZE))
        screen.draw.rect(rect, (0, 0, 0))

    def draw(self):
        rect = Rect((self.pos[0] - 32, self.pos[1] - 32), (SIZE, SIZE))
        screen.draw.rect(rect, (255, 255, 255))


tiles = []
highlight = Highlight()

tile_x = SIZE * 10 - SIZE / 2
tile_y = SIZE / 2

highlight.pos = (tile_x + SIZE, tile_y)
highlight.i = 0

for i in os.listdir('images/'):
    tile_x += SIZE
    if tile_x > WIDTH:
        tile_x = SIZE * 10 + SIZE / 2
        tile_y += SIZE
    if tile_y > HEIGHT:
        break
    print(i, (tile_x, tile_y))
    tiles.append(Actor(i, (tile_x, tile_y)))

ground = {}
for col in range(10):
    for row in range(10):
        ground[(col, row)] = Actor('dirt', (col * SIZE + SIZE / 2, row * SIZE + SIZE / 2))

def draw():
    highlight.erase()
    for tile in tiles:
        tile.draw()
    for tile in ground.values():
        tile.draw()
    highlight.draw()

def on_mouse_down(pos, button):
    # Check if we selected new tile
    for i in range(len(tiles)):
        if button == mouse.LEFT and tiles[i].collidepoint(pos):
            highlight.i = i
            highlight.old_pos = highlight.pos
            highlight.pos = tiles[i].pos

    # Check if we added to the map
    for coords in ground:
        if button == mouse.LEFT and ground[coords].collidepoint(pos):
            ground[coords].image = tiles[highlight.i].image

def on_key_down(key, mod, unicode):
    if key == keys.ESCAPE or key == keys.Q:
        exit()
