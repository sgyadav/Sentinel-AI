import { useEffect, useState } from "react";
import api from "../services/api";

function SecurityTimeline() {

  const [incidents, setIncidents] = useState([]);

  const loadTimeline = async () => {

    try {

      const response = await api.get("/incidents");

      const sorted = response.data.reverse();

      setIncidents(sorted);

    } catch (error) {

      console.log(error);

    }

  };

  useEffect(() => {

    loadTimeline();

    const timer = setInterval(loadTimeline, 3000);

    return () => clearInterval(timer);

  }, []);

  const getColor = (risk) => {

    if (risk >= 70) return "#dc2626";

    if (risk >= 40) return "#f59e0b";

    return "#16a34a";

  };

  return (

    <div
      style={{
        background: "white",
        marginTop: "30px",
        padding: "25px",
        borderRadius: "10px",
        boxShadow: "0px 3px 10px rgba(0,0,0,.2)"
      }}
    >

      <h2>⚡ Live Security Timeline</h2>

      <hr />

      {incidents.length === 0 && (

        <p>No Security Events</p>

      )}

      {incidents.map((incident, index) => (

        <div
          key={incident.incident_id}
          style={{
            display: "flex",
            gap: "20px",
            padding: "15px",
            borderLeft: `5px solid ${getColor(incident.risk_score)}`,
            marginBottom: "15px",
            background: "#fafafa"
          }}
        >

          <div>

            <strong>#{index + 1}</strong>

          </div>

          <div>

            <strong>

              🚨 {incident.attack_type}

            </strong>

            <br />

            <b>Host:</b> {incident.hostname}

            <br />

            <b>Risk:</b>

            <span
              style={{
                color: getColor(incident.risk_score),
                fontWeight: "bold"
              }}
            >
              {" "}
              {incident.risk_score}
            </span>

            <br />

            <b>Status:</b> {incident.status}

            <br />

            <b>Recommendation:</b> {incident.recommendation}

          </div>

        </div>

      ))}

    </div>

  );

}

export default SecurityTimeline;