# areas/__init__.py

# ---- starting area ----
from .start import start

# ---- normal encounters ----
from .encounters import (
    goblin_toll,
    bandits,
)

# ---- merchants / random encounters ----
from .merchants import (
    traveling_merchant,
    traveling_merchant2,
    traveling_merchant4,
    shop,
)

# ---- cave + dragon chain ----
from .cave import (
    cave,
    dragon,
    dead_dragon,
    elder_dragon,
    fight_elder_dragon,
)

# ---- forks / branching ----
from .fork import (
    fork,
    actual_fork,
)

# ---- teleport system ----
from .teleport import (
    teleporter_trap,
    teleporter_trap_landing,
)

# ---- endpoints ----
from .endpoints import (
    oasis,
    dead_end,
)

# ---- one way ----
from .garden_gate import (
    garden_gate,
    back_of_gate
)

# ---- password gate ----
from .password_gate import (
    create_password_gate_areas,
    position_password_gate,
    validate_password_gate_access,
    password_gate
)

# ---- orc coliseum ----
from .coliseum import coliseum_path