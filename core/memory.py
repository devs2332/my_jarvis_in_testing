# jarvis_ai/core/memory.py
import json
import os
from collections import deque

class Memory:
    def __init__(self, file="memory.json"):
        self.file = file
        self.data = {}
        self.history = deque(maxlen=10)  # for old code compatibility
        self._load()

    def _load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.data = data
                    else:
                        print("⚠️ Memory file malformed (not a dict). Resetting.")
                        self.data = {}
            except Exception as e:
                print(f"⚠️ Error loading memory: {e}")
                self.data = {}

    def _save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=2)

    # ✅ NEW MEMORY (Phase 4)
    def set(self, key, value):
        self.data[key] = value
        self._save()

    def get(self, key):
        return self.data.get(key)

    # ✅ OLD MEMORY SUPPORT (Phase 3 / old brain.py)
    def remember(self, item):
        # self.history.append(item) # Old transient way
        
        if "history" not in self.data:
            self.data["history"] = []
            
        self.data["history"].append(item)
        
        # Keep manageable size (last 20 items)
        if len(self.data["history"]) > 20:
            self.data["history"].pop(0)
            
        self._save()

    def get_last(self, n=4):
        return self.data.get("history", [])[-n:]
