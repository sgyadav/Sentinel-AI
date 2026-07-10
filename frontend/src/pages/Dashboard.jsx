import { useEffect, useState } from "react";
import api from "../services/api";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import DashboardCards from "../components/DashboardCards";
import EmployeeTable from "../components/EmployeeTable";
import IncidentTable from "../components/IncidentTable";
import HighRiskEmployees from "../components/HighRiskEmployees";
import IncidentAnalytics from "../components/IncidentAnalytics";
import SecurityTimeline from "../components/SecurityTimeline";
import NotificationCenter from "../components/NotificationCenter";
import AttackTrendChart from "../components/AttackTrendChart";
import LiveEventStream from "../components/LiveEventStream";

function Dashboard() {

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

        } catch (error) {

            console.log(error);

        }

    };

    useEffect(() => {

        loadDashboard();

        const timer = setInterval(loadDashboard, 3000);

        return () => {

            clearInterval(timer);

        };

    }, []);

    return (

        <>

            <Sidebar />

            <Topbar />

            <div
                style={{
                    marginLeft: "260px",
                    marginTop: "90px",
                    padding: "25px",
                }}
            >

                <h1>Security Operations Center</h1>

                <DashboardCards dashboard={dashboard} />

                <AttackTrendChart />

                <LiveEventStream />

                <NotificationCenter />

                <SecurityTimeline />

                <HighRiskEmployees />

                <IncidentAnalytics />

                <EmployeeTable />

                <IncidentTable />

            </div>

        </>

    );

}

export default Dashboard;
