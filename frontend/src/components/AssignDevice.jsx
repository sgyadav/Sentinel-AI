import { useEffect, useState } from "react";
import api from "../services/api";

function AssignDevice() {
  const [employees, setEmployees] = useState([]);
  const [devices, setDevices] = useState([]);
  const [assignment, setAssignment] = useState({
    employee_id: "",
    hostname: "",
  });

  const loadEmployees = async () => {
    const response = await api.get("/employee/");
    setEmployees(response.data);
  };

  const loadDevices = async () => {
    const response = await api.get("/device/");
    setDevices(response.data);
  };

  useEffect(() => {
    loadEmployees();
    loadDevices();
  }, []);

  const assign = async () => {
    try {
      await api.post("/assign-device", assignment);
      alert("Device assigned");
    } catch (error) {
      console.log(error);
      alert("Assignment failed");
    }
  };

  return (
    <div
      style={{
        background: "white",
        padding: "20px",
        borderRadius: "10px",
        boxShadow: "0 2px 8px rgba(0,0,0,.2)",
        marginBottom: "25px",
      }}
    >
      <h2>Assign Device</h2>

      <select
        value={assignment.employee_id}
        onChange={(e) =>
          setAssignment({
            ...assignment,
            employee_id: e.target.value,
          })
        }
      >
        <option value="">Select Employee</option>

        {employees.map((employee) => (
          <option key={employee.employee_id} value={employee.employee_id}>
            {employee.employee_id} - {employee.name}
          </option>
        ))}
      </select>

      <br />
      <br />

      <select
        value={assignment.hostname}
        onChange={(e) =>
          setAssignment({
            ...assignment,
            hostname: e.target.value,
          })
        }
      >
        <option value="">Select Device</option>

        {devices.map((device) => (
          <option key={device.hostname} value={device.hostname}>
            {device.hostname}
          </option>
        ))}
      </select>

      <br />
      <br />

      <button onClick={assign}>Assign Device</button>
    </div>
  );
}

export default AssignDevice;
