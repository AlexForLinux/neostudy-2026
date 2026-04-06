import sqlite3
import json
import os

class RecipeRepo:
    def __init__(self, path2db, path2recipe):
        self.__path2db = path2db
        self.__path2recipe = path2recipe

        if (not self._recipe_exists()):
            self._load_recipes()

    def _get_connection(self):
        return sqlite3.connect(self.__path2db)
    
    def _recipe_exists(self):
        conn = self._get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, ('recipe',))

            return cursor.fetchone() is not None
        
        finally:
            conn.close()
        
    def _load_batch(self, source, batch_size=128):
        batch = []

        for filename in os.listdir(source):
            if filename.endswith(".json"):
                file_path = os.path.join(source, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    batch.append(data)

                if (len(batch) >= batch_size):
                    yield batch
                    batch = []

        if batch:
            yield batch

    def _load_recipes(self):
        conn = self._get_connection()
        
        try:
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT
            )
            """)

            for batch in self._load_batch(self.__path2recipe):
                rows = [
                    (json.dumps(r, ensure_ascii=False),) for r in batch
                ]

                cursor.executemany(
                    "INSERT INTO recipes (data) VALUES (?)",
                    rows
                )

            conn.commit()
            
        except:
            conn.rollback()
            conn.close()

    def read_all_recipes(self):
        conn = self._get_connection()
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, data FROM recipes")

            for rid, data in cursor:
                recipe = json.loads(data)
                yield rid, recipe
                
        finally:
            conn.close()

    def read_recipes_by_ids(self, ids):
        conn = self._get_connection()

        try:
            cursor = conn.cursor()
            placeholder = ",".join("?" for _ in ids)
            cursor.execute(
                f"SELECT id, data FROM recipes WHERE id IN ({placeholder})",
                tuple(ids)
            )

            rows = cursor.fetchall()
            return {rid: json.loads(data) for rid, data in rows}
        
        finally:
            conn.close()

#TODO: сделать универсальный прототип Repo: подключение, проверка существования