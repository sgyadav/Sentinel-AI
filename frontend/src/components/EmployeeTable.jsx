import { useEffect, useState } from "react";

import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from "@mui/material";

import api from "../services/api";

function EmployeeTable() {

  const [employees, setEmployees] = useState([]);

  const loadEmployees = async () => {

    try {

      const response = await api.get("/admin-dashboard");

      setEmployees(response.data.employees);

    } catch (err) {

      console.log(err);

    }

  };

  useEffect(() => {

    loadEmployees();

    const timer = setInterval(loadEmployees, 3000);

    return () => clearInterval(timer);

  }, []);

  const getRiskColor = (risk) => {

    if (risk >= 70) return "error";

    if (risk >= 40) return "warning";

    return "success";

  };

  return (

    <TableContainer
      component={Paper}
      sx={{ marginTop: 4 }}
    >

      <Table>

        <TableHead>

          <TableRow>

            <TableCell><b>ID</b></TableCell>

            <TableCell><b>Name</b></TableCell>

            <TableCell><b>Department</b></TableCell>

            <TableCell><b>Designation</b></TableCell>

            <TableCell><b>Risk Score</b></TableCell>

          </TableRow>

        </TableHead>

        <TableBody>

          {employees.map((emp) => (

            <TableRow key={emp.employee_id}>

              <TableCell>{emp.employee_id}</TableCell>

              <TableCell>{emp.name}</TableCell>

              <TableCell>{emp.department}</TableCell>

              <TableCell>{emp.designation}</TableCell>

              <TableCell>

                <Chip
                  label={emp.risk_score}
                  color={getRiskColor(emp.risk_score)}
                />

              </TableCell>

            </TableRow>

          ))}

        </TableBody>

      </Table>

    </TableContainer>

  );

}

export default EmployeeTable;