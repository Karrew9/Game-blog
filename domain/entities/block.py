from pydantic import BaseModel
from enum import Enum

class BlockType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    CODE = "code"
    QUOTE = "quote"

class BlockBase(BaseModel):
    type: BlockType
    content: dict

class TextBlock(BlockBase):
    type: BlockType = BlockType.TEXT
    content: dict = {
        "text": str,
        "align": "left" | "center" | "right"
    }

class ImageBlock(BlockBase):
    type: BlockType = BlockType.IMAGE
    content: dict = {
        "url": str,
        "caption": str,
        "width": int
    }