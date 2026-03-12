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