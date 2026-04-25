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
            handler = self.handlers.get("on_0_duration")
            if handler:
                handler(ctx, self)
            