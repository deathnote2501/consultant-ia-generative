from typing import Optional, List, Dict
from uuid import UUID # Only if uuid is chosen for UserRead.id, otherwise int
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int # As per prompt, but will use UUID if preferred later. For now, int.

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseRead(CourseBase):
    id: int

class SlideBase(BaseModel):
    course_id: int
    order_index: int
    template_type: str
    content_json: Dict
    specific_prompt: Optional[str] = None
    suggested_messages_json: Optional[List[str]] = None

class SlideCreate(SlideBase):
    pass

class SlideRead(SlideBase):
    id: int
