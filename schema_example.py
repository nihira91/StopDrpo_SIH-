from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
class User(BaseModel):
    student_id: Annotated[str, Field(min_length=5, max_length=5, discription="Student ID must be of length 5", example="S1234")]
    name: Annotated[str, Field(min_length=1, max_length=50, description="Name of the student", example="yee rane")]
    branch: Annotated[Literal["Computer Science Engineering",
                            "Information Technology",
                            "Electronics and Communication Engineering",
                            "Electrical Engineering",
                            "Mechanical Engineering",
                            "Civil Engineering",
                            "Chemical Engineering",
                            "Biotechnology",
                            "Production and Industrial Engineering",
                            "Mathematics and Computing"],
                            Field(discription="Branch of the student", example="Computer Science Engineering")
                            ]
    year: Annotated[int, Field(ge=1, le=4, description="Year of study", example=3)]
    @computed_field
    @property
    def admission_year(self) -> int:
        return 2025 - self.year
    age: Annotated[int, Field(ge=17, le=30, description="Age of the student", example=20)]
    avg_attendance_overall: Annotated[float, Field(ge=0, le=100, description="Average attendance overall in percentage", example=85.5)]
    last_4_week_attendance: Annotated[float, Field(ge=0, le=100, description="Average attendance in last 4 weeks in percentage", example=90.0)]
    current_sgpa: Annotated[float, Field(ge=0, le=10, description="Current semester GPA", example=8.5)]
    cgpa: Annotated[float, Field(ge=0, le=10, description="Cumulative GPA", example=8.0)]
    backlog_prev: Annotated[int, Field(ge=0, le=20, description="Number of backlogs in previous semesters", example=2)]
    backlog_curr: Annotated[int, Field(ge=0, le=20, description="Number of backlogs in current semester", example=1)]
    fee_status: Annotated[Literal["paid", "overdue"], Field(description="Fee status of the student", example="Paid")]
    lms_logins_30d: Annotated[int, Field(ge=0, le=100, description="Number of LMS logins in the last 30 days", example=25)]

    from fastapi import FastAPI
import numpu as np
app = FastAPI()

def encode_branch(branch: str):
    branch_array = {
    "Computer Science Engineering": [0., 0., 1., 0., 0., 0., 0., 0., 0.],
    "Information Technology": [0., 0., 0., 0., 0., 1., 0., 0., 0.],
    "Electronics and Communication Engineering": [0., 0., 0., 0., 1., 0., 0., 0., 0.],
    "Electrical Engineering": [0., 0., 0., 1., 0., 0., 0., 0., 0.],
    "Mechanical Engineering": [0., 0., 0., 0., 0., 0., 0., 1., 0.],
    "Civil Engineering": [0., 1., 0., 0., 0., 0., 0., 0., 0.],
    "Chemical Engineering": [1., 0., 0., 0., 0., 0., 0., 0., 0.],
    "Biotechnology": [0., 0., 0., 0., 0., 0., 0., 0., 0.],
    "Production and Industrial Engineering": [0., 0., 0., 0., 0., 0., 0., 0., 1.],
    "Mathematics and Computing": [0., 0., 0., 0., 0., 0., 1., 0., 0.]
    }
    return np.array(branch_array[branch])

@app.post("/predict")
def predict(student : User):
    branch_encoded = encode_branch(student.branch)
    print(encoded)