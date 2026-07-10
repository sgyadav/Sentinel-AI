import { useEffect, useState } from "react";
import api from "../services/api";

function DashboardCards() {

    const [dashboard, setDashboard] = useState({

        employees: 0,
        devices: 0,
        incidents: 0,
        events: 0,
        critical: 0,
        medium: 0,
        low: 0,
        agents_online: 0,
        threat_feed: "Disconnected"

    });

    const loadDashboard = async () => {

        try {

            const response = await api.get("/dashboard");

            setDashboard(response.data);

        }

        catch (error) {

            console.log(error);

        }

    };

    useEffect(() => {

        loadDashboard();

        const timer = setInterval(loadDashboard, 3000);

        return () => clearInterval(timer);

    }, []);

    return (

        <div
            style={{
                display: "grid",
                gridTemplateColumns: "repeat(6,1fr)",
                gap: "20px",
                marginBottom: "30px"
            }}
        >

            <Card
                title="Employees"
                value={dashboard.employees}
                color="#2563eb"
            />

            <Card
                title="Devices"
                value={dashboard.devices}
                color="#16a34a"
            />

            <Card
                title="Incidents"
                value={dashboard.incidents}
                color="#dc2626"
            />

            <Card
                title="Critical"
                value={dashboard.critical}
                color="#7f1d1d"
            />

            <Card
                title="Agents Online"
                value={dashboard.agents_online}
                color="#9333ea"
            />

            <Card
                title="Threat Feed"
                value={dashboard.threat_feed}
                color="#0891b2"
            />

        </div>

    );

}

function Card({ title, value, color }) {

    return (

        <div
            style={{
                background: color,
                color: "white",
                borderRadius: "15px",
                padding: "20px",
                textAlign: "center",
                boxShadow: "0px 4px 12px rgba(0,0,0,.25)"
            }}
        >

            <h3>{title}</h3>

            <h1>{value}</h1>

        </div>

    );

}

export default DashboardCards;