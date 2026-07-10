import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import api from "../services/api";
import RegisterEmployee from "../components/RegisterEmployee";

function Employees() {

  const [employees, setEmployees] = useState([]);

  const loadEmployees = async () => {
    try {

      const response = await api.get("/admin-dashboard");

      setEmployees(response.data.employees);

    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {

    loadEmployees();

    const timer = setInterval(loadEmployees, 3000);

    return () => clearInterval(timer);

  }, []);

  return (
    <>
      <Sidebar />
      <Topbar />

      <div
        style={{
          marginLeft: "260px",
          marginTop: "90px",
          padding: "30px",
        }}
      >
        <h1>👥 Employee Monitoring Center</h1>

        <RegisterEmployee />

        <table
          style={{
            width: "100%",
            marginTop: "20px",
            borderCollapse: "collapse",
            background: "white",
            boxShadow: "0px 2px 8px rgba(0,0,0,.2)",
          }}
        >
          <thead
            style={{
              background: "#1e293b",
              color: "white",
            }}
          >
            <tr>
              <th style={{ padding: "12px" }}>Employee ID</th>
              <th>Name</th>
              <th>Department</th>
              <th>Designation</th>
              <th>Assigned Device</th>
              <th>Risk Score</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {employees.map((emp) => (
              <tr
                key={emp.employee_id}
                style={{
                  textAlign: "center",
                  borderBottom: "1px solid #ddd",
                }}
              >
                <td>{emp.employee_id}</td>
                <td>{emp.name}</td>
                <td>{emp.department}</td>
                <td>{emp.designation}</td>

                <td>
                  {emp.devices.length > 0
                    ? emp.devices.join(", ")
                    : "Not Assigned"}
                </td>

                <td>{emp.risk_score}</td>

                <td>
                  {emp.risk_score > 80
                    ? "🔴 High Risk"
                    : emp.risk_score > 40
                    ? "🟡 Medium"
                    : "🟢 Safe"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default Employees;