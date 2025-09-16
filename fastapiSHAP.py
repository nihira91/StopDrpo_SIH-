from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
import numpy as np
import joblib
import shap
import pandas as pd
from fastapi.responses import JSONResponse


model = joblib.load("model.pkl")  

app = FastAPI(title="Student Dropout Prediction API")

class User(BaseModel):
    student_id: Annotated[str, Field(min_length=5, max_length=5, description="Student ID must be of length 5", example="S1234")]
    name: Annotated[str, Field(min_length=1, max_length=50, description="Name of the student", example="John Doe")]
    branch: Annotated[Literal[
        "Computer Science Engineering",
        "Information Technology",
        "Electronics and Communication Engineering",
        "Electrical Engineering",
        "Mechanical Engineering",
        "Civil Engineering",
        "Chemical Engineering",
        "Biotechnology",
        "Production and Industrial Engineering",
        "Mathematics and Computing"
    ], Field(description="Branch of the student", example="Computer Science Engineering")]
    
    year: Annotated[int, Field(ge=1, le=4, description="Year of study", example=3)]
    
    @computed_field
    @property
    def admission_year(self) -> int:
        return 2026 - self.year  
    
    age: Annotated[int, Field(ge=17, le=30, description="Age of the student", example=20)]
    avg_attendance_overall: Annotated[float, Field(ge=0, le=100, description="Average attendance overall in percentage", example=85.5)]
    last_4_week_attendance: Annotated[float, Field(ge=0, le=100, description="Average attendance in last 4 weeks in percentage", example=90.0)]
    current_sgpa: Annotated[float, Field(ge=0, le=10, description="Current semester GPA", example=8.5)]
    cgpa: Annotated[float, Field(ge=0, le=10, description="Cumulative GPA", example=8.0)]
    backlog_prev: Annotated[int, Field(ge=0, le=20, description="Number of backlogs in previous semesters", example=2)]
    backlog_curr: Annotated[int, Field(ge=0, le=20, description="Number of backlogs in current semester", example=1)]
    fee_status: Annotated[Literal["paid", "overdue"], Field(description="Fee status of the student", example="paid")]
    lms_logins_30d: Annotated[int, Field(ge=0, le=100, description="Number of LMS logins in the last 30 days", example=25)]

def encode_branch(branch: str):
    """Encode branch using one-hot encoding (excluding first category to avoid dummy variable trap)"""
    branch_mapping = {
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
    return np.array(branch_mapping[branch])

def encode_fee_status(fee_status: str):
    """Encode fee status (excluding first category to avoid dummy variable trap)"""
    fee_mapping = {
        "overdue": [1.],  
        "paid": [0.]      
    }
    return np.array(fee_mapping[fee_status])

def prepare_features(student: User):
    """Prepare feature array in the same order as training data"""

    branch_encoded = encode_branch(student.branch)
    fee_encoded = encode_fee_status(student.fee_status)
    
    numerical_features = np.array([        # Numerical features (in the same order as training)
        student.year,
        student.admission_year,
        student.age,
        student.avg_attendance_overall,
        student.last_4_week_attendance,
        student.current_sgpa,
        student.cgpa,
        student.backlog_prev,
        student.backlog_curr,
        student.lms_logins_30d
    ])
    
    features = np.concatenate([branch_encoded, fee_encoded, numerical_features])
    return features.reshape(1, -1)

@app.get("/")
def read_root():
    return {"message": "Student Dropout Prediction API"}

@app.post("/predict")                        #main prediction endpoint
def predict_dropout(student: User):

        features = prepare_features(student)             #Prepare features
        
        prediction = model.predict(features)[0]
        prediction_proba = model.predict_proba(features)[0]
        
        result = {                                                    #response
            "student_id": student.student_id,
            "student_name": student.name,
            "prediction": {
                "dropout_risk": bool(prediction),
                "dropout_probability": float(prediction_proba[1]),
                "retention_probability": float(prediction_proba[0])
            },
            "risk_level": get_risk_level(prediction_proba[1]),
            "student_info": {
                "branch": student.branch,
                "year": student.year,
                "current_sgpa": student.current_sgpa,
                "cgpa": student.cgpa,
                "last_4_week_attendance": student.last_4_week_attendance,
                "backlog_curr": student.backlog_curr,
                "fee_status": student.fee_status
            }
        }
        
        return result


@app.post("/predict_with_shap")
def predict_with_explanation(student: User):
 
        features = prepare_features(student)
        
     
        prediction = model.predict(features)[0]
        prediction_proba = model.predict_proba(features)[0]
        
    
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(features)
        
    
        feature_names = [
            'Chemical Engineering', 'Civil Engineering', 'Computer Science Engineering',
            'Electrical Engineering', 'Electronics and Communication Engineering',
            'Information Technology', 'Mathematics and Computing', 'Mechanical Engineering',
            'Production and Industrial Engineering', 'Fee Overdue', 'Year', 'Admission Year',
            'Age', 'Avg Attendance Overall', 'Last 4 Week Attendance', 'Current SGPA',
            'CGPA', 'Backlog Previous', 'Backlog Current', 'LMS Logins 30d'
        ]
        
    
        if isinstance(shap_values, list):
            shap_dropout = shap_values[1][0]  # SHAP values for dropout class
        else:
            shap_dropout = shap_values[0]
        
        # Create feature importance explanation
        feature_importance = []
        for i, (name, value, shap_val) in enumerate(zip(feature_names, features[0], shap_dropout)):
            feature_importance.append({
                "feature": name,
                "value": float(value),
                "shap_value": float(shap_val),
                "impact": "increases_dropout_risk" if shap_val > 0 else "decreases_dropout_risk"
            })
        
        # Sort by absolute SHAP value to get most important features
        feature_importance.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        
        result = {
            "student_id": student.student_id,
            "student_name": student.name,
            "prediction": {
                "dropout_risk": bool(prediction),
                "dropout_probability": float(prediction_proba[1]),
                "retention_probability": float(prediction_proba[0])
            },
            "risk_level": get_risk_level(prediction_proba[1]),
            "explanation": {
                "top_risk_factors": feature_importance[:5],
                "all_factors": feature_importance
            },
            "recommendations": get_recommendations(student, feature_importance[:5])
        }
        
        return result

def get_risk_level(dropout_probability: float) -> str:

    if dropout_probability < 0.3:
        return "Low Risk"
    elif dropout_probability < 0.6:
        return "Medium Risk"
    else:
        return "High Risk"

def get_recommendations(student: User, top_factors: list) -> list:

    recommendations = []
    
    for factor in top_factors:
        if factor["impact"] == "increases_dropout_risk" and factor["shap_value"] > 0.01:
            feature_name = factor["feature"]
            
            if "Attendance" in feature_name:
                recommendations.append("Improve class attendance - consider academic counseling")
            elif "SGPA" in feature_name or "CGPA" in feature_name:
                recommendations.append("Focus on academic performance - seek tutoring or study groups")
            elif "Backlog" in feature_name:
                recommendations.append("Clear pending backlogs immediately - prioritize backlog subjects")
            elif "Fee" in feature_name:
                recommendations.append("Resolve fee payment issues - contact finance office")
            elif "LMS" in feature_name:
                recommendations.append("Increase engagement with online learning materials")
    
    if not recommendations:
        recommendations.append("Continue current academic progress - maintain good performance")
    
    return recommendations

