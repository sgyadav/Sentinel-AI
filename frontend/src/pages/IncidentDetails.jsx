import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import api from "../services/api";

function IncidentDetails() {

    const { id } = useParams();

    const [incident, setIncident] = useState(null);

    useEffect(() => {

        api.get(`/incident/${id}`)
            .then(res => setIncident(res.data))
            .catch(console.log);

    }, [id]);

    if (!incident) {

        return <h2>Loading...</h2>;

    }

    return (

        <>
            <Sidebar />
            <Topbar />

            <div
                style={{
                    marginLeft: "260px",
                    marginTop: "90px",
                    padding: "30px"
                }}
            >

                <h1>🚨 Incident Investigation</h1>

                <hr/>

                <h2>{incident.attack_type}</h2>

                <p><b>Incident ID:</b> {incident.incident_id}</p>

                <p><b>Hostname:</b> {incident.hostname}</p>

                <p><b>Risk Score:</b> {incident.risk_score}</p>

                <p><b>Status:</b> {incident.status}</p>

                <p><b>MITRE:</b> {incident.mitre_technique}</p>

                <p><b>Tactic:</b> {incident.mitre_tactic}</p>

                <p><b>Recommendation:</b> {incident.recommendation}</p>

                <p><b>SOAR Action:</b> {incident.response_action}</p>

            </div>

        </>

    );

}

export default IncidentDetails;