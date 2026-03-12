# core/area_utils.py

# --------------------------------------------------
# MOVEMENT COMMANDS
# --------------------------------------------------

def forward(option: int = 0):
    """
    Player chooses to move forward.
    option selects which forward path when multiple exist.
    """
    return "forward", option

def back(option: int = 0):
    """
    Player chooses to move backward.
    option selects which back path when multiple exist.
    """
    return "back", option


# --------------------------------------------------
# COMMON FLOW HELPERS
# --------------------------------------------------

def run_away():
    """
    Standard escape behavior used by encounters.
    Keeps messaging consistent across areas.
    """
    print("You somehow manage to escape back the way you came.")
    return back()

def press_enter_to_continue():
    """
    Standard pause used after encounters.
    """
    input("\nPress enter to continue...")