import sys
import math
import heapq
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict, deque

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
towns_by_region: Dict[int, List[int]] = defaultdict(list)

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
    
    region = region_id_grid[town_y][town_x]
    regions_with_town.add(region)
    towns_by_region[region].append(town_id)

def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < width and 0 <= y < height

def move_cost(x: int, y: int) -> int:
    if (x, y) in town_cells:
        return 0
    return CELL_COST[type_grid[y][x]]

def get_neighbors(x: int, y: int) -> List[Tuple[int, int]]:
    """Get valid neighbors in priority order (N, E, S, W)"""
    neighbors = []
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny):
            neighbors.append((nx, ny))
    return neighbors

def find_path_for_tracks(src: Tuple[int, int], dst: Tuple[int, int], 
                        occupied: Set[Tuple[int, int]], 
                        inked_regions: Set[int],
                        max_cost: int = 3) -> List[Tuple[int, int]]:
    """Find cells to place tracks between src and dst, avoiding occupied cells"""
    sx, sy = src
    tx, ty = dst
    
    # BFS to find shortest path considering occupied cells
    queue = deque([(sx, sy, [])])
    visited = {(sx, sy)}
    
    while queue:
        x, y, path = queue.popleft()
        
        if (x, y) == (tx, ty):
            # Filter out towns and occupied cells from path
            result = []
            for px, py in path:
                if (px, py) not in town_cells and (px, py) not in occupied:
                    cost = move_cost(px, py)
                    if cost <= max_cost:
                        result.append((px, py))
            return result
        
        for nx, ny in get_neighbors(x, y):
            if (nx, ny) in visited:
                continue
            
            rid = region_id_grid[ny][nx]
            if rid in inked_regions:
                continue
            
            # We can move through occupied cells, but can't place tracks there
            visited.add((nx, ny))
            queue.append((nx, ny, path + [(nx, ny)]))
    
    return []

def calculate_region_value(region_id: int, region_stats: Dict) -> int:
    """Calculate strategic value of a region"""
    if region_id not in region_stats:
        return 0
    
    stats = region_stats[region_id]
    value = 0
    
    # High value for regions with multiple towns
    value += len(towns_by_region.get(region_id, [])) * 100
    
    # Value for POIs in region
    for x, y in stats.get("cells", []):
        if (x, y) in poi_cells:
            value += 50
    
    # Penalty for enemy presence
    value -= stats.get("enemy_count", 0) * 20
    
    # Bonus for our presence
    value += stats.get("my_count", 0) * 10
    
    # Penalty for high instability
    instability = stats.get("instability", 0)
    if instability >= 2:
        value -= 100
    elif instability == 1:
        value -= 30
    
    return value

# Game state variables
foe_id = 1 - my_id
turn_count = 0
side_quest_completed = False
current_strategy = "side_quest"
attempted_placements = set()

while True:
    turn_count += 1
    my_score = int(input())
    foe_score = int(input())
    
    # Parse board state
    active_connections: Set[str] = set()
    region_stats: Dict[int, Dict[str, any]] = {}
    inked_regions: Set[int] = set()
    cell_owner = {}
    occupied_cells = set()  # Cells with any tracks
    
    for y in range(height):
        for x in range(width):
            inputs = input().split()
            tracks_owner = int(inputs[0])
            instability = int(inputs[1])
            inked = inputs[2] != "0"
            part_of = inputs[3] if len(inputs) > 3 else "x"
            
            rid = region_id_grid[y][x]
            cell_owner[(x, y)] = tracks_owner
            
            # Track occupied cells (has any track)
            if tracks_owner != -1:
                occupied_cells.add((x, y))
            
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
                for token in part_of.split(","):
                    active_connections.add(token)
    
    actions = []
    paint_used = 0
    cells_to_place = []
    
    # Strategy 1: PRIORITIZE SIDE QUEST
    if not side_quest_completed and poi_cells:
        # Find shortest path from any town to any POI
        best_side_quest = None
        best_cost = 10**9
        
        for tid, (tx, ty) in towns.items():
            for px, py in poi_cells:
                # Check if POI already has our track
                if cell_owner.get((px, py), -1) == my_id:
                    side_quest_completed = True
                    break
                    
                # Find path to POI
                path = find_path_for_tracks((tx, ty), (px, py), occupied_cells, inked_regions, 3)
                if path:
                    # Calculate total cost
                    total_cost = sum(move_cost(x, y) for x, y in path[:1])  # Just first cell
                    if total_cost <= 3 and total_cost < best_cost:
                        best_cost = total_cost
                        best_side_quest = (tid, (px, py), path)
        
        if best_side_quest and not side_quest_completed:
            tid, (px, py), path = best_side_quest
            # Place tracks towards POI
            for x, y in path:
                if (x, y) == (px, py) and paint_used + 3 <= 3:
                    # Place on POI directly
                    cells_to_place.append((x, y, 3))
                    paint_used += 3
                    side_quest_completed = True
                    break
                elif (x, y) not in occupied_cells and (x, y) not in town_cells:
                    cost = move_cost(x, y)
                    if paint_used + cost <= 3:
                        cells_to_place.append((x, y, cost))
                        paint_used += cost
                        occupied_cells.add((x, y))
                        if paint_used >= 3:
                            break
    
    # Strategy 2: Focus on high-value connections in regions with multiple towns
    if paint_used < 3:
        # Sort regions by value
        region_values = [(calculate_region_value(rid, region_stats), rid) for rid in region_stats]
        region_values.sort(reverse=True)
        
        # Look for connections in high-value regions
        best_connections = []
        
        for src_id, desires in desired_by_src.items():
            if src_id not in towns:
                continue
                
            sx, sy = towns[src_id]
            src_region = region_id_grid[sy][sx]
            
            for dst_id in desires:
                if dst_id not in towns:
                    continue
                    
                tx, ty = towns[dst_id]
                dst_region = region_id_grid[ty][tx]
                
                # Prioritize connections in high-value regions
                region_value = max(
                    calculate_region_value(src_region, region_stats),
                    calculate_region_value(dst_region, region_stats)
                )
                
                # Find buildable path
                path = find_path_for_tracks((sx, sy), (tx, ty), occupied_cells, inked_regions, 3)
                if path:
                    # Calculate actual cost we can afford
                    affordable_cells = []
                    temp_cost = paint_used
                    for x, y in path:
                        cost = move_cost(x, y)
                        if temp_cost + cost <= 3:
                            affordable_cells.append((x, y))
                            temp_cost += cost
                        else:
                            break
                    
                    if affordable_cells:
                        best_connections.append((region_value, src_id, dst_id, affordable_cells))
        
        best_connections.sort(reverse=True)
        
        # Place tracks for best connection
        if best_connections:
            _, src_id, dst_id, affordable_cells = best_connections[0]
            
            for x, y in affordable_cells:
                if (x, y) not in occupied_cells and (x, y) not in town_cells:
                    cost = move_cost(x, y)
                    if paint_used + cost <= 3:
                        cells_to_place.append((x, y, cost))
                        paint_used += cost
                        occupied_cells.add((x, y))
    
    # Strategy 3: Expand from existing tracks in valuable regions
    if paint_used < 3:
        expansion_candidates = []
        
        for (x, y), owner in cell_owner.items():
            if owner == my_id:
                for nx, ny in get_neighbors(x, y):
                    if (nx, ny) not in occupied_cells and (nx, ny) not in town_cells:
                        rid = region_id_grid[ny][nx]
                        if rid not in inked_regions:
                            cost = move_cost(nx, ny)
                            if paint_used + cost <= 3:
                                value = calculate_region_value(rid, region_stats)
                                # Bonus for cells next to POIs
                                if (nx, ny) in poi_cells:
                                    value += 100
                                expansion_candidates.append((value, nx, ny, cost))
        
        expansion_candidates.sort(reverse=True)
        
        for _, nx, ny, cost in expansion_candidates:
            if paint_used + cost <= 3 and (nx, ny) not in occupied_cells:
                cells_to_place.append((nx, ny, cost))
                paint_used += cost
                occupied_cells.add((nx, ny))
                if paint_used >= 3:
                    break
    
    # Build PLACE_TRACKS actions
    for x, y, _ in cells_to_place:
        actions.append(f"PLACE_TRACKS {x} {y}")
    
    # Strategy 4: Disruption targeting
    disrupt_target = None
    best_disrupt_value = -10**9
    
    for rid, stats in region_stats.items():
        if stats["inked"] or rid in regions_with_town:
            continue
        
        value = 0
        
        # High priority for regions about to be inked
        if stats["instability"] == 2:
            # Check if enemy has significant presence
            if stats["enemy_count"] > stats["my_count"]:
                value += 100
        elif stats["instability"] == 1:
            if stats["enemy_count"] > stats["my_count"] + 2:
                value += 50
        
        # Value for disrupting enemy connections
        if stats["enemy_count"] > 0:
            value += stats["enemy_count"] * 10
            
        # Penalty for our own tracks
        value -= stats["my_count"] * 20
        
        # Bonus for regions that connect multiple towns
        town_connections = 0
        for cell in stats["cells"]:
            for tid, (tx, ty) in towns.items():
                if abs(cell[0] - tx) <= 2 and abs(cell[1] - ty) <= 2:
                    town_connections += 1
        value += town_connections * 5
        
        if value > best_disrupt_value:
            best_disrupt_value = value
            disrupt_target = rid
    
    if disrupt_target:
        actions.append(f"DISRUPT {disrupt_target}")
    
    # Output actions
    if not actions:
        actions = ["WAIT"]
    
    print("; ".join(actions))
    sys.stdout.flush()
    
    # Update todo status
    if turn_count == 1:
        debug(f"Turn {turn_count}: Side quest status: {side_quest_completed}")
        debug(f"POI cells: {poi_cells}")
        debug(f"High value regions: {sorted([(rid, len(towns_by_region.get(rid, []))) for rid in regions_with_town], key=lambda x: x[1], reverse=True)[:5]}")
