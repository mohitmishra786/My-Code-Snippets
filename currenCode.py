import sys
import math
import heapq
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict

def debug(*args):
    print(*args, file=sys.stderr, flush=True)

# Terrain costs
CELL_COST = {0: 1, 1: 2, 2: 3, 3: 3}

# Direction priorities for pathfinding
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W

# Read initial input
my_id = int(input())
width = int(input())
height = int(input())

# Initialize grids
region_id_grid = [[0] * width for _ in range(height)]
type_grid = [[0] * width for _ in range(height)]

for y in range(height):
    for x in range(width):
        region_id, _type = [int(k) for k in input().split()]
        region_id_grid[y][x] = region_id
        type_grid[y][x] = _type

# Read towns
town_count = int(input())
towns: Dict[int, Tuple[int, int]] = {}
desired_by_src: Dict[int, List[int]] = {}
desired_by_dst: Dict[int, List[int]] = defaultdict(list)
town_cells: Set[Tuple[int, int]] = set()
regions_with_town: Set[int] = set()
poi_cells: Set[Tuple[int, int]] = set()

# Find POIs
for y in range(height):
    for x in range(width):
        if type_grid[y][x] == 3:
            poi_cells.add((x, y))

# Parse town data
for _ in range(town_count):
    inputs = input().split()
    town_id = int(inputs[0])
    town_x = int(inputs[1])
    town_y = int(inputs[2])
    raw = inputs[3] if len(inputs) > 3 else ""
    
    if raw.lower() in ("x", "-", "none", ""):
        desires = []
    else:
        desires = [int(t) for t in raw.split(",") if t != ""]
    
    towns[town_id] = (town_x, town_y)
    desired_by_src[town_id] = desires
    for dst_id in desires:
        desired_by_dst[dst_id].append(town_id)
    town_cells.add((town_x, town_y))
    regions_with_town.add(region_id_grid[town_y][town_x])

def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < width and 0 <= y < height

def move_cost(x: int, y: int) -> int:
    if (x, y) in town_cells:
        return 0
    return CELL_COST[type_grid[y][x]]

def dijkstra_path(src: Tuple[int, int], dst: Tuple[int, int], 
                 avoid_cells: Set[Tuple[int, int]] = set(),
                 avoid_inked: Set[int] = set()) -> Tuple[int, List[Tuple[int, int]]]:
    """Find shortest path from src to dst avoiding certain cells and inked regions."""
    sx, sy = src
    tx, ty = dst
    pq = [(0, sx, sy, [])]
    best = {(sx, sy): 0}
    
    while pq:
        cost, x, y, path = heapq.heappop(pq)
        if (x, y) == (tx, ty):
            return cost, path + [(x, y)]
        if cost != best[(x, y)]:
            continue
            
        # Try all directions in priority order
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in avoid_cells and (nx, ny) != (tx, ty):
                continue
            rid = region_id_grid[ny][nx]
            if rid in avoid_inked:
                continue
                
            step = move_cost(nx, ny)
            ncost = cost + step
            
            if (nx, ny) not in best or ncost < best[(nx, ny)]:
                best[(nx, ny)] = ncost
                heapq.heappush(pq, (ncost, nx, ny, path + [(x, y)]))
    
    return 10**9, []

# Game state variables
foe_id = 1 - my_id
turn_count = 0
side_quest_completed = False
active_connections_history = []
my_connections = {}
enemy_connections = {}

while True:
    turn_count += 1
    my_score = int(input())
    foe_score = int(input())
    
    # Parse board state
    active_connections: Set[str] = set()
    region_stats: Dict[int, Dict[str, any]] = {}
    inked_regions: Set[int] = set()
    cell_owner = {}
    cell_part_of = {}
    
    for y in range(height):
        for x in range(width):
            inputs = input().split()
            tracks_owner = int(inputs[0])
            instability = int(inputs[1])
            inked = inputs[2] != "0"
            part_of = inputs[3] if len(inputs) > 3 else "x"
            
            rid = region_id_grid[y][x]
            cell_owner[(x, y)] = tracks_owner
            
            if inked:
                inked_regions.add(rid)
                
            # Update region stats
            if rid not in region_stats:
                region_stats[rid] = {
                    "enemy_count": 0, 
                    "my_count": 0, 
                    "neutral_count": 0,
                    "instability": instability, 
                    "inked": inked,
                    "cells": []
                }
            
            region_stats[rid]["instability"] = instability
            region_stats[rid]["inked"] = inked or region_stats[rid]["inked"]
            region_stats[rid]["cells"].append((x, y))
            
            if tracks_owner == foe_id:
                region_stats[rid]["enemy_count"] += 1
            elif tracks_owner == my_id:
                region_stats[rid]["my_count"] += 1
            elif tracks_owner == 2:
                region_stats[rid]["neutral_count"] += 1
                
            if part_of != "x":
                cell_part_of[(x, y)] = part_of
                for token in part_of.split(","):
                    active_connections.add(token)
    
    # Track active connections
    active_connections_history.append(active_connections)
    
    # Analyze connections
    my_connections.clear()
    enemy_connections.clear()
    
    for conn_str in active_connections:
        parts = conn_str.split("-")
        if len(parts) == 2:
            src, dst = int(parts[0]), int(parts[1])
            # Count tracks for this connection
            my_tracks = 0
            enemy_tracks = 0
            
            for (x, y), part in cell_part_of.items():
                if conn_str in part.split(","):
                    if cell_owner[(x, y)] == my_id:
                        my_tracks += 1
                    elif cell_owner[(x, y)] == foe_id:
                        enemy_tracks += 1
            
            if my_tracks > 0:
                my_connections[conn_str] = my_tracks
            if enemy_tracks > 0:
                enemy_connections[conn_str] = enemy_tracks
    
    actions = []
    paint_used = 0
    disruption_used = False
    
    # Strategy 1: Complete side quest if possible
    if not side_quest_completed and poi_cells and paint_used < 3:
        best_poi = None
        best_cost = 10**9
        
        for tid, (tx, ty) in towns.items():
            for px, py in poi_cells:
                if cell_owner.get((px, py), -1) in (my_id, 2):
                    continue
                cost, path = dijkstra_path((tx, ty), (px, py), set(), inked_regions)
                if cost < best_cost:
                    best_cost = cost
                    best_poi = (tid, (px, py), path)
        
        if best_poi and best_cost <= 3:
            tid, (px, py), path = best_poi
            # Place track on POI
            if paint_used + 3 <= 3:
                actions.append(f"PLACE_TRACKS {px} {py}")
                paint_used += 3
                side_quest_completed = True
    
    # Strategy 2: Secure connections with manual placement
    best_connections = []
    
    for src_id, dst_list in desired_by_src.items():
        if src_id not in towns:
            continue
        sx, sy = towns[src_id]
        
        for dst_id in dst_list:
            if dst_id not in towns:
                continue
            tx, ty = towns[dst_id]
            
            # Check if already connected
            conn_key = f"{src_id}-{dst_id}"
            if conn_key in my_connections:
                continue
            
            cost, path = dijkstra_path((sx, sy), (tx, ty), set(), inked_regions)
            if cost < 10**9:
                # Calculate strategic value
                value = len(path)  # Base value is path length (more points)
                
                # Bonus for being targeted by enemy
                for rid in set(region_id_grid[y][x] for x, y in path):
                    if rid in region_stats and region_stats[rid]["enemy_count"] > 0:
                        value += 5
                
                # Bonus for POI overlap
                poi_overlap = sum(1 for x, y in path if (x, y) in poi_cells)
                value += poi_overlap * 3
                
                # Penalty for regions near inking
                for rid in set(region_id_grid[y][x] for x, y in path):
                    if rid in region_stats and region_stats[rid]["instability"] >= 2:
                        value -= 10
                
                best_connections.append((value, cost, src_id, dst_id, path))
    
    best_connections.sort(reverse=True)
    
    # Place tracks for best connection
    if best_connections and paint_used < 3:
        _, _, src_id, dst_id, path = best_connections[0]
        
        # Find unclaimed cells in path that we can afford
        for x, y in path[1:-1]:  # Skip towns
            if cell_owner.get((x, y), -1) not in (my_id, 2) and paint_used + move_cost(x, y) <= 3:
                actions.append(f"PLACE_TRACKS {x} {y}")
                paint_used += move_cost(x, y)
    
    # Strategy 3: Block enemy connections
    if paint_used < 3:
        for conn_str, enemy_track_count in enemy_connections.items():
            if enemy_track_count >= 2:  # Enemy has significant presence
                # Find cells in this connection we can block
                for (x, y), part in cell_part_of.items():
                    if conn_str in part.split(",") and cell_owner[(x, y)] == foe_id:
                        # Try to place our track nearby
                        for dx, dy in DIRECTIONS:
                            nx, ny = x + dx, y + dy
                            if in_bounds(nx, ny) and (nx, ny) not in town_cells:
                                if cell_owner.get((nx, ny), -1) == -1:
                                    cost = move_cost(nx, ny)
                                    if paint_used + cost <= 3:
                                        actions.append(f"PLACE_TRACKS {nx} {ny}")
                                        paint_used += cost
                                        break
                        if paint_used >= 3:
                            break
                if paint_used >= 3:
                    break
    
    # Strategy 4: Fill remaining paint points efficiently
    while paint_used < 3:
        # Find cheapest unclaimed cells near our tracks
        best_cell = None
        best_cost = 10
        
        for (x, y), owner in cell_owner.items():
            if owner == my_id:
                for dx, dy in DIRECTIONS:
                    nx, ny = x + dx, y + dy
                    if in_bounds(nx, ny) and (nx, ny) not in town_cells:
                        if cell_owner.get((nx, ny), -1) == -1:
                            cost = move_cost(nx, ny)
                            if paint_used + cost <= 3 and cost < best_cost:
                                best_cost = cost
                                best_cell = (nx, ny)
        
        if best_cell:
            actions.append(f"PLACE_TRACKS {best_cell[0]} {best_cell[1]}")
            paint_used += best_cost
        else:
            break
    
    # Strategy 5: Disruption
    if not disruption_used:
        disrupt_target = None
        best_disrupt_value = -10**9
        
        for rid, stats in region_stats.items():
            if stats["inked"] or rid in regions_with_town:
                continue
            
            value = 0
            
            # High priority: regions with enemy tracks that are part of connections
            if stats["enemy_count"] > 0:
                value += stats["enemy_count"] * 5
                
                # Check if this region is critical for enemy connections
                for conn_str in enemy_connections:
                    for (x, y) in stats["cells"]:
                        if cell_part_of.get((x, y), "").find(conn_str) != -1:
                            value += 10
                            break
            
            # Consider instability level
            if stats["instability"] == 2:
                value += 20  # One more disrupt will ink it
            elif stats["instability"] == 1:
                value += 5
            
            # Penalty for our own tracks
            value -= stats["my_count"] * 3
            
            if value > best_disrupt_value:
                best_disrupt_value = value
                disrupt_target = rid
        
        if disrupt_target:
            actions.append(f"DISRUPT {disrupt_target}")
            disruption_used = True
    
    # Output actions
    if not actions:
        actions = ["WAIT"]
    
    print("; ".join(actions))
    sys.stdout.flush()