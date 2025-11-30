import math


# (les barrels pris par les adversaires sont toujours collected: False)
def make_move(game_state):
    ship = game_state['your_ship']
    ship_pos = ship['position']
    ship_velocity = ship['velocity']
    current_data = game_state['data']

    print(current_data)
    # Parse current_data: split on ';' and parse second part as comma-separated integers
    exclude_barrels = []
    if (current_data is not None) and (current_data != ';') and (current_data != ''):
        data_parts = current_data.split(';')
        if data_parts[1] is not None:
            for dp in data_parts[1].split(','):
                if dp != '':
                    exclude_barrels.append(int(dp))
        if (data_parts[0] is not None) and (data_parts[0] != ''):
            pos = data_parts[0].split(':')
            target = {'x': int(pos[0]), 'y': int(pos[1])}
            distance_to_barrel = get_distance(ship_pos, target)
            collection_radius = 5
            if distance_to_barrel <= collection_radius:
                exclude_barrels.append(int(pos[2]))

    # Find all uncollected barrels first
    targets = []

    # Add uncollected barrels
    index = 0
    for barrel in game_state['barrels']:
        distance = get_distance(barrel['position'], ship_pos)
        if distance < 250 and (index not in exclude_barrels) and (not barrel['collected']):
            targets.append({
                'position': barrel['position'],
                'type': 'barrel',
                'distance': distance,
                'index': index,
            })
        index += 1

    # If no barrels left, go for islands
    if not targets:
        for island in game_state['islands']:
            if not island['validated']:
                island_pos = get_island_corrected_position(island)
                targets.append({
                    'position': island_pos,
                    'type': 'island',
                    'distance': get_distance(island_pos, ship_pos)
                })

    if not targets:
        return {
            'acceleration': 0,
            'angle': ship['angle']
        }

    # Find closest target
    closest_target = None
    min_distance = float('inf')

    for target in targets:
        if target['distance'] < min_distance:
            min_distance = target['distance']
            closest_target = target

    # If no valid target found, maintain course
    if closest_target is None:
        return {
            'acceleration': 0,
            'angle': ship['angle']
        }

    if min_distance == float('inf'):
        dx = closest_target['position']['x'] - ship_pos['x']
        dy = closest_target['position']['y'] - ship_pos['y']
        min_distance = math.sqrt(dx * dx + dy * dy)

    # Calculate angle to target with velocity prediction
    dx = closest_target['position']['x'] - ship_pos['x']
    dy = closest_target['position']['y'] - ship_pos['y']

    # Calculate current speed
    current_speed = math.sqrt(ship_velocity['x'] ** 2 + ship_velocity['y'] ** 2)

    margin = 10

    # For islands, add margin to avoid collision
    if closest_target['type'] == 'island':
        # Calculate the direction and add offset
        target_dist = math.sqrt(dx * dx + dy * dy)
        if target_dist > 0:
            # Add 30 pixel margin perpendicular to approach
            # Offset slightly to the side
            offset_angle = math.atan2(dy, dx) + math.pi / 2  # 90 degrees offset
            dx += margin * math.cos(offset_angle)
            dy += margin * math.sin(offset_angle)

    # Predict where we'll be in a few turns and aim accordingly
    if current_speed > 1:
        # Compensate for momentum - predict future position
        time_to_target = min_distance / max(current_speed, 0.1)
        lookahead = min(time_to_target * 0.3, 3)  # Look ahead 30% of travel time, max 3 turns
        predicted_x = ship_pos['x'] + ship_velocity['x'] * lookahead
        predicted_y = ship_pos['y'] + ship_velocity['y'] * lookahead
        dx = closest_target['position']['x'] - predicted_x
        dy = closest_target['position']['y'] - predicted_y

        # Re-apply island margin after prediction
        if closest_target['type'] == 'island':
            target_dist = math.sqrt(dx * dx + dy * dy)
            if target_dist > 0:
                offset_angle = math.atan2(dy, dx) + math.pi / 2
                dx += margin * math.cos(offset_angle)
                dy += margin * math.sin(offset_angle)

    target_angle = math.degrees(math.atan2(dx, -dy)) % 360

    # Calculate angle difference
    angle_diff = (target_angle - ship['angle']) % 360
    if angle_diff > 180:
        angle_diff -= 360

    # Determine acceleration based on distance and alignment
    is_aligned = abs(angle_diff) < 30  # Are we pointing roughly at target?
    print(str(is_aligned))

    if min_distance < 25:
        # Very close - slow down significantly
        if current_speed < 1.5 or is_aligned:
            acceleration = 30
        else:
            acceleration = -80
    elif min_distance < 60:
        # Medium distance - moderate speed, but only if aligned
        if not is_aligned:
            acceleration = -40  # Brake to turn better
        elif current_speed > 4:
            acceleration = -30
        else:
            acceleration = 40
    elif min_distance < 150:
        # Getting closer - speed up if aligned
        if is_aligned:
            acceleration = 95
        else:
            acceleration = 50
    else:
        acceleration = 100

    # Adaptive turning - turn faster when far, slower when close
    if min_distance < 40:
        max_turn = 45  # Tighter control when close
    else:
        max_turn = 75  # Faster turning when far

    if abs(angle_diff) > max_turn:
        new_angle = (ship['angle'] + max_turn * (1 if angle_diff > 0 else -1)) % 360
    else:
        new_angle = target_angle

    next_data = ""
    if closest_target['type'] == 'barrel':
        next_data += str(closest_target["position"]["x"])
        next_data += ':'
        next_data += str(closest_target["position"]["y"])
        next_data += ':'
        next_data += str(closest_target["index"])
    next_data += ";"
    for eb in exclude_barrels:
        next_data += str(eb) + ','

    return {
        'acceleration': acceleration,
        'angle': int(new_angle),
        'data': next_data,
    }


def get_island_corrected_position(island):
    radius = island['radius']
    if island['type'] == 1:
        return {
            'x': island['position']['x'] + radius + 1,
            'y': island['position']['y'],
        }
    elif island['type'] == 2:
        return {
            'x': island['position']['x'],
            'y': island['position']['y'] + radius + 1,
        }
    elif island['type'] == 3:
        return {
            'x': island['position']['x'] - radius - 1,
            'y': island['position']['y'],
        }
    elif island['type'] == 4:
        return {
            'x': island['position']['x'],
            'y': island['position']['y'] - radius - 1,
        }
    else:
        raise Exception('Unknown island type')


def get_distance(p1, p2):
    return math.sqrt((p1['x'] - p2['x']) ** 2 + (p1['y'] - p2['y']) ** 2)
