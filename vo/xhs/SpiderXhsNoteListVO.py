from pydantic import BaseModel


class SpiderXhsNoteListVO(BaseModel):
    notes: list = None
    total_count: int = None