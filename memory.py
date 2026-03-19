from datetime import datetime

class Memory:
    def __init__(self, max_size=20):
        self.max_size = max_size
        self.events = []  # 每个事件为字典：{"time":..., "type":..., "content":..., "affection_change":...}
    
    def add_event(self, event_type, content, affection_change=0):
        self.events.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type": event_type,
            "content": content,
            "affection_change": affection_change
        })
        if len(self.events) > self.max_size:
            self.events.pop(0)
    
    def get_recent(self, n=None):
        if n is None:
            return self.events
        return self.events[-n:]
    
    def format_for_prompt(self):
        if not self.events:
            return "暂无共同回忆。"
        lines = []
        for e in self.events[-self.max_size:]:
            lines.append(f"[{e['time']}] {e['type']}: {e['content']} (好感变化:{e['affection_change']:+d})")
        return "\n".join(lines)
    
    def to_dict(self):
        return {
            "max_size": self.max_size,
            "events": self.events
        }
    
    @classmethod
    def from_dict(cls, data):
        mem = cls(data["max_size"])
        mem.events = data["events"]
        return mem