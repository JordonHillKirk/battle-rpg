# core/map_engine.py

import random

from areas import *
from core.area_utils import press_enter_to_continue

RULES = {}

# --------------------------------------------------
# DEBUG OUTPUT
# --------------------------------------------------

def print_connections(areas, conns):
    with open("map.txt", "w") as f:
        for node in conns:
            f.write(f"area {node}: {areas[node]['name']}\n")
            f.write(f"forward: {conns[node]['forward']}\n")
            f.write(f"back: {conns[node]['back']}\n\n")


# --------------------------------------------------
# AREA DEFINITIONS
# --------------------------------------------------

s = {"name": "Start", "func": start}

normal_areas = [
    {"name": "Goblin Toll", "func": goblin_toll},
    {"name": "Bandits", "func": bandits},
]

random_encounters = [
    {"name": "Traveling Merchant", "func": traveling_merchant, "target": 25, "rules": ["random_encounter"]},
    {"name": "Traveling Merchant", "func": traveling_merchant, "target": 25, "rules": ["random_encounter"]},
    {"name": "Traveling Merchant2", "func": traveling_merchant2, "target": 25, "rules": ["random_encounter"]},
    {"name": "Traveling Merchant2", "func": traveling_merchant2, "target": 25, "rules": ["random_encounter"]},
    {"name": "Actual Fork", "func": actual_fork, "target": 10, "rules": ["random_encounter"]},
]

branching_areas = [
    {"name": "Fork", "func": fork},
    {"name": "Fork2", "func": fork},
]

endpoint_areas = [
    {"name": "Cave", "func": cave},
    {"name": "Oasis", "func": oasis},
]

dummy_endpoints = [
    {"name": "Dummy Cave", "func": cave},
]

one_way_from_areas = [
    {"name": "Teleporter Trap", "func": teleporter_trap},
]

one_way_to_areas = [
    {
        "name": "Teleporter Trap Landing",
        "func": teleporter_trap_landing,
        "rules": ["teleport_only"]
    },
]


# --------------------------------------------------
# MAP RANDOMIZATION (RESTORED)
# --------------------------------------------------

def randomize_areas(ctx):

    def connect(from_area, to_area, one_way=False):

        # redirect dummy cave
        if areas[to_area]["name"] == "Dummy Cave":
            to_area = next(
                node["index"] for node in areas
                if node["name"] == "Cave"
            )

        connections[from_area]["forward"].append(to_area)

        if not one_way:
            connections[to_area]["back"].append(from_area)

    def find_area_index(a):
        return next(idx for idx, node in enumerate(areas) if node == a)

    areas = []
    endpoints = []
    connections = {}
    areas.clear()
    endpoints.clear()
    connections.clear()

    areas.extend(normal_areas)
    areas.extend(random_encounters)
    areas.extend(branching_areas)
    areas.extend(one_way_to_areas)

    endpoints.extend(endpoint_areas)
    endpoints.extend(dummy_endpoints)
    endpoints.extend(one_way_from_areas)

    random.shuffle(endpoints)

    # first endpoint
    areas.append(endpoints[0])

    random.shuffle(areas)
    areas.insert(0, s)

    # assign indices
    for i, node in enumerate(areas):
        node["index"] = i

    # insert endpoints for branches
    for i, branch in enumerate(branching_areas, start=1):
        branch_index = find_area_index(branch)
        insert_index = random.randint(branch_index + 1, len(areas))
        areas.insert(insert_index, endpoints[i])

    # final endpoint
    areas.append(endpoints[-1])

    # reindex
    for i, node in enumerate(areas):
        node["index"] = i
        connections[i] = {"forward": [], "back": []}

    endpoints.sort(key=lambda ep: ep["index"])
    branching_areas.sort(key=lambda br: br["index"])

    # connect graph
    for i, node in enumerate(areas):

        if node["name"] == "Start":
            connect(i, i + 1)
            connect(i, endpoints[0]["index"] + 1)

        elif node in branching_areas:
            branch_index = branching_areas.index(node)
            connect(i, i + 1)
            connect(i, endpoints[branch_index + 1]["index"] + 1)

        elif node in one_way_from_areas:
            landing = one_way_to_areas[0]
            connect(i, landing["index"], one_way=True)

        elif node in endpoints:
            pass

        else:
            connect(i, i + 1)

    print_connections(areas, connections)
    ctx.map.areas = areas
    ctx.map.endpoints = endpoints
    ctx.map.connections = connections
    for node in areas:
        if node in dummy_endpoints:
            ctx.map.visited.append(True)
        else:
            ctx.map.visited.append(False)


# --------------------------------------------------
# SKIP ROUTING
# --------------------------------------------------

def skip(ctx, num, dir):
    direction = "forward"
    index = 0
    d = "forward" if direction == dir else "back"
    return ctx.map.connections[num][d][index], d, num


# --------------------------------------------------
# AREA EXECUTION ENGINE
# --------------------------------------------------

def area(ctx, num, dir, last_area):
    side_path = False
    node = ctx.map.areas[num]

    # --------------------------------------------------
    # VISIT TRACKING
    # --------------------------------------------------
    first_time = not ctx.map.visited[num]
    ctx.map.visited[num] = True

    # --------------------------------------------------
    # RULE ENGINE
    # --------------------------------------------------
    rule_result = evaluate_rules(ctx, node, num, dir, last_area)
    if rule_result is not None:
        return rule_result

    # --------------------------------------------------
    # BRANCHING AREA LOGIC
    # --------------------------------------------------
    if node in branching_areas:

        # degenerate branch (both exits same)
        if ctx.map.connections[num]["forward"][0] == ctx.map.connections[num]["forward"][1]:
            return skip(ctx, num, dir)

        # determine if arriving from side path
        if last_area == ctx.map.connections[num]["forward"][1]:
            side_path = True
        else:
            side_path = False
    else:
        side_path = False

    # --------------------------------------------------
    # SAME ENTRY DETECTION (CAVE LOGIC)
    # --------------------------------------------------
    same_entries = False
    if (
        len(ctx.map.connections[num]["back"]) > 1
        and ctx.map.connections[num]["back"][0] == ctx.map.connections[num]["back"][1]
    ):
        same_entries = True

    # --------------------------------------------------
    # CALL AREA FUNCTION (SIGNATURE ADAPTER)
    # --------------------------------------------------
    func = node["func"]
    kwargs = {
        "first_time": first_time,
        "same_entries": same_entries,
        "side_path": side_path,
    }

    direction, index = func(ctx, kwargs)

    # --------------------------------------------------
    # PAUSE HANDLING
    # --------------------------------------------------
    if node not in random_encounters:
        press_enter_to_continue()
    elif ctx.map.random_encounter_triggered:
        ctx.map.random_encounter_triggered = False
        press_enter_to_continue()

    # --------------------------------------------------
    # DIRECTION RESOLUTION
    # --------------------------------------------------
    if node in branching_areas and direction == "forward" and index == 1:
        # side path ALWAYS treated as forward
        d = "forward"
    else:
        if direction == "forward":
            d = dir
        else:
            d = "back" if dir == "forward" else "forward"

    # --------------------------------------------------
    # ROUTING RESOLUTION
    # --------------------------------------------------
    try:
        if index == -1:
            return last_area, d, num

        elif index == -2:
            next_index = ctx.map.connections[num][d][0]
            if next_index == last_area:
                next_index = ctx.map.connections[num][d][1]
            return next_index, d, num

        else:
            return ctx.map.connections[num][d][index], d, num

    except Exception:
        print("\nRouting failure.")
        print("num =", num)
        print("last_area =", last_area)
        print("dir =", dir)
        print("direction =", direction)
        print("d =", d)
        print("index =", index)
        raise

def evaluate_rules(ctx, node, num, dir, last_area):
    rules = node.get("rules", [])

    for rule in rules:
        result = RULES[rule](ctx, node, num, dir, last_area)
        if result is not None:
            return result

    return None

def rule_random_encounter(ctx, node, num, dir, last_area):
    if random.randint(1, 100) > node["target"]:
        return skip(ctx, num, dir)
    ctx.map.random_encounter_triggered = True

RULES["random_encounter"] = rule_random_encounter

def rule_teleport_only(ctx, node, num, dir, last_area):
    if not ctx.arrival.teleport:
        return skip(ctx, num, dir)

    # consume teleport state
    ctx.arrival.teleport = False

RULES["teleport_only"] = rule_teleport_only

def rule_one_way_to(ctx, node, num, dir, last_area):
    if last_area in ctx.map.connections[num]["forward"]:
        return skip(ctx, num, dir)

RULES["one_way_to"] = rule_one_way_to

# --------------------------------------------------
# MAIN TRAVERSAL LOOP
# --------------------------------------------------

def main(ctx):
    print("\nYou wake up in a dark forest.")

    current = 0
    direction = "forward"
    last_area = 0

    while current is not None and 0 <= current < len(ctx.map.areas):
        if current == 0:
            direction = "forward"

        current, direction, last_area = area(
            ctx, current, direction, last_area
        )