class Status:
    def __init__(self, name, duration, handlers=None, data=None):
        self.name = name
        self.duration = duration
        self.handlers = handlers or {}
        self.data = data or {}

    def reduce_duration(self, ctx, val = 1):
        self.duration -= val
        if self.duration <= 0:
            handler = self.handlers.get("on_0_duration")
            if handler:
                handler(ctx)