import sys
from collections import deque, defaultdict
import heapq

class Town:
    def __init__(self, id, x, y, desired):
        self.id = id
        self.x = x
        self.y = y
        self.desired = desired

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
    towns = []
    town_id_to_idx = {}
    town_positions = {}  # (x,y) -> town_id
    poi_cells = set()
   
    # Find POIs
    for y in range(height):
        for x in range(width):
            if type_grid[y][x] == 3:
                poi_cells.add((x, y))
   
    for i in range(town_count):
        parts = input().split()
        tid, tx, ty = int(parts[0]), int(parts[1]), int(parts[2])
        desired_s = parts[3] if len(parts) > 3 else "x"
        desired = []
        if desired_s != "x" and desired_s != "-":
            desired = list(map(int, desired_s.split(',')))
        towns.append(Town(tid, tx, ty, desired))
        town_id_to_idx[tid] = i
        town_positions[(tx, ty)] = tid
        town_regions.add(region_grid[ty][tx])
   
    dr = [-1, 0, 1, 0]
    dc = [0, 1, 0, -1]
   
    def in_bounds(y, x):
        return 0 <= y < height and 0 <= x < width
   
    def is_town_cell(y, x):
        return (x, y) in town_positions
   
    turn = 0
    
    while True:
        turn += 1
        try:
            my_score = int(input())
            foe_score = int(input())
        except EOFError:
            break
       
        track_owner = [[0] * width for _ in range(height)]
        instability = [[0] * width for _ in range(height)]
        inked = [[False] * width for _ in range(height)]
        active_connections = set()
        connection_paths = defaultdict(set)  # connection -> set of cells
       
        for y in range(height):
            for x in range(width):
                parts = input().split()
                owner = int(parts[0])
                inst = int(parts[1])
                inked_tok = parts[2]
                part_conn = parts[3] if len(parts) > 3 else "x"
                
                track_owner[y][x] = owner
                instability[y][x] = inst
                inked[y][x] = (inked_tok != "0")
                
                # Track active connections
                if part_conn != "x":
                    for conn in part_conn.split(','):
                        active_connections.add(conn)
                        connection_paths[conn].add((x, y))
       
        # Check which desired connections are already active
        already_connected = set()
        for conn in active_connections:
            parts = conn.split('-')
            if len(parts) == 2:
                src_id, dst_id = int(parts[0]), int(parts[1])
                already_connected.add((src_id, dst_id))
       
        def has_connection(town_a_id, town_b_id):
            """Check if two towns are already connected"""
            return (town_a_id, town_b_id) in already_connected
       
        def bfs_connected(sx, sy, tx, ty):
            """Check if there's a path of tracks/towns between two points"""
            vis = [[False] * width for _ in range(height)]
            q = deque()
            q.append((sy, sx))
            vis[sy][sx] = True
           
            while q:
                y, x = q.popleft()
                if y == ty and x == tx:
                    return True
               
                for k in range(4):
                    ny, nx = y + dr[k], x + dc[k]
                    if not in_bounds(ny, nx) or vis[ny][nx] or inked[ny][nx]:
                        continue
                    # Can traverse through our tracks, neutral tracks, or towns
                    if track_owner[ny][nx] in (my_id, 2) or is_town_cell(ny, nx):
                        vis[ny][nx] = True
                        q.append((ny, nx))
           
            return False
       
        def find_best_path(sx, sy, tx, ty, budget=3):
            """Find optimal path considering cost and existing tracks"""
            INF = int(1e9)
            dist = [[INF] * width for _ in range(height)]
            parent = [[(-1, -1)] * width for _ in range(height)]
           
            pq = []
            dist[sy][sx] = 0
            heapq.heappush(pq, (0, sy, sx))
           
            while pq:
                d, y, x = heapq.heappop(pq)
                if d != dist[y][x]:
                    continue
               
                if y == ty and x == tx:
                    break
               
                for k in range(4):
                    ny, nx = y + dr[k], x + dc[k]
                    if not in_bounds(ny, nx) or inked[ny][nx]:
                        continue
                   
                    # Calculate cost
                    cost = 0
                    if not is_town_cell(ny, nx):
                        if track_owner[ny][nx] == my_id:
                            cost = 0  # Already our track
                        elif track_owner[ny][nx] == foe_id:
                            cost = INF  # Can't place on enemy tracks
                        elif track_owner[ny][nx] == 2:
                            cost = 0  # Neutral track is free to traverse
                        else:  # Empty cell
                            cost = paint_cost(type_grid[ny][nx])
                   
                    new_dist = dist[y][x] + cost
                    if new_dist < dist[ny][nx] and new_dist <= budget:
                        dist[ny][nx] = new_dist
                        parent[ny][nx] = (y, x)
                        heapq.heappush(pq, (new_dist, ny, nx))
           
            # Reconstruct path
            if dist[ty][tx] >= INF:
                return INF, []
           
            path = []
            cy, cx = ty, tx
            while (cy, cx) != (-1, -1):
                path.append((cx, cy))
                py, px = parent[cy][cx]
                cy, cx = py, px
           
            path.reverse()
            return dist[ty][tx], path
       
        # Find side quest opportunities (connecting to POIs)
        side_quest_candidates = []
        if poi_cells:
            for town in towns:
                for poi_x, poi_y in poi_cells:
                    # Check if POI is already connected
                    if bfs_connected(town.x, town.y, poi_x, poi_y):
                        continue
                    
                    cost, path = find_best_path(town.x, town.y, poi_x, poi_y, budget=3)
                    if cost < INF:
                        side_quest_candidates.append((cost, town.id, (poi_x, poi_y), path))
       
        # Sort by cost (cheapest first)
        side_quest_candidates.sort(key=lambda x: x[0])
       
        # Find all possible connections
        connection_candidates = []
       
        for i in range(len(towns)):
            town_a = towns[i]
            for wanted_id in town_a.desired:
                if wanted_id not in town_id_to_idx:
                    continue
               
                # Check if already connected
                if has_connection(town_a.id, wanted_id):
                    continue
               
                town_b = towns[town_id_to_idx[wanted_id]]
                
                # Check if there's already a path
                if bfs_connected(town_a.x, town_a.y, town_b.x, town_b.y):
                    continue
               
                cost, path = find_best_path(town_a.x, town_a.y, town_b.x, town_b.y, budget=3)
                if cost < INF and len(path) > 0:
                    # Calculate priority
                    priority = cost  # Prefer cheaper connections
                    connection_candidates.append((priority, cost, town_a.id, town_b.id, path))
       
        # Sort by priority (lowest cost first)
        connection_candidates.sort(key=lambda x: x[0])
       
        paint = 3
        actions = []
        placed_this_turn = set()
       
        # Priority 1: Side quests if cheap enough
        if side_quest_candidates and side_quest_candidates[0][0] <= paint:
            cost, tid, (poi_x, poi_y), path = side_quest_candidates[0]
            for px, py in path:
                if is_town_cell(py, px) or (px, py) in placed_this_turn:
                    continue
                if track_owner[py][px] != -1:
                    continue
                    
                cell_cost = paint_cost(type_grid[py][px])
                if cell_cost <= paint:
                    actions.append(f"PLACE_TRACKS {px} {py}")
                    paint -= cell_cost
                    placed_this_turn.add((px, py))
                    
                    if paint <= 0:
                        break
       
        # Priority 2: Complete connections
        for _, cost, src_id, dst_id, path in connection_candidates:
            if paint <= 0:
                break
               
            for px, py in path:
                if is_town_cell(py, px) or (px, py) in placed_this_turn:
                    continue
                if track_owner[py][px] != -1:
                    continue
                    
                cell_cost = paint_cost(type_grid[py][px])
                if cell_cost <= paint:
                    actions.append(f"PLACE_TRACKS {px} {py}")
                    paint -= cell_cost
                    placed_this_turn.add((px, py))
                    
                    if paint <= 0:
                        break
       
        # Strategic disruption
        region_analysis = defaultdict(lambda: {
            'enemy_tracks': 0,
            'my_tracks': 0,
            'instability': 0,
            'is_town_region': False,
            'cells': []
        })
       
        for y in range(height):
            for x in range(width):
                rid = region_grid[y][x]
                if inked[y][x]:
                    continue
                    
                region_analysis[rid]['instability'] = instability[y][x]
                region_analysis[rid]['is_town_region'] = rid in town_regions
                region_analysis[rid]['cells'].append((x, y))
                
                if track_owner[y][x] == foe_id:
                    region_analysis[rid]['enemy_tracks'] += 1
                elif track_owner[y][x] == my_id:
                    region_analysis[rid]['my_tracks'] += 1
       
        # Find best region to disrupt
        best_disrupt = None
        best_score = -1
       
        for rid, stats in region_analysis.items():
            if stats['is_town_region'] or stats['instability'] >= 4:
                continue
               
            score = 0
            
            # High priority if enemy has many tracks
            score += stats['enemy_tracks'] * 10
            
            # Extra priority if close to inking (instability 3 means one more disrupt inks it)
            if stats['instability'] == 3:
                score += 50
            elif stats['instability'] == 2:
                score += 20
                
            # Penalty for our own tracks
            score -= stats['my_tracks'] * 15
            
            # Bonus if this region is part of enemy connections
            region_in_connection = False
            for (x, y) in stats['cells']:
                for conn, cells in connection_paths.items():
                    if (x, y) in cells and '-' in conn:
                        # Check if enemy owns tracks in this connection
                        enemy_owned = any(track_owner[cy][cx] == foe_id for cx, cy in cells)
                        if enemy_owned:
                            region_in_connection = True
                            score += 30
                            break
                if region_in_connection:
                    break
            
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
