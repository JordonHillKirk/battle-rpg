from core.constants import ON_0_DURATION

class Status:
    def __init__(self, id, name, duration, handlers=None, data=None, tags=None):
        self.id = id
        self.name = name
        self.duration = duration
        self.handlers = handlers or {}
        self.data = data or {}
        self.tags = tags or set()

    def reduce_duration(self, ctx, val = 1):
        self.duration -= val
        if self.duration <= 0:
            handler = self.handlers.get(ON_0_DURATION)
            if handler:
                handler(ctx, self)
            