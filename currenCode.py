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
       
        # Simple strategy: Use AUTOPLACE for shortest unconnected desired connection
        best_connection = None
        best_dist = float('inf')
        
        for src_id, dest_list in desires.items():
            if src_id not in towns:
                continue
            
            sx, sy = towns[src_id]
            
            for dst_id in dest_list:
                if dst_id not in towns:
                    continue
                
                # Skip if already connected
                if (src_id, dst_id) in connected_pairs:
                    continue
                
                tx, ty = towns[dst_id]
                dist = abs(tx - sx) + abs(ty - sy)
                
                if dist < best_dist:
                    best_dist = dist
                    best_connection = (src_id, dst_id, sx, sy, tx, ty)
        
        # Place AUTOPLACE command
        if best_connection:
            _, _, sx, sy, tx, ty = best_connection
            actions.append(f"AUTOPLACE {sx} {sy} {tx} {ty}")
        
        # Try to use remaining paint points strategically
        # Priority 1: Place track on POI if possible
        for px, py in poi_cells:
            if track_owner[py][px] == -1 and not inked[py][px]:
                cost = paint_cost(type_grid[py][px])
                if cost <= paint:
                    actions.append(f"PLACE_TRACKS {px} {py}")
                    paint -= cost
                    track_owner[py][px] = my_id  # Mark as placed
                    break
        
        # Priority 2: Expand from our tracks or towns to fill remaining paint
        if paint > 0:
            placed_this_turn = set()
            
            for y in range(height):
                for x in range(width):
                    if paint <= 0:
                        break
                    
                    # Find our tracks or towns
                    if track_owner[y][x] == my_id or (x, y) in town_set:
                        # Check neighbors
                        for k in range(4):
                            ny, nx = y + dr[k], x + dc[k]
                            
                            if not in_bounds(ny, nx):
                                continue
                            if (nx, ny) in town_set:
                                continue
                            if (nx, ny) in placed_this_turn:
                                continue
                            if track_owner[ny][nx] != -1:
                                continue
                            if inked[ny][nx]:
                                continue
                            
                            cost = paint_cost(type_grid[ny][nx])
                            if cost <= paint:
                                actions.append(f"PLACE_TRACKS {nx} {ny}")
                                paint -= cost
                                track_owner[ny][nx] = my_id
                                placed_this_turn.add((nx, ny))
                                break
                
                if paint <= 0:
                    break
        
        # Disruption strategy: Target enemy-heavy regions
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
            
            # Prioritize regions close to inking
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
