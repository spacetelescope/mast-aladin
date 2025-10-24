class SyncManager():
    def __init__(self):
        self.source = None
        self.destination = None
        self.aspects = ["center", "fov", "rotation"]

    def _callback(self, caller):
        self.destination.sync_to(self.source, self.aspects)

    def start_real_time_sync(self, source, destination, aspects):
        # ensure we stop any previously configured real time sync
        self.stop_real_time_sync()

        self.source = source
        self.destination = destination
        self.aspects = aspects

        # call the sync method once manually to align the views
        self.destination.sync_to(self.source, self.aspects)

        # add a callback to the source to update the destination when the view changes
        self.source.add_callback(self._callback)

    def stop_real_time_sync(self):
        prev_source = self.source
        self.source = None
        self.destination = None
        self.aspects = None

        if prev_source:
            prev_source.remove_callback(self._callback)
