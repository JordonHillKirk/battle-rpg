# =========================
# Entity / Stat Keys
# =========================
NAME = "name"

HP = "hp"
MAX_HP = "max_hp"

MP = "mp"
MAX_MP = "max_mp"

ATTACK = "attack"
DEFENSE = "defense"
MAGIC = "magic"

PRONOUN_SUBJECT = "subject"
PRONOUN_OBJECT = "object"
PRONOUN_POSSESSIVE = "possessive"


# =========================
# Ability Dictionary Keys
# =========================
ID = "id"
COST = "cost"
HOVER = "hover"
VALUE = "value"
TYPE = "type"

DAMAGE = "damage"
HEAL = "heal"
FUNC = "func"
HITS = "hits"


# =========================
# Ability Type Keys
# =========================
TYPE_ATTACK = "attack"
TYPE_ITEM = "item"
TYPE_SPELL = "spell"
TYPE_SPECIAL = "special"


# =========================
# Ability Cost Keys
# =========================
COST_MP = "mp"
COST_ITEM = "item"


# =========================
# Status Tags
# =========================
BUFF = "buff"
DEBUFF = "debuff"
CLEANSABLE = "cleansable"
PERMANENT = "permanent"


# =========================
# Status Event Hooks
# =========================
ON_APPLY = "on_apply"

ON_TURN_START = "on_turn_start"
ON_TURN_END = "on_turn_end"

ON_PRE_DAMAGE = "on_pre_damage"
ON_POST_DAMAGE = "on_post_damage"

ON_0_DURATION = "on_0_duration"
ON_BATTLE_END = "on_battle_end"


# =========================
# Menu States
# =========================
MENU_NONE = ""

MENU_MAIN = "main"
MENU_ATTACK = "attack"
MENU_ITEMS = "items"
MENU_SPELLS = "spells"
MENU_SPECIAL = "special"
MENU_QUIT = "quit"

MENU_DEBUG = "debug"


# =========================
# Action Types
# =========================
ACTION_ATTACK = "attack"
ACTION_ITEM = "item"
ACTION_SPELL = "spell"
ACTION_SPECIAL = "special"


# =========================
# Turn States
# =========================
PLAYER = "player"
ENEMY = "enemy"


# =========================
# Button Colors
# =========================
SPECIAL_COLOR = (50, 150, 150)
DEFAULT_COLOR = (50, 50, 150)


# =========================
# Window Sizing
# =========================
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
DEBUG_PANEL_WIDTH = 200
GAME_WIDTH = WINDOW_WIDTH - DEBUG_PANEL_WIDTH