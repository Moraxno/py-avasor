import psutil

class StatusRole:
    def __init__(self):
        pass
    
    def handle_message(self, msg: str):
        if msg == "cpu":
            return psutil.cpu_percent(interval=1)
        elif msg == "close":
            raise RuntimeError
        else:
            return "nope"
        
    