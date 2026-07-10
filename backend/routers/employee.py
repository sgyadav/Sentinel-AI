from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models import Employee
from services.employee_service import (
    create_employee,
    get_all_employees,
    get_employee,
    update_employee,
    delete_employee,
    search_employee
)

router = APIRouter(
    prefix="/employee",
    tags=["Employees"]
)


# ==========================
# Register Employee
# ==========================

@router.post("/register")
def register_employee(
    employee: Employee,
    db: Session = Depends(get_db)
):
    return create_employee(db, employee)


# ==========================
# Get All Employees
# ==========================

@router.get("/")
def get_employees(
    db: Session = Depends(get_db)
):
    return get_all_employees(db)


# ==========================
# Get Single Employee
# ==========================

@router.get("/{employee_id}")
def get_single_employee(
    employee_id: str,
    db: Session = Depends(get_db)
):
    employee = get_employee(db, employee_id)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee Not Found"
        )

    return employee


# ==========================
# Update Employee
# ==========================

@router.put("/{employee_id}")
def update_employee_details(
    employee_id: str,
    employee: Employee,
    db: Session = Depends(get_db)
):
    return update_employee(
        db,
        employee_id,
        employee
    )


# ==========================
# Delete Employee
# ==========================

@router.delete("/{employee_id}")
def remove_employee(
    employee_id: str,
    db: Session = Depends(get_db)
):
    return delete_employee(
        db,
        employee_id
    )


# ==========================
# Search Employee
# ==========================

@router.get("/search/{keyword}")
def search(
    keyword: str,
    db: Session = Depends(get_db)
):
    return search_employee(
        db,
        keyword
    )