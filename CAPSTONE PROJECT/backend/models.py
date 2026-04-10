from pydantic import BaseModel
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str
    location: Optional[str] = None
    language: Optional[str] = "en"

class QueryResponse(BaseModel):
    reply: str
    sources: Optional[List[str]] = []

class ImageUploadResponse(BaseModel):
    disease_detected: str
    confidence: float
    recommendation: str

class DashboardInsights(BaseModel):
    disease_alerts: List[str]
    yield_predictions: List[str]
    recommendations: List[str]

class CommentBase(BaseModel):
    author: str
    content: str
    time: Optional[str] = "Just now"

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: str

class PostBase(BaseModel):
    author: str
    location: str
    content: str
    time: Optional[str] = "Just now"

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: str
    likes: int = 0
    comments: int = 0
    active: bool = True
    comment_list: List[Comment] = []
