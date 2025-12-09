import json, os

class JsonStore:
    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.path):
            self._write([])
        self.data = self._read()

    def _read(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.data = data

    def list_all(self):
        return self.data

    def create(self, item):
        self.data.append(item)
        self._write(self.data)

    def update(self, key, value, fields):
        for it in self.data:
            if it.get(key) == value:
                it.update(fields)
                break
        self._write(self.data)

    def delete(self, key, value):
        self.data = [it for it in self.data if it.get(key) != value]
        self._write(self.data)
