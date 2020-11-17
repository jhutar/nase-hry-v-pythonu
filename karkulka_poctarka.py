import pygame.image
import random
import uuid


TITLE = 'Počítání za jídlo'
WIDTH = 800
HEIGHT = 600

SIZE = 64
MAP = {
    (0, 0): {
        "image": ["dirt"],
        "direction": "right",
    },
    (0, 1): {
        "image": ["dirt"],
        "direction": "up",
    },
    (0, 2): {
        "image": ["dirt"],
        "direction": "up",
    },
    (1, 0): {
        "image": ["dirt"],
        "direction": "right",
    },
    (1, 1): {
        "image": ["dirt", "bush_big"],
        "direction": None,
    },
    (1, 2): {
        "image": ["dirt"],
        "direction": "left",
    },
    (2, 0): {
        "image": ["dirt"],
        "direction": "down",
    },
    (2, 1): {
        "image": ["dirt"],
        "direction": "down",
    },
    (2, 2): {
        "image": ["dirt"],
        "direction": "left",
    },
}


def coord_to_pos(coord):
    return coord[0] * SIZE, coord[1] * SIZE


class Hero(Actor):
    def __init__(self, image, coord, background):
        self.coord = coord   # current coordinates of the hero on the map
        self.background = background
        self.movement = None
        topleft = coord_to_pos(coord)
        super().__init__(image, topleft=topleft)
        self.journey()   # initiate hero's journey through the map

    def journey(self):
        if self.movement is not None and self.movement.running:
            self.movement.stop()
        coord = self.background.get_next_goal(self.coord)
        self.coord = coord
        topleft = coord_to_pos(coord)
        self.movement = animate(self, topleft=topleft, duration=1, tween='linear')
        self.movement.on_finished = self.journey

    def claim(self, coord):
        if self.movement.running:
            self.movement.stop()
        self.coord = coord
        topleft = coord_to_pos(coord)
        self.movement = animate(self, topleft=topleft, duration=1, tween='bounce_end')

    def update(self):
        for coord, tile in self.background.map_data.items():
            if self.colliderect(tile['actor']):
                tile['dirty'] = True


class Background():
    def __init__(self, map_data):
        self.map_data = map_data
        for coord, tile in self.map_data.items():
            topleft = coord_to_pos(coord)

            if len(tile['image']) == 1:
                tile['actor'] = Actor(tile['image'][0], topleft=topleft)
            elif len(tile['image']) > 1:
                name = uuid.uuid4()
                first = pygame.image.load('images/' + tile['image'][0] + '.png').convert_alpha()
                for additional_name in tile['image'][1:]:
                    additional = pygame.image.load('images/' + additional_name + '.png').convert_alpha()
                    first.blit(additional, (0,0))
                images.add(name, first)
                tile['actor'] = Actor(name, topleft=topleft)
            else:
                raise Exception(f"No image specified for {coord} tile")

            tile['dirty'] = True

    def get_next_goal(self, coord):
        """
        For given source coord using map tile's "direction" property
        calculate target coord.
        E.g. source = (0, 0) and directon on that tile = "right" makes
             it to return (1, 0)
        """
        if self.map_data[coord]['direction'] == "up":
            return coord[0], coord[1] - 1
        if self.map_data[coord]['direction'] == "right":
            return coord[0] + 1, coord[1]
        if self.map_data[coord]['direction'] == "down":
            return coord[0], coord[1] + 1
        if self.map_data[coord]['direction'] == "left":
            return coord[0] - 1, coord[1]

    def get_path_coords(self):
        """
        Return set of coords whose tiles have some direction (that means
        hero wanders through them and they can be used for placing treasures)
        """
        coords = set()
        for coord, tile in self.map_data.items():
            if tile['direction'] is not None:
                coords.add(coord)
        return coords

    def draw(self):
        for tile in self.map_data.values():
            if tile['dirty']:
                tile['actor'].draw()
                tile['dirty'] = False

    def update(self):
        pass


class PuzzleX():
    def __init__(self, status, area):
        self.status = status
        self.area = area
        self.a = random.randint(0, 9)
        self.b = random.randint(0, 9)
        self.points = self.a * self.b
        if self.a == 5 or self.b == 5:
            self.points = int(self.points / 2)
        if self.points == 0:
            self.points = 1
        self.answer = []

    def on_key_down(self, key, mod, unicode):
        if key == keys.BACKSPACE and len(self.answer) > 0:
            del(self.answer[-1])
            return

        if key == keys.RETURN or key == keys.KP_ENTER:
            if int(''.join(self.answer)) == self.a * self.b:
                self.status.puzzle_passed(self.points)
            else:
                self.status.puzzle_failed(self.points)

        try:
            answer = int(unicode)
        except Exception as e:
            return
        self.answer.append(unicode)

    def draw(self):
        screen.draw.filled_rect(self.area, "gray")
        pos = (self.area.left + 10, self.area.top + 10)
        screen.draw.text("Kolik je:", pos)
        pos = (self.area.left + 10, self.area.top + 40)
        screen.draw.text(f"{self.a} * {self.b} = {''.join(self.answer)}", pos)


class Status():
    score = 0
    treasures = {}
    frame = 0
    puzzle = None

    def __init__(self, background, hero):
        self.background = background
        self.hero = hero
        self.create_treasure()
        self.puzzle_area = Rect((200, 100), (200, 200))

    def create_treasure(self):
        possible_coords = self.background.get_path_coords()
        possible_coords -= set({self.hero.coord, self.background.get_next_goal(self.hero.coord)})
        coord = random.sample(possible_coords, 1)[0]
        topleft = coord_to_pos(coord)
        self.treasures[coord] = {
            'actor': Actor("repa", topleft=topleft),
        }

    def detect_colisions(self):
        for coord in list(self.treasures.keys()):
            if self.treasures[coord]['actor'].colliderect(self.hero):
                self.hero.claim(coord)
                del(self.treasures[coord])
                puzzle = random.choice(puzzles)
                self.puzzle = puzzle(self, self.puzzle_area)

    def on_key_down(self, key, mod, unicode):
        if self.puzzle is not None:
            self.puzzle.on_key_down(key, mod, unicode)

    def puzzle_area_clean(self):
        screen.draw.filled_rect(self.puzzle_area, "black")

    def puzzle_passed(self, points):
        self.puzzle = None
        self.score += points
        screen.draw.filled_rect(self.puzzle_area, "darkgreen")
        clock.schedule_unique(self.puzzle_area_clean, 2)

    def puzzle_failed(self, points):
        self.puzzle = None
        self.score -= points
        screen.draw.filled_rect(self.puzzle_area, "darkred")
        clock.schedule_unique(self.puzzle_area_clean, 2)

    def draw(self):
        for coord, treasure in self.treasures.items():
            treasure['actor'].draw()
        if self.puzzle is not None:
            self.puzzle.draw()
        rect = Rect((200, 0), (200, 100))
        screen.draw.filled_rect(rect, "black")
        screen.draw.text(f"SCORE: {self.score}", (200, 0))
        screen.draw.text(f"FRAME: {self.frame:.02f}", (200, 25))

    def update(self, dt):
        self.frame += dt
        if self.puzzle is None and not self.hero.movement.running:
            self.hero.journey()
            clock.schedule_unique(self.create_treasure, 1.0)


background = Background(MAP)
hero = Hero("karkulka.png", (0, 0), background)
enemy = Actor("vlk.png", (100, 100))
puzzles = [PuzzleX]
status = Status(background, hero)


def draw():
    background.draw()
    status.draw()
    hero.draw()
    enemy.draw()


def update(dt):
    background.update()
    hero.update()
    status.update(dt)
    status.detect_colisions()


def on_key_down(key, mod, unicode):
    if key == keys.ESCAPE or key == keys.Q:
        exit()
    status.on_key_down(key, mod, unicode)
