# core/game_context.py

class MapState:
    def __init__(self):
        self.areas = []
        self.endpoints = []
        self.connections = {}
        self.visited = []
        self.random_encounter_triggered = False


class Flags:
    def __init__(self):
        self.fork_found = False


class ArrivalState:
    def __init__(self):
        self.teleport = False


class GameContext:
    def __init__(self):
        self.map = MapState()
        self.flags = Flags()
        self.arrival = ArrivalState()
        self.player = None
        self.game = None