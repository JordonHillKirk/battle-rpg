# core/map_engine.py

import copy
import random

from areas import *
from core.area_utils import press_enter_to_continue
from core.game_context import GameContext

RULES = {}

# --------------------------------------------------
# AREA DEFINITIONS
# --------------------------------------------------

# path generators must equal path consumers.
s = {"name": "Start", "func": start, "type": "start"}

normal_areas = [
    {"name": "Goblin Toll", "func": goblin_toll, "type": "normal"},
    {"name": "Bandits", "func": bandits, "type": "normal"},
    {"name": "Coliseum", "func": coliseum_path, "type": "normal"},
    {"name": "Garden Gate", "func": garden_gate, "type": "one_way_strict"},
    {"name": "Password Gate", "func": password_gate, "type": "normal", "setup": create_password_gate_areas, "post_insert": position_password_gate, "validator": validate_password_gate_access
}
]

random_encounters = [
    {"name": "Traveling Merchant", "func": traveling_merchant, "type": "normal", "target": 25, "rules": ["random_encounter"]},
    {"name": "Traveling Merchant", "func": traveling_merchant, "type": "normal", "target": 25, "rules": ["random_encounter"]},
    {"name": "Traveling Merchant2", "func": traveling_merchant2, "type": "normal", "target": 25, "rules": ["random_encounter"]},
    {"name": "Traveling Merchant2", "func": traveling_merchant2, "type": "normal", "target": 25, "rules": ["random_encounter"]},
    {"name": "Actual Fork", "func": actual_fork, "type": "normal", "target": 10, "rules": ["random_encounter"]},
]

branching_areas = [
    {"name": "Fork", "func": fork, "type": "branch"},
    {"name": "Fork2", "func": fork, "type": "branch"},
]

cave_node = {"name": "Cave", "func": cave, "type": "endpoint"}
endpoint_areas = [
    cave_node,
    {"name": "Oasis", "func": oasis, "type": "endpoint"},
]

dummy_endpoints = [
    {"name": "Dummy Cave", "type": "dummy", "target": cave_node},
]

teleport_landing = {"name": "Teleport Landing", "func": teleporter_trap_landing, "type": "normal", "rules": ["teleport_only"]}

one_way_to_areas = [
    teleport_landing
]

one_way_from_areas = [
    {
        "name": "Teleporter Trap",
        "func": teleporter_trap,
        "type": "one_way_to_normal",
        "target": teleport_landing
    }
]

# --------------------------------------------------
# DEBUG OUTPUT
# --------------------------------------------------

def print_connections(areas, conns):
    with open("map.txt", "w") as f:
        for node in conns:
            f.write(f"area {node}: {areas[node]['name']}\n")
            f.write(f"forward: {conns[node]['forward']}\n")
            f.write(f"back: {conns[node]['back']}\n\n")

def stress_test_maps(ctx, runs=1000):
    failures = {
        "return_to_start": 0,
        "softlock": 0,
        "password_gate": 0,
    }

    for i in range(runs):
        randomize_areas(ctx)

        ok_return = validate_return_to_start(ctx, False)
        ok_softlock = validate_no_softlocks(ctx, False)
        ok_password = validate_password_gate_access(ctx, False)

        if not ok_return:
            failures["return_to_start"] += 1
        elif not ok_softlock:
            failures["softlock"] += 1
        elif not ok_password:
            failures["password_gate"] += 1

        else:
            print(f"Run {i+1}: OK")

    print("\n--- STRESS TEST RESULTS ---")
    print(f"Total runs: {runs}")
    print(f"Return-to-start failures: {failures['return_to_start']}")
    print(f"Softlock failures: {failures['softlock']}")
    print(f"Password gate failures: {failures['password_gate']}")

def visualize_map(ctx):
    areas = ctx.map.areas
    connections = ctx.map.connections

    def dfs(area_index, depth=0, visited=None):
        if visited is None:
            visited = set()

        indent = "  " * depth
        node = areas[area_index]
        name = node["name"]

        forward = connections.get(area_index, {}).get("forward", [])

        # Color / markers
        if node.get("type") == "endpoint":
            marker = "[END]"
        elif node.get("type") == "branch":
            marker = "[BRANCH]"
        elif node.get("type") == "one_way_to_normal":
            marker = "[ONE-WAY]"
        elif node.get("is_password_tree"):
            marker = "[TREE]"
        else:
            marker = ""

        print(f"{indent}- {name} (#{area_index}) {marker}")

        visited.add(area_index)

        for next_area in forward:
            if next_area not in visited:
                dfs(next_area, depth + 1, visited)
            else:
                print(f"{'  ' * (depth + 1)}↪ {areas[next_area]['name']} (#{next_area}) [loop]")

    print("\nMAP VISUALIZATION:")
    dfs(0)
   
def validate_return_to_start(ctx, verbose=True):
    areas = ctx.map.areas
    connections = ctx.map.connections

    reachable = set()
    stack = [0]  # Start node

    while stack:
        current = stack.pop()

        if current in reachable:
            continue

        reachable.add(current)

        # Traverse both directions
        neighbors = (
            connections.get(current, {}).get("forward", []) +
            connections.get(current, {}).get("back", [])
        )

        for n in neighbors:
            if n not in reachable:
                stack.append(n)

    all_nodes = set(connections.keys())
    unreachable = all_nodes - reachable

    if unreachable:
        if verbose:
            print("❌ These areas cannot return to Start:")
            for i in unreachable:
                print(f"- {areas[i]['name']} (#{i})")
            return False
    if verbose:
        print("✅ All areas can reach Start")
    return True

def can_escape_without(ctx, start, blocked):
    areas = ctx.map.areas
    connections = ctx.map.connections

    visited = set()
    stack = [start]

    while stack:
        current = stack.pop()

        if current == 0:
            return True

        if current in visited:
            continue
        visited.add(current)

        neighbors = []

        # forward always allowed
        neighbors.extend(connections.get(current, {}).get("forward", []))

        # back only if current node is not strict one-way
        if areas[current].get("type") != "one_way_strict":
            neighbors.extend(connections.get(current, {}).get("back", []))

        for n in neighbors:
            if n == blocked:
                continue
            stack.append(n)

    return False

def validate_no_softlocks(ctx, verbose=True):
    areas = ctx.map.areas
    connections = ctx.map.connections

    for i, node in enumerate(areas):
        if node.get("type") == "one_way_strict":
            forward_paths = connections[i]["forward"]

            if not forward_paths:
                if verbose:
                    print(f"❌ {node['name']} has no landing.")
                return False

            landing = forward_paths[0]

            if not can_escape_without(ctx, landing, i):
                if verbose:
                    print(
                        f"❌ Softlock risk: "
                        f"{node['name']} → {areas[landing]['name']}"
                    )
                return False
    if verbose:
        print("✅ No softlocks detected")
    return True

# --------------------------------------------------
# MAP RANDOMIZATION
# --------------------------------------------------

def randomize_areas(ctx: GameContext, verbose = False):

    def connect(from_area, to_area, one_way=False):
        to_node = areas[to_area]

        # redirect dummy cave
        if to_node.get("type") == "dummy":
            to_area = next(
                node["index"] for node in areas
                if node["name"] == to_node["target"]["name"]
            )

        connections[from_area]["forward"].append(to_area)

        if not one_way:
            connections[to_area]["back"].append(from_area)

    def find_area_index(a):
        return next(idx for idx, node in enumerate(areas) if node["name"] == a["name"])
    
    generated_areas = []
    generated_endpoints = []

    all_area_defs = (
        normal_areas
        + random_encounters
        + branching_areas
        + one_way_to_areas
        + one_way_from_areas
        + endpoint_areas
    )

    # get additional areas from any areas with setup
    for node in all_area_defs:
        if "setup" in node:
            result = node["setup"](ctx)

            generated_areas.extend(result.get("areas", []))
            generated_endpoints.extend(result.get("endpoints", []))

    while True:
        areas = []
        endpoints = []
        connections = {}
        areas.clear()
        endpoints.clear()
        connections.clear()

        areas.extend(copy.deepcopy(normal_areas))
        areas.extend(copy.deepcopy(random_encounters))
        areas.extend(copy.deepcopy(branching_areas))
        areas.extend(copy.deepcopy(one_way_to_areas))
        areas.extend(copy.deepcopy(generated_areas))

        endpoints.extend(copy.deepcopy(endpoint_areas))
        endpoints.extend(copy.deepcopy(dummy_endpoints))
        endpoints.extend(copy.deepcopy(one_way_from_areas))
        endpoints.extend(copy.deepcopy(generated_endpoints))

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

        # run post-insert hooks
        for node in list(areas):
            if "post_insert" in node:
                node["post_insert"](ctx, areas, node)

        # final endpoint
        areas.append(endpoints[-1])

        # reindex
        for i, node in enumerate(areas):
            node["index"] = i
            if node["type"] != "dummy":
                connections[i] = {"forward": [], "back": []}

        endpoints.sort(key=lambda ep: ep["index"])
        branching_nodes = [n for n in areas if n.get("type") == "branch"]
        branching_nodes.sort(key=lambda n: n["index"])

        # connect graph
        for i, node in enumerate(areas):

            node_type = node.get("type", "normal")

            if node_type == "start":
                connect(i, i + 1)
                connect(i, endpoints[0]["index"] + 1)

            elif node_type == "branch":
                branch_index = branching_nodes.index(node)
                connect(i, i + 1)
                connect(i, endpoints[branch_index + 1]["index"] + 1)

            elif node_type == "one_way_to_normal":
                to_index = find_area_index(node["target"])
                connect(i, to_index, one_way=True)

            elif node_type in ["endpoint", "dummy"]:
                pass

            else:
                connect(i, i + 1)
        
        ctx.map.areas = areas
        ctx.map.endpoints = endpoints
        ctx.map.connections = connections
        validators = [validate_return_to_start, validate_no_softlocks]
        for node in areas:
            if "validator" in node:
                validators.append(node["validator"])

        all_valid = all(v(ctx, verbose = False) for v in set(validators))
        if all_valid:
            break
        if verbose:
            print("Map generation failed.")

    print_connections(areas, connections)
    
    ctx.map.visited = []
    for node in areas:
        if node.get("type") == "dummy":
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

def area(ctx: GameContext, num, dir, last_area):
    side_path = False
    node = ctx.map.areas[num]
    ctx.map.current_area = num
    node_type = node.get("type", "normal")

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
    if node_type == "branch":

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
        "entry_direction": dir,
    }
    kwargs.update(node.get("kwargs", {}))

    direction, index = func(ctx, kwargs)

    # --------------------------------------------------
    # PAUSE HANDLING
    # --------------------------------------------------
    if "random_encounter" not in node.get("rules", []):
        press_enter_to_continue()
    elif ctx.map.random_encounter_triggered:
        ctx.map.random_encounter_triggered = False
        press_enter_to_continue()

    # --------------------------------------------------
    # DIRECTION RESOLUTION
    # --------------------------------------------------
    if node["type"] == "branch" and direction == "forward" and index == 1:
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

if __name__ == "__main__":
    pass