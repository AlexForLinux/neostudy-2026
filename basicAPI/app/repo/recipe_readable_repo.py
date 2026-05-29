import json
import os
from typing import List, Generator, Tuple
from app.my_schemas.identified import Identified
from app.repo.from_json_to_repo  import FromJson2Repo
from app.my_schemas.local_recipe import LocalRecipe

class RecipeReadbleRepo(FromJson2Repo): #implements ReadableRepo
    def __init__(self, path2db: str, path2json: str):
        super().__init__(path2db, path2json)

    def _exists(self) -> bool:
        conn = self._get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, ("recipes",))

            return cursor.fetchone() is not None
        
        finally:
            conn.close()
        
    def __load_batch(self, source, batch_size=128) -> Generator[List[LocalRecipe]]:
        batch = []

        for filename in os.listdir(source):
            if filename.endswith(".json"):
                file_path = os.path.join(source, filename)

                with open(file_path, "r", encoding="utf-8") as f:
                    doc = LocalRecipe(**json.load(f))
                    batch.append(doc)

                if (len(batch) >= batch_size):
                    yield batch
                    batch = []

        if batch:
            yield batch

    def _load_docs(self):
        conn = self._get_connection()
        
        try:
            cursor = conn.cursor()

            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT
            )
            """)

            for batch in self.__load_batch(self._path2json):
                rows = [(row.model_dump_json(),) for row in batch]

                cursor.executemany(
                    f"INSERT INTO recipes (data) VALUES (?)",
                    rows
                )

            conn.commit()
            
        except Exception  as e:
            conn.rollback()
            conn.close()

    def get_all(self) -> Generator[Identified[LocalRecipe]]:
        conn = self._get_connection()
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, data FROM recipes")

            for rid, data in cursor:
                yield Identified[LocalRecipe](
                    id=rid, 
                    data=LocalRecipe(**json.loads(data))
                )
                
        finally:
            conn.close()

    def get_by_ids(self, ids: Tuple[int]) -> List[Identified[LocalRecipe]] :
        conn = self._get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id, data FROM recipes WHERE id IN ({",".join("?" for _ in ids)})",
                ids
            )

            rows = cursor.fetchall()

            return [Identified[LocalRecipe](
                id=rid, 
                data=LocalRecipe(**json.loads(data))
            ) for rid, data in rows]
        
        finally:
            conn.close()