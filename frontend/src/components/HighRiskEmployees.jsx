import { useEffect, useState } from "react";
import api from "../services/api";

function HighRiskEmployees() {

    const [employees, setEmployees] = useState([]);

    const load = async () => {

        try {

            const res = await api.get("/admin-dashboard");

            const highRisk = res.data.employees
                .filter(emp => emp.risk_score >= 50)
                .sort((a, b) => b.risk_score - a.risk_score)
                .slice(0, 5);

            setEmployees(highRisk);

        } catch (err) {

            console.log(err);

        }

    };

    useEffect(() => {

        load();

        const timer = setInterval(load, 3000);

        return () => clearInterval(timer);

    }, []);

    const getColor = (risk) => {

        if (risk >= 80) return "#dc2626";

        if (risk >= 60) return "#f59e0b";

        return "#16a34a";

    };

    return (

        <div
            style={{
                background: "white",
                padding: "20px",
                marginTop: "30px",
                borderRadius: "10px",
                boxShadow: "0 3px 10px rgba(0,0,0,.2)"
            }}
        >

            <h2>⚠ Top High Risk Employees</h2>

            {employees.length === 0 &&

                <p>No High Risk Employees</p>

            }

            {employees.map(emp => (

                <div
                    key={emp.employee_id}
                    style={{
                        padding: "15px",
                        borderBottom: "1px solid #ddd"
                    }}
                >

                    <b>{emp.name}</b>

                    <br />

                    Employee ID : {emp.employee_id}

                    <br />

                    Department : {emp.department}

                    <br />

                    Risk Score :

                    <span
                        style={{
                            color: getColor(emp.risk_score),
                            fontWeight: "bold",
                            marginLeft: "8px"
                        }}
                    >
                        {emp.risk_score}
                    </span>

                </div>

            ))}

        </div>

    );

}

export default HighRiskEmployees;