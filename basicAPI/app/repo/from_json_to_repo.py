import sqlite3
from sqlite3 import Connection
import json
import os
from typing import List, Generator, Tuple, TypeVar, Callable
from app.schemas.identified import Identified
from pydantic import BaseModel

class FromJson2Repo:
    def __init__(self, path2db: str, path2json: str):
        self._path2db = path2db
        self._path2json = path2json

        print("PARENT", not self._exists())

        if (not self._exists()):
            self._load_docs()

    def _get_connection(self) -> Connection:
        return sqlite3.connect(self._path2db)
    
    def _exists(self) -> bool:
        pass
        
    def _load_docs(self):
        pass