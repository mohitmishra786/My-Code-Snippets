import sys
from collections import deque, defaultdict
import heapq

def debug(*args):
    print(*args, file=sys.stderr, flush=True)

def paint_cost(cell_type):
    return {0: 1, 1: 2, 2: 3, 3: 3}[cell_type]

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
    towns = {}  # town_id -> (x, y)
    desires = {}  # town_id -> list of desired connections
    town_positions = {}  # (x,y) -> town_id
    poi_cells = set()
   
    # Find POIs
    for y in range(height):
        for x in range(width):
            if type_grid[y][x] == 3:
                poi_cells.add((x, y))
   
    for _ in range(town_count):
        parts = input().split()
        tid, tx, ty = int(parts[0]), int(parts[1]), int(parts[2])
        desired_s = parts[3] if len(parts) > 3 else "x"
        
        towns[tid] = (tx, ty)
        town_positions[(tx, ty)] = tid
        town_regions.add(region_grid[ty][tx])
        
        if desired_s not in ("x", "-", ""):
            desires[tid] = list(map(int, desired_s.split(',')))
        else:
            desires[tid] = []
   
    dr = [-1, 0, 1, 0]
    dc = [0, 1, 0, -1]
   
    def in_bounds(y, x):
        return 0 <= y < height and 0 <= x < width
   
    def is_town_cell(x, y):
        return (x, y) in town_positions
   
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
        active_connections = set()
       
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
                        active_connections.add(conn)
       
        # Parse active connections to know which are already done
        connected_pairs = set()
        for conn in active_connections:
            parts = conn.split('-')
            if len(parts) == 2:
                try:
                    src_id, dst_id = int(parts[0]), int(parts[1])
                    connected_pairs.add((src_id, dst_id))
                except:
                    pass
       
        def can_reach(sx, sy, tx, ty):
            """BFS to check if destination is reachable through non-inked regions"""
            vis = [[False] * width for _ in range(height)]
            q = deque([(sy, sx)])
            vis[sy][sx] = True
           
            while q:
                y, x = q.popleft()
                if y == ty and x == tx:
                    return True
               
                for k in range(4):
                    ny, nx = y + dr[k], x + dc[k]
                    if not in_bounds(ny, nx) or vis[ny][nx] or inked[ny][nx]:
                        continue
                    vis[ny][nx] = True
                    q.append((ny, nx))
           
            return False
       
        actions = []
        paint = 3
       
        # Strategy 1: Try to complete side quest (connect to POI)
        if poi_cells:
            for tid, (tx, ty) in towns.items():
                for poi_x, poi_y in poi_cells:
                    # Check if we can build path
                    if can_reach(tx, ty, poi_x, poi_y):
                        # Try to place track on or near POI
                        if track_owner[poi_y][poi_x] == -1 and not inked[poi_y][poi_x]:
                            cost = paint_cost(type_grid[poi_y][poi_x])
                            if cost <= paint:
                                actions.append(f"PLACE_TRACKS {poi_x} {poi_y}")
                                paint -= cost
                                break
                        else:
                            # Try to build towards POI
                            for k in range(4):
                                ny, nx = poi_y + dr[k], poi_x + dc[k]
                                if in_bounds(ny, nx) and track_owner[ny][nx] == -1 and not inked[ny][nx]:
                                    if not is_town_cell(nx, ny):
                                        cost = paint_cost(type_grid[ny][nx])
                                        if cost <= paint:
                                            actions.append(f"PLACE_TRACKS {nx} {ny}")
                                            paint -= cost
                                            break
                if paint <= 0:
                    break
       
        # Strategy 2: Use AUTOPLACE to build connections
        connection_priority = []
        
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
                
                # Check if reachable
                if can_reach(sx, sy, tx, ty):
                    # Calculate priority (prefer shorter distances)
                    dist = abs(tx - sx) + abs(ty - sy)
                    connection_priority.append((dist, src_id, dst_id, sx, sy, tx, ty))
        
        # Sort by distance (shortest first for easier completion)
        connection_priority.sort()
        
        # Try to build using AUTOPLACE
        if connection_priority and len(actions) == 0:
            _, src_id, dst_id, sx, sy, tx, ty = connection_priority[0]
            actions.append(f"AUTOPLACE {sx} {sy} {tx} {ty}")
       
        # Strategy 3: Manual track placement for expansion
        if paint > 0:
            # Find our existing tracks and expand from them
            expansion_cells = []
            
            for y in range(height):
                for x in range(width):
                    if track_owner[y][x] == my_id or is_town_cell(x, y):
                        # Look at neighbors
                        for k in range(4):
                            ny, nx = y + dr[k], x + dc[k]
                            if in_bounds(ny, nx) and track_owner[ny][nx] == -1 and not inked[ny][nx]:
                                if not is_town_cell(nx, ny):
                                    cost = paint_cost(type_grid[ny][nx])
                                    # Prefer plains (cheap)
                                    priority = cost
                                    # Bonus if near POI
                                    if (nx, ny) in poi_cells:
                                        priority -= 10
                                    expansion_cells.append((priority, cost, nx, ny))
            
            # Sort by priority
            expansion_cells.sort()
            
            # Place tracks
            placed = set()
            for _, cost, x, y in expansion_cells:
                if paint >= cost and (x, y) not in placed:
                    actions.append(f"PLACE_TRACKS {x} {y}")
                    paint -= cost
                    placed.add((x, y))
                    if paint <= 0:
                        break
       
        # Strategy 4: Aggressive disruption
        region_enemy_count = {}
        region_instability = {}
        
        for y in range(height):
            for x in range(width):
                rid = region_grid[y][x]
                if inked[y][x] or rid in town_regions:
                    continue
                
                if rid not in region_enemy_count:
                    region_enemy_count[rid] = 0
                    region_instability[rid] = instability_grid[y][x]
                
                if track_owner[y][x] == foe_id:
                    region_enemy_count[rid] += 1
       
        # Find best region to disrupt
        best_disrupt = None
        best_score = -1
       
        for rid, enemy_count in region_enemy_count.items():
            if enemy_count == 0:
                continue
            
            score = enemy_count * 10
            
            inst = region_instability[rid]
            # Prioritize regions close to inking
            if inst == 3:
                score += 100  # One more disruption inks it
            elif inst == 2:
                score += 50
            elif inst == 1:
                score += 20
            
            if score > best_score:
                best_score = score
                best_disrupt = rid
       
        if best_disrupt is not None:
            actions.append(f"DISRUPT {best_disrupt}")
       
        # Output
        if not actions:
            actions = ["WAIT"]
       
        print(";".join(actions))
        sys.stdout.flush()

if __name__ == "__main__":
    main()
