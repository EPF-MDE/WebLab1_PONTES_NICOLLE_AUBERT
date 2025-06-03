# app/exceptions.py

from fastapi import HTTPException

class ItemNotFoundError(HTTPException):
    def __init__(self, item_id: int):
        super().__init__(status_code=404, detail=f"Item with id {item_id} not found")
