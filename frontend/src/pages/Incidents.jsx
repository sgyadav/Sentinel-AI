import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import api from "../services/api";

function Incidents() {

  const [incidents, setIncidents] = useState([]);

  const loadIncidents = async () => {
    try {
      const response = await api.get("/incidents");
      setIncidents(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {

    loadIncidents();

    const timer = setInterval(loadIncidents, 3000);

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
        <h1>🚨 Security Incidents</h1>

        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            marginTop: "25px",
            background: "white",
            boxShadow: "0px 2px 8px rgba(0,0,0,0.2)",
          }}
        >
          <thead
            style={{
              background: "#1e293b",
              color: "white",
            }}
          >
            <tr>
              <th style={{ padding: "12px" }}>Incident ID</th>
              <th>Hostname</th>
              <th>Attack</th>
              <th>Risk Score</th>
              <th>Status</th>
              <th>Priority</th>
            </tr>
          </thead>

          <tbody>
            {incidents.map((incident) => (
              <tr
                key={incident.incident_id}
                style={{
                  textAlign: "center",
                  borderBottom: "1px solid #ddd",
                }}
              >
                <td>{incident.incident_id}</td>
                <td>{incident.hostname}</td>
                <td>{incident.attack_type}</td>
                <td>{incident.risk_score}</td>
                <td>{incident.status}</td>
                <td>{incident.priority}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default Incidents;