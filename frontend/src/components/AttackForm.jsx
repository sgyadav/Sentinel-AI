import { useState } from "react";
import api from "../services/api";

function AttackForm() {

  const [eventType, setEventType] = useState("Failed Login");
  const [result, setResult] = useState(null);

  const simulateAttack = async () => {

    const payload = {
      hostname: "PC-001",
      event_type: eventType,
      severity: "High",
      description: "Attack generated from Sentinel AI Simulator"
    };

    try {

      const response = await api.post("/event", payload);

      setResult(response.data);

    } catch (error) {

      console.log(error);

      alert("Simulation Failed");

    }

  };

  return (

    <div
      style={{
        background: "white",
        padding: "30px",
        borderRadius: "10px",
        boxShadow: "0px 3px 10px rgba(0,0,0,0.2)"
      }}
    >

      <h2>🛡 Attack Simulation</h2>

      <select
        value={eventType}
        onChange={(e) => setEventType(e.target.value)}
        style={{
          width: "100%",
          padding: "10px",
          marginTop: "20px"
        }}
      >

        <option>Failed Login</option>
<option>Brute Force</option>
<option>Malware</option>
<option>Ransomware</option>
<option>USB Attack</option>
<option>Port Scan</option>
<option>Privilege Escalation</option>
<option>Data Exfiltration</option>
<option>Command & Control</option>
<option>DNS Tunneling</option>

      </select>

      <button
        onClick={simulateAttack}
        style={{
          marginTop: "20px",
          width: "100%",
          padding: "12px",
          background: "#d32f2f",
          color: "white",
          border: "none",
          cursor: "pointer"
        }}
      >

        Simulate Attack

      </button>

      {result && (

        <div
          style={{
            marginTop: "30px"
          }}
        >

         <h3>🤖 AI Security Analysis</h3>

<p>
<b>Alert:</b> {result.alert}
</p>

<p>
<b>Incident:</b> {result.incident.attack_type}
</p>

<p>
<b>Risk Score:</b>

<span
style={{
color:
result.incident.risk_score >= 80
? "red"
: result.incident.risk_score >= 50
? "orange"
: "green",
fontWeight: "bold"
}}
>
{" "}
{result.incident.risk_score}
</span>

</p>

<p>
<b>Priority:</b> {result.response.priority}
</p>

<p>
<b>Response:</b> {result.response.action}
</p>

<p>
<b>Recommendation:</b> {result.investigation.recommendation}
</p>

<p>
<b>Confidence:</b> {result.investigation.confidence}%
</p>

        </div>

      )}

    </div>

  );

}

export default AttackForm;