from sqlalchemy.orm import Session
from sqlalchemy import or_

from db.models import EmployeeDB


# =====================================================
# CREATE EMPLOYEE
# =====================================================

def create_employee(db: Session, employee):

    db_employee = EmployeeDB(
        employee_id=employee.employee_id,
        name=employee.name,
        department=employee.department,
        designation=employee.designation,
        email=employee.email,
        risk_score=0
    )

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return db_employee


# =====================================================
# GET ALL EMPLOYEES
# =====================================================

def get_all_employees(db: Session):

    return db.query(EmployeeDB).all()


# =====================================================
# GET SINGLE EMPLOYEE
# =====================================================

def get_employee(db: Session, employee_id: str):

    return (
        db.query(EmployeeDB)
        .filter(EmployeeDB.employee_id == employee_id)
        .first()
    )


# =====================================================
# UPDATE EMPLOYEE
# =====================================================

def update_employee(
    db: Session,
    employee_id: str,
    employee
):

    db_employee = (
        db.query(EmployeeDB)
        .filter(EmployeeDB.employee_id == employee_id)
        .first()
    )

    if not db_employee:
        return {
            "success": False,
            "message": "Employee Not Found"
        }

    db_employee.name = employee.name
    db_employee.department = employee.department
    db_employee.designation = employee.designation
    db_employee.email = employee.email

    db.commit()
    db.refresh(db_employee)

    return db_employee


# =====================================================
# DELETE EMPLOYEE
# =====================================================

def delete_employee(
    db: Session,
    employee_id: str
):

    db_employee = (
        db.query(EmployeeDB)
        .filter(EmployeeDB.employee_id == employee_id)
        .first()
    )

    if not db_employee:
        return {
            "success": False,
            "message": "Employee Not Found"
        }

    db.delete(db_employee)
    db.commit()

    return {
        "success": True,
        "message": "Employee Deleted Successfully"
    }


# =====================================================
# SEARCH EMPLOYEE
# =====================================================

def search_employee(
    db: Session,
    keyword: str
):

    return (
        db.query(EmployeeDB)
        .filter(
            or_(
                EmployeeDB.employee_id.contains(keyword),
                EmployeeDB.name.contains(keyword),
                EmployeeDB.department.contains(keyword),
                EmployeeDB.designation.contains(keyword),
                EmployeeDB.email.contains(keyword)
            )
        )
        .all()
    )