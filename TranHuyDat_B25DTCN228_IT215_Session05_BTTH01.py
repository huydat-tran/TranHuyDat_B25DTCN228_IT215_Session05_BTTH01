from fastapi import FastAPI, HTTPException, status
from typing import Optional
from pydantic import BaseModel, Field

app = FastAPI()

courses = [
    {"id": 1, "code": "PY101", "name": "Python Basic", "duration": 30, "fee": 3000000},
    {
        "id": 2,
        "code": "API101",
        "name": "FastAPI Basic",
        "duration": 24,
        "fee": 2500000,
    },
    {"id": 3, "code": "JV101", "name": "Java Basic", "duration": 40, "fee": 4000000},
]


class CoursePayload(BaseModel):
    code: str
    name: str = Field(..., min_length=1)
    duration: int = Field(gt=0)
    fee: float = Field(ge=0)


@app.post("/courses", status_code=status.HTTP_201_CREATED)
def create_course(payload: CoursePayload):
    is_code_duplicate = any(c.get("code") == payload.code for c in courses)

    if is_code_duplicate:
        raise HTTPException(status_code=400, detail="Course code already exists")

    new_id = 1 if not courses else max(c.get("id", 0) for c in courses) + 1

    new_course = {"id": new_id, **payload.model_dump()}
    courses.append(new_course)

    return {"message": "Tạo khóa học thành công", "data": new_course}


@app.get("/courses")
def get_course(
    keyword: Optional[str] = None,
    min_fee: Optional[float] = None,
    max_fee: Optional[float] = None,
):
    filtered_courses = courses

    if keyword:
        kw = keyword.lower().strip()

        filtered_courses = [
            course
            for course in filtered_courses
            if kw in course.get("name").lower() or kw in course.get("code").lower()
        ]

    if min_fee:
        filtered_courses = [
            course for course in filtered_courses if course.get("fee") >= min_fee
        ]

    if max_fee:
        filtered_courses = [
            course for course in filtered_courses if course.get("fee") <= max_fee
        ]

    return {"message": "Lấy danh sách khóa học thành công", "data": filtered_courses}


def get_course_by_id(course_id: int):
    return next((c for c in courses if c.get("id") == course_id), None)


@app.get("/courses/{course_id}")
def get_course_detail(course_id: int):
    course = get_course_by_id(course_id)

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return {"message": "Tìm thấy khóa học", "data": course}


@app.put("/courses/{course_id}")
def update_course(course_id: int, payload: CoursePayload):
    target_course = get_course_by_id(course_id)

    if not target_course:
        raise HTTPException(status_code=404, detail="Course not found")

    is_code_duplicate = any(
        c.get("code") == payload.code and c.get("id") != course_id for c in courses
    )

    if is_code_duplicate:
        raise HTTPException(status_code=400, detail="Course code already exists")

    target_course.update(payload.model_dump())

    return {"message": "Cập nhật thành công", "data": target_course}


@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    target_course = get_course_by_id(course_id)

    if not target_course:
        raise HTTPException(status_code=404, detail="Course not found")

    courses.remove(target_course)

    return {"message": "Xóa khóa học thành công"}
