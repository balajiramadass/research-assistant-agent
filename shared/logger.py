from datetime import datetime

class StepLogger:
    def __init__(self):
        self.events = []

    def log(self, stage: str, detail: str):
        self.events.append({
            "stage": stage,
            "detail": detail,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

    def get_events(self):
        return self.events

    def clear(self):
        self.events = []