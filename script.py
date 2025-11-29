# # {
# #     "islands": [
# #         {
# #             "position": {"x": 400, "y": 300},
# #             "radius": 5,
# #             "type": 1,
# #             "validated": False
# #         }
# #     ],
# #     "barrels": [
# #         {
# #             "position": {"x": 200, "y": 150},
# #             "radius": 10,
# #             "collected": False
# #         }
# #     ],
# #     "your_ship": {
# #         "position": {"x": 100, "y": 100},
# #         "velocity": {"x": 2.5, "y": -1.2},
# #         "angle": 45
# #     },
# #     "sea_size": 1000,
# #     "data": "your_persistent_data_string"
# # }
import array
import math


#
# # vju: type1 east > entre l'ile et la bordure droite
# # vju: type2 south > entre l'ile et la bordure bas
# # vju: type3 west > entre l'ile et la bordure gauche
# # vju: type4 north > entre l'ile et la bordure haut
#

def get_island_target(island):
    x = island["position"]["x"]
    y = island["position"]["y"]
    radius = island["radius"]
    island_type = island["type"]

    if island_type == 1:
        return {"x": x + radius + 1, "y": y}
    elif island_type == 2:
        return {"x": x, "y": y + radius + 1}
    elif island_type == 3:
        return {"x": x - radius - 1, "y": y}
    elif island_type == 4:
        return {"x": x, "y": y - radius - 1}
    else:
        raise Exception(f"Invalid type {island_type}")


def get_coordinate_1(x, y, size):
    return x + (y * size)


def create_map(size: int, islands):
    map_data = array.array('b', [1] * size * size)

    for island in islands:
        x = island["position"]["x"]
        y = island["position"]["y"]
        radius = island["radius"]
        # vju: on construit les cases inaccessible
        for i in range(radius):
            for j in range(radius):
                check_x = x + i
                check_y = y + j
                coord = get_coordinate_1(check_x, check_y, size)
                if difference((x, y), (check_x, check_y)) >= radius:
                    map_data[coord] = 1
                else:
                    map_data[coord] = 0

    return map_data


def get_next_target(islands, ship_pos):
    closest_island = None
    min_distance = float('inf')

    for island in islands:
        if island["validated"]:
            continue
        distance = difference_obj(ship_pos, island["position"])
        if distance < min_distance:
            min_distance = distance
            closest_island = island

    if closest_island:
        return get_island_target(closest_island)
    raise Exception(f"What should we do?")


def make_move(game_state):
    your_ship = game_state['your_ship']
    islands = game_state['islands']
    barrels = game_state['barrels']
    sea_size = game_state['sea_size']
    data = game_state['data']

    ship_pos = your_ship["position"]
    map_access = create_map(sea_size, islands)
    next_target = get_next_target(islands, ship_pos)
    # TODO :
    # - déterminer la meilleur prochaine position par rapport à la courante, à la target et à la xième suivante
    # - améliorer le get_next_target
    # - prendre en compte les barrels
    # - passer de la data pour réduire les calculs initiaux

    # Calculate angle to target
    dx = next_target["x"] - ship_pos["x"]
    dy = next_target["y"] - ship_pos["y"]
    target_angle = math.degrees(math.atan2(dy, dx)) % 360

    # Calculate distance to target
    distance_to_target = difference_obj(ship_pos, next_target)

    # Calculate current speed
    current_speed = math.sqrt(your_ship['velocity']['x'] ** 2 + your_ship['velocity']['y'] ** 2)

    # Determine acceleration based on distance and current speed
    # Calculate optimal speed based on distance to target
    optimal_speed = min(distance_to_target / 10, 10)  # Scale speed with distance, max 10

    # Calculate acceleration to reach optimal speed
    speed_difference = optimal_speed - current_speed

    # Acceleration ranges from -100 to 100
    acceleration = max(-100, min(100, math.floor(speed_difference) * 20))  # Scale factor of 20 for responsiveness

    # If very close to target, strong deceleration
    # if distance_to_target < 10:
    #     acceleration = max(acceleration, -100)  # Allow full deceleration when very close

    # Check if direct path is blocked by checking multiple points along the path
    # path_clear = True
    # steps = 5  # Check 5 points along the path
    #
    # for i in range(1, steps + 1):
    #     ratio = i / steps
    #     check_x = int(ship_pos["x"] + (next_target["x"] - ship_pos["x"]) * ratio)
    #     check_y = int(ship_pos["y"] + (next_target["y"] - ship_pos["y"]) * ratio)
    #
    #     if 0 <= check_x < sea_size and 0 <= check_y < sea_size:
    #         if map_access[get_coordinate_1(check_x, check_y, sea_size)] == 0:  # 0 means invalid/obstacle
    #             path_clear = False
    #             break
    #     else:
    #         # Out of bounds
    #         path_clear = False
    #         break

    # If path is blocked, try to find a clear angle (simple obstacle avoidance)
    final_angle = target_angle
    # if not path_clear:
    #     # Try angles offset by 15 degrees, preferring smaller angles first
    #     for offset in [15, -15, 30, -30, 45, -45, 60, -60, 75, -75, 90, -90]:
    #         test_angle = (target_angle + offset) % 360
    #         # Check if this angle leads to valid positions
    #         angle_clear = True
    #
    #         # Check multiple points in this direction
    #         for i in range(1, 4):  # Check 3 points ahead
    #             test_distance = min(15 * i, distance_to_target // 2)
    #             test_dx = test_distance * math.cos(math.radians(test_angle))
    #             test_dy = test_distance * math.sin(math.radians(test_angle))
    #             test_x = int(ship_pos["x"] + test_dx)
    #             test_y = int(ship_pos["y"] + test_dy)
    #
    #             if not (0 <= test_x < sea_size and 0 <= test_y < sea_size):
    #                 angle_clear = False
    #                 break
    #
    #             if map_access["map"][get_map_coordinate_1(map_access, test_x, test_y)] == 0:  # Invalid position
    #                 angle_clear = False
    #                 break
    #
    #         if angle_clear:
    #             final_angle = test_angle
    #             break

    return {
        'acceleration': acceleration,
        'angle': final_angle,
    }


#
#
# # def compute_next_position(current_pos, velocity, angle):
# #     # Calculate current speed (magnitude of velocity vector)
# #     current_speed = math.sqrt(velocity['x'] ** 2 + velocity['y'] ** 2)
# #
# #     # Convert angle from degrees to radians
# #     angle_rad = math.radians(angle)
# #
# #     # Compute velocity components based on angle and speed
# #     vx = current_speed * math.cos(angle_rad)
# #     vy = current_speed * math.sin(angle_rad)
# #
# #     return {
# #         'x': current_pos['x'] + vx,
# #         'y': current_pos['y'] + vy
# #     }
#
def difference(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def difference_obj(p1, p2):
    return abs(p1["x"] - p2["x"]) + abs(p1["y"] - p2["y"])
#
#
# game_state = {
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
#
# make_move(game_state)
