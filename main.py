from fastapi import FastAPI, HTTPException, Request
from typing import Dict
from models import Student
from ai_summary import generate_student_summary
from threading import Lock
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

students: Dict[int, Student] = {}
next_id = 1
lock = Lock()

@app.get("/")
def home():
    return "Base route"


# Create student
@app.post("/students", response_model=Student, status_code=201)
def create_student(student: Student):
    global next_id
    with lock:
        if student.id is None:
            student.id = next_id
            next_id += 1
        elif student.id in students:
            raise HTTPException(status_code=409,detail=f"Student ID {student.id} already exists")
        
        students[student.id] = student
    return student

# Get all students
@app.get("/students", response_model=list[Student])
def get_all_students():
    with lock:
        return list(students.values())

# Get one student
@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    with lock:
        student = students.get(student_id)
        if not student:
            raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")
        return student

# Update student
@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, updated: Student):
    with lock:
        if student_id not in students:
            raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")

        current = students[student_id]
       
        current.name = updated.name or current.name
        current.age = updated.age or current.age
        current.email = updated.email or current.email
        students[student_id] = current
        return current

# Delete student
@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    with lock:
        if student_id not in students:
            raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")
        del students[student_id]
    return

# Generate AI summary
@app.get("/students/{student_id}/summary")
def student_summary(student_id: int):
    with lock:
        student = students.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")

    summary = generate_student_summary(student)
    return {"student_id": student_id, "summary": summary}


# Invalid input exceptions status code : 422
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Invalid input data",
            "details": exc.errors()
        }
    )

# status code: 404, 400
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"Page '{request.url.path}' not found",
                "redirect_url": "/"
            }
        )
    elif exc.status_code == 400:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": exc.detail
            }
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )

# status code : 500
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Unexpected error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "details": str(exc)  
        }
    )