import { useState } from "react";
import api from "../services/api";

function RegisterEmployee() {
  const [employee, setEmployee] = useState({
    employee_id: "",
    name: "",
    department: "",
    designation: "",
    email: "",
  });

  const registerEmployee = async () => {
    try {
      await api.post("/employee/register", employee);

      alert("Employee registered successfully");

      setEmployee({
        employee_id: "",
        name: "",
        department: "",
        designation: "",
        email: "",
      });
    } catch (error) {
      console.log(error);
      alert("Registration failed");
    }
  };

  return (
    <div
      style={{
        background: "white",
        padding: "20px",
        marginBottom: "25px",
        borderRadius: "10px",
        boxShadow: "0 2px 8px rgba(0,0,0,.2)",
      }}
    >
      <h2>Register Employee</h2>

      <input
        placeholder="Employee ID"
        value={employee.employee_id}
        onChange={(e) =>
          setEmployee({ ...employee, employee_id: e.target.value })
        }
      />

      <br />
      <br />

      <input
        placeholder="Employee Name"
        value={employee.name}
        onChange={(e) => setEmployee({ ...employee, name: e.target.value })}
      />

      <br />
      <br />

      <input
        placeholder="Department"
        value={employee.department}
        onChange={(e) =>
          setEmployee({ ...employee, department: e.target.value })
        }
      />

      <br />
      <br />

      <input
        placeholder="Designation"
        value={employee.designation}
        onChange={(e) =>
          setEmployee({ ...employee, designation: e.target.value })
        }
      />

      <br />
      <br />

      <input
        placeholder="Email"
        value={employee.email}
        onChange={(e) => setEmployee({ ...employee, email: e.target.value })}
      />

      <br />
      <br />

      <button onClick={registerEmployee}>Register Employee</button>
    </div>
  );
}

export default RegisterEmployee;
