import math

def make_move(game_state):
    ship = game_state['your_ship']
    ship_pos = ship['position']
    ship_velocity = ship['velocity']
    
    # Find all uncollected barrels first
    targets = []
    
    # Add uncollected barrels
    for barrel in game_state['barrels']:
        if not barrel['collected']:
            targets.append({
                'position': barrel['position'],
                'type': 'barrel'
            })
    
    # If no barrels left, go for islands
    if not targets:
        for island in game_state['islands']:
            if not island['validated']:
                targets.append({
                    'position': island['position'],
                    'type': 'island'
                })
    
    if not targets:
        return {
            'acceleration': 0,
            'angle': ship['angle'],
            'data': ''
        }
    
    # Find closest target
    closest_target = None
    min_distance = float('inf')
    
    for target in targets:
        dx = target['position']['x'] - ship_pos['x']
        dy = target['position']['y'] - ship_pos['y']
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < min_distance:
            min_distance = distance
            closest_target = target
    
    # If no valid target found, maintain course
    if closest_target is None:
        return {
            'acceleration': 0,
            'angle': ship['angle'],
            'data': ''
        }
    
    # Calculate angle to target with velocity prediction
    dx = closest_target['position']['x'] - ship_pos['x']
    dy = closest_target['position']['y'] - ship_pos['y']
    
    # Calculate current speed
    current_speed = math.sqrt(ship_velocity['x']**2 + ship_velocity['y']**2)
    
    # For islands, add margin to avoid collision
    if closest_target['type'] == 'island':
        # Calculate the direction and add offset
        target_dist = math.sqrt(dx * dx + dy * dy)
        if target_dist > 0:
            # Add 30 pixel margin perpendicular to approach
            margin = 30
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
                margin = 30
                offset_angle = math.atan2(dy, dx) + math.pi / 2
                dx += margin * math.cos(offset_angle)
                dy += margin * math.sin(offset_angle)
    
    target_angle = math.degrees(math.atan2(dx, -dy)) % 360
    
    # Calculate angle difference
    angle_diff = (target_angle - ship['angle']) % 360
    if angle_diff > 180:
        angle_diff -= 360
    
    # Determine acceleration based on distance and alignment
    is_aligned = abs(angle_diff) < 20  # Are we pointing roughly at target?
    
    if min_distance < 25:
        # Very close - slow down significantly
        if current_speed < 1.5:
            acceleration = 30
        else:
            acceleration = -60
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
            acceleration = 70
        else:
            acceleration = 20
    else:
        # Far - full speed if aligned
        if is_aligned:
            acceleration = 100
        else:
            acceleration = 40
    
    # Adaptive turning - turn faster when far, slower when close
    if min_distance < 40:
        max_turn = 15  # Tighter control when close
    else:
        max_turn = 35  # Faster turning when far
    
    if abs(angle_diff) > max_turn:
        new_angle = (ship['angle'] + max_turn * (1 if angle_diff > 0 else -1)) % 360
    else:
        new_angle = target_angle
    
    return {
        'acceleration': acceleration,
        'angle': int(new_angle),
        'data': ''
    }