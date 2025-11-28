# {
#     "islands": [
#         {
#             "position": {"x": 400, "y": 300},
#             "radius": 5,
#             "type": 1,
#             "validated": False
#         }
#     ],
#     "barrels": [
#         {
#             "position": {"x": 200, "y": 150},
#             "radius": 10,
#             "collected": False
#         }
#     ],
#     "your_ship": {
#         "position": {"x": 100, "y": 100},
#         "velocity": {"x": 2.5, "y": -1.2},
#         "angle": 45
#     },
#     "sea_size": 1000,
#     "data": "your_persistent_data_string"
# }
import array
from typing import Iterable


# vju: type1 east > entre l'ile et la bordure droite
# vju: type2 south > entre l'ile et la bordure bas
# vju: type3 west > entre l'ile et la bordure gauche
# vju: type4 north > entre l'ile et la bordure haut

class Island:
    def __init__(self, island):
        self.x = island["position"]["x"]
        self.y = island["position"]["y"]
        self.radius = island["radius"]
        self.type = island["type"]
        self.validated = island["validated"]

    def target(self) -> Point:
        if type == 1:
            return Point(self.x + self.radius + 1, self.y)
        elif type == 2:
            return Point(self.x, self.y + self.radius + 1)
        elif type == 3:
            return Point(self.x - self.radius - 1, self.y)
        elif type == 4:
            return Point(self.x, self.y - self.radius - 1)
        else:
            raise Exception(f"Invalid type {type}")

    def get_coordinate_1(self, size) -> int:
        return self.x + (self.y * size)


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class Map:
    def __init__(self, size: int, islands: Iterable[Island], barrels):
        self.size = size
        self.islands = islands
        self.barrels = barrels
        self.map = array.array('b', [1] * size * size)

        for isl in islands:
            self.map[isl.get_coordinate_1(self.size)] = 0
            # vju: on construit les cases inaccessible
            for i in range(isl.radius):
                for j in range(isl.radius):
                    if difference_obj(isl, Point(isl.x + i, isl.y + j)) >= isl.radius:
                        self.map[isl.get_coordinate_1(self.size)] = 1
                    else:
                        self.map[isl.get_coordinate_1(self.size)] = 0

    def get_next_target(self, ship: Point):
        for isl in self.islands:
            if isl.validated:
                continue
            return isl.target()
        raise Exception(f"What should we do?")

    def get_coordinate_1(self, x: int, y: int) -> int:
        return x + (y * self.size)


def make_move(game_state):
    your_ship = game_state['your_ship']
    temp_islands = game_state['islands']
    barrels = game_state['barrels']
    sea_size = game_state['sea_size']
    data = game_state['data']

    islands = []
    for island in temp_islands:
        islands.append(Island(island))
    ship_pos = Point(your_ship['position']['x'], your_ship['position']['y'])

    mymap = Map(sea_size, islands, barrels)
    next_target = mymap.get_next_target(ship_pos)

    # Compute next position based on current position, velocity magnitude, and angle
    # next_position = compute_next_position(your_ship['position'], your_ship['velocity'], your_ship['angle'])
    # next_pos = (next_position['x'], next_position['y'])

    # target = None
    # min_distance = -100
    #
    # for island in temp_islands:
    #     if island['validated']:
    #         continue
    #     island_pos = (island['position']['x'], island['position']['y'])
    #     # Calculate distance from ship center to island center
    #     distance = difference(ship_pos, island_pos)
    #     if distance < min_distance:
    #         min_distance = distance
    #         target = island
    #
    # if target is None:
    #     for barrel in barrels:
    #         if barrel['collected']:
    #             continue
    #         barrel_pos = (barrel['position']['x'], barrel['position']['y'])
    #         distance = difference(ship_pos, barrel_pos)
    #         if distance < min_distance:
    #             min_distance = distance
    #             target = barrel
    #
    # # If we found an island, we could steer towards it
    # # For now, just return the island info in data for debugging
    # island_info = ""
    # if target:
    #     island_info = f" | Closest island at ({target['position']['x']}, {target['position']['y']}), distance: {min_distance}"

    return {
        'acceleration': 0,
        'angle': 0,
        'data': ''
    }


def compute_next_position(current_pos, velocity, angle):
    """Compute next position using velocity magnitude and angle direction"""
    import math

    # Calculate current speed (magnitude of velocity vector)
    current_speed = math.sqrt(velocity['x'] ** 2 + velocity['y'] ** 2)

    # Convert angle from degrees to radians
    angle_rad = math.radians(angle)

    # Compute velocity components based on angle and speed
    vx = current_speed * math.cos(angle_rad)
    vy = current_speed * math.sin(angle_rad)

    return {
        'x': current_pos['x'] + vx,
        'y': current_pos['y'] + vy
    }


def difference(p1, p2) -> int:
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def difference_obj(p1, p2) -> int:
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)
