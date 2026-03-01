# jarvis_ai/core/memory.py
import json
import os
import time
import uuid
import threading
from collections import deque

class Memory:
    def __init__(self, file="memory.json"):
        self.file = file
        self.data = {}
        self.on_change = None  # Callback fired when memory changes
        self._last_mtime = 0
        self._load()
        
        # Start file watcher thread
        self._watcher_thread = threading.Thread(target=self._watch_file, daemon=True)
        self._watcher_thread.start()

    def _watch_file(self):
        """Background thread to watch for external changes to memory.json."""
        while True:
            time.sleep(2)
            if os.path.exists(self.file):
                try:
                    current_mtime = os.stat(self.file).st_mtime
                    if self._last_mtime > 0 and current_mtime > self._last_mtime:
                        print("🔄 memory.json changed externally, reloading...")
                        self._load(notify=True)
                except Exception as e:
                    pass

    def _notify(self):
        """Invoke the on_change callback if registered."""
        if self.on_change:
            try:
                self.on_change()
            except Exception as e:
                print(f"⚠️ Error in memory on_change callback: {e}")

    def _load(self, notify=False):
        if os.path.exists(self.file):
            try:
                with open(self.file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.data = data
                    else:
                        print("⚠️ Memory file malformed (not a dict). Resetting.")
                        self.data = {}
                self._last_mtime = os.stat(self.file).st_mtime
            except Exception as e:
                print(f"⚠️ Error loading memory: {e}")
                self.data = {}
        
        # Ensure default structures exist
        if "history" not in self.data:
            self.data["history"] = []
        if "trash" not in self.data:
            self.data["trash"] = []

        if notify:
            self._notify()

    def _save(self):
        try:
            with open(self.file, "w") as f:
                json.dump(self.data, f, indent=2)
            self._last_mtime = os.stat(self.file).st_mtime
        except Exception as e:
            print(f"⚠️ Error saving memory: {e}")

    # ✅ GENERAL STORAGE
    def set(self, key, value):
        self.data[key] = value
        self._save()
        self._notify()

    def get(self, key):
        return self.data.get(key)

    # ✅ CONVERSATION HISTORY (With IDs & Timestamps)
    def remember(self, item):
        # item is typically {"user": "...", "jarvis": "...", "provider": "...", "model": "...", ...}
        
        # Add metadata if missing
        if "id" not in item:
            item["id"] = str(uuid.uuid4())
        if "timestamp" not in item:
            item["timestamp"] = time.time()
            
        self.data["history"].append(item)
        
        # Keep manageable size (last 200 items)
        if len(self.data["history"]) > 200:
            self.data["history"].pop(0)
            
        self._save()
        self._notify()

    def get_history(self, limit=50):
        # Return reversed (newest first)
        return self.data["history"][::-1][:limit]

    def get_conversation(self, conversation_id):
        for item in self.data["history"]:
            if item.get("id") == conversation_id:
                return item
        return None

    # ✅ TRASH MANAGEMENT
    def move_to_trash(self, conversation_id):
        history = self.data["history"]
        for i, item in enumerate(history):
            if item.get("id") == conversation_id:
                # Remove from history
                removed_item = history.pop(i)
                # Add deletion metadata
                removed_item["deleted_at"] = time.time()
                # Add to trash
                self.data["trash"].insert(0, removed_item) # Newest deleted first
                self._save()
                self._notify()
                return True
        return False

    def restore_from_trash(self, conversation_id):
        trash = self.data["trash"]
        for i, item in enumerate(trash):
            if item.get("id") == conversation_id:
                # Remove from trash
                restored_item = trash.pop(i)
                # Remove deletion metadata
                if "deleted_at" in restored_item:
                    del restored_item["deleted_at"]
                # Add back to history
                self.data["history"].append(restored_item)
                # Sort history by timestamp to ensure correct order
                self.data["history"].sort(key=lambda x: x.get("timestamp", 0))
                self._save()
                self._notify()
                return True
        return False

    def delete_permanently(self, conversation_id):
        trash = self.data["trash"]
        for i, item in enumerate(trash):
            if item.get("id") == conversation_id:
                trash.pop(i)
                self._save()
                self._notify()
                return True
        return False

    def empty_trash(self):
        self.data["trash"] = []
        self._save()
        self._notify()
        return True

    def get_trash(self):
        return self.data["trash"]

    # ✅ LEGACY SUPPORT (Deprecate if safe)
    def get_last(self, n=4):
        return self.data.get("history", [])[-n:]
