import sys
from collections import deque

def paint_cost(cell_type):
    return {0: 1, 1: 2, 2: 3, 3: 3}[cell_type]

def debug(*args):
    print(*args, file=sys.stderr, flush=True)

def main():
    my_id = int(input())
    foe_id = 1 - my_id
    width = int(input())
    height = int(input())
   
    region_grid = [[0] * width for _ in range(height)]
    type_grid = [[0] * width for _ in range(height)]
    town_regions = set()
   
    for y in range(height):
        for x in range(width):
            rid, cell_type = map(int, input().split())
            region_grid[y][x] = rid
            type_grid[y][x] = cell_type
   
    town_count = int(input())
    towns = {}
    desires = {}
    town_set = set()
    poi_cells = set()
   
    for y in range(height):
        for x in range(width):
            if type_grid[y][x] == 3:
                poi_cells.add((x, y))
   
    for _ in range(town_count):
        parts = input().split()
        tid, tx, ty = int(parts[0]), int(parts[1]), int(parts[2])
        desired_s = parts[3] if len(parts) > 3 else "x"
        
        towns[tid] = (tx, ty)
        town_set.add((tx, ty))
        town_regions.add(region_grid[ty][tx])
        
        if desired_s not in ("x", "-", ""):
            desires[tid] = list(map(int, desired_s.split(',')))
        else:
            desires[tid] = []
   
    dr = [-1, 0, 1, 0]
    dc = [0, 1, 0, -1]
   
    def in_bounds(y, x):
        return 0 <= y < height and 0 <= x < width
   
    turn = 0
    last_autoplace = None
    autoplace_fail_count = 0
    
    while True:
        turn += 1
        try:
            my_score = int(input())
            foe_score = int(input())
        except EOFError:
            break
       
        track_owner = [[-1] * width for _ in range(height)]
        instability_grid = [[0] * width for _ in range(height)]
        inked = [[False] * width for _ in range(height)]
        connected_pairs = set()
       
        for y in range(height):
            for x in range(width):
                parts = input().split()
                owner = int(parts[0])
                inst = int(parts[1])
                inked_tok = parts[2]
                part_conn = parts[3] if len(parts) > 3 else "x"
                
                track_owner[y][x] = owner
                instability_grid[y][x] = inst
                inked[y][x] = (inked_tok != "0")
                
                if part_conn != "x":
                    for conn in part_conn.split(','):
                        parts_conn = conn.split('-')
                        if len(parts_conn) == 2:
                            try:
                                connected_pairs.add((int(parts_conn[0]), int(parts_conn[1])))
                            except:
                                pass
       
        actions = []
        paint = 3
        placed_this_turn = set()
       
        # Find best AUTOPLACE connection (shortest unconnected)
        best_connection = None
        best_dist = float('inf')
        
        for src_id, dest_list in desires.items():
            if src_id not in towns:
                continue
            
            sx, sy = towns[src_id]
            
            for dst_id in dest_list:
                if dst_id not in towns:
                    continue
                
                if (src_id, dst_id) in connected_pairs:
                    continue
                
                tx, ty = towns[dst_id]
                dist = abs(tx - sx) + abs(ty - sy)
                
                # Skip if we just tried this and failed
                if last_autoplace == (sx, sy, tx, ty) and autoplace_fail_count >= 2:
                    continue
                
                if dist < best_dist:
                    best_dist = dist
                    best_connection = (src_id, dst_id, sx, sy, tx, ty)
        
        # Manual track placement strategy - BUILD PATHS INCREMENTALLY
        # Priority 1: Build towards POIs (side quest)
        poi_progress = False
        if poi_cells:
            # Find closest POI to our existing network
            best_poi_cell = None
            best_poi_dist = float('inf')
            
            for px, py in poi_cells:
                # Skip if already has track
                if track_owner[py][px] != -1 or inked[py][px]:
                    continue
                
                # Check cost - only consider if affordable
                cost = paint_cost(type_grid[py][px])
                if cost > 3:
                    continue
                
                # Find distance to nearest town or our track
                min_dist = float('inf')
                for y in range(height):
                    for x in range(width):
                        if track_owner[y][x] == my_id or (x, y) in town_set:
                            dist = abs(px - x) + abs(py - y)
                            if dist < min_dist:
                                min_dist = dist
                
                if min_dist < best_poi_dist:
                    best_poi_dist = min_dist
                    best_poi_cell = (px, py, cost)
            
            # If POI is reachable, build path towards it
            if best_poi_cell:
                px, py, poi_cost = best_poi_cell
                
                # If we can afford the POI directly, place it
                if poi_cost <= paint:
                    actions.append(f"PLACE_TRACKS {px} {py}")
                    paint -= poi_cost
                    track_owner[py][px] = my_id
                    placed_this_turn.add((px, py))
                    poi_progress = True
                else:
                    # Build path towards POI incrementally
                    # Find cells adjacent to our network that move towards POI
                    candidates = []
                    
                    for y in range(height):
                        for x in range(width):
                            if track_owner[y][x] == my_id or (x, y) in town_set:
                                for k in range(4):
                                    ny, nx = y + dr[k], x + dc[k]
                                    
                                    if not in_bounds(ny, nx):
                                        continue
                                    if (nx, ny) in town_set or (nx, ny) in placed_this_turn:
                                        continue
                                    if track_owner[ny][nx] != -1 or inked[ny][nx]:
                                        continue
                                    
                                    cost = paint_cost(type_grid[ny][nx])
                                    dist_to_poi = abs(nx - px) + abs(ny - py)
                                    
                                    # Lower distance to POI is better
                                    candidates.append((dist_to_poi, cost, nx, ny))
                    
                    # Sort by distance to POI, then by cost
                    candidates.sort()
                    
                    # Place tracks moving towards POI
                    for _, cost, nx, ny in candidates[:3]:  # Place up to 3 tracks
                        if paint >= cost and (nx, ny) not in placed_this_turn:
                            actions.append(f"PLACE_TRACKS {nx} {ny}")
                            paint -= cost
                            track_owner[ny][nx] = my_id
                            placed_this_turn.add((nx, ny))
                            poi_progress = True
                            if paint <= 0:
                                break
        
        # Priority 2: If we have paint left and POI isn't making progress, expand network
        if paint > 0 and not poi_progress:
            expansion_candidates = []
            
            for y in range(height):
                for x in range(width):
                    if track_owner[y][x] == my_id or (x, y) in town_set:
                        for k in range(4):
                            ny, nx = y + dr[k], x + dc[k]
                            
                            if not in_bounds(ny, nx):
                                continue
                            if (nx, ny) in town_set or (nx, ny) in placed_this_turn:
                                continue
                            if track_owner[ny][nx] != -1 or inked[ny][nx]:
                                continue
                            
                            cost = paint_cost(type_grid[ny][nx])
                            # Prefer cheap cells (plains)
                            expansion_candidates.append((cost, nx, ny))
            
            # Remove duplicates and sort by cost
            unique_candidates = {}
            for cost, nx, ny in expansion_candidates:
                if (nx, ny) not in unique_candidates:
                    unique_candidates[(nx, ny)] = cost
            
            sorted_candidates = sorted(unique_candidates.items(), key=lambda x: x[1])
            
            for (nx, ny), cost in sorted_candidates:
                if paint >= cost and (nx, ny) not in placed_this_turn:
                    actions.append(f"PLACE_TRACKS {nx} {ny}")
                    paint -= cost
                    track_owner[ny][nx] = my_id
                    placed_this_turn.add((nx, ny))
                    if paint <= 0:
                        break
        
        # Add AUTOPLACE command
        if best_connection:
            _, _, sx, sy, tx, ty = best_connection
            actions.append(f"AUTOPLACE {sx} {sy} {tx} {ty}")
            
            # Track if same as last turn
            if last_autoplace == (sx, sy, tx, ty):
                autoplace_fail_count += 1
            else:
                autoplace_fail_count = 0
                last_autoplace = (sx, sy, tx, ty)
        
        # Disruption: Target enemy-heavy regions close to inking
        region_enemy = {}
        
        for y in range(height):
            for x in range(width):
                if inked[y][x]:
                    continue
                
                rid = region_grid[y][x]
                if rid in town_regions:
                    continue
                
                if track_owner[y][x] == foe_id:
                    if rid not in region_enemy:
                        region_enemy[rid] = {
                            'count': 0,
                            'instability': instability_grid[y][x]
                        }
                    region_enemy[rid]['count'] += 1
        
        best_disrupt = None
        best_score = -1
        
        for rid, info in region_enemy.items():
            score = info['count'] * 10
            
            if info['instability'] == 3:
                score += 100
            elif info['instability'] == 2:
                score += 50
            elif info['instability'] == 1:
                score += 20
            
            if score > best_score:
                best_score = score
                best_disrupt = rid
        
        if best_disrupt is not None:
            actions.append(f"DISRUPT {best_disrupt}")
        
        if not actions:
            actions = ["WAIT"]
        
        print(";".join(actions))
        sys.stdout.flush()

if __name__ == "__main__":
    main()
