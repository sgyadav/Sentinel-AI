import { useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import api from "../services/api";

function ThreatIntel() {

  const [ip, setIp] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeIP = async () => {

    if (!ip) {
      alert("Please enter an IP address");
      return;
    }

    try {

      setLoading(true);

      const response = await api.get(`/threat-intel/${ip}`);

      setResult(response.data);

    } catch (err) {

      console.log(err);

      alert("Unable to retrieve Threat Intelligence.");

    } finally {

      setLoading(false);

    }

  };

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

        <h1>🌍 Threat Intelligence Center</h1>

        <p>Analyze an IP address using integrated threat intelligence providers.</p>

        <div
          style={{
            background: "#fff",
            padding: "20px",
            borderRadius: "10px",
            marginTop: "20px",
            boxShadow: "0 4px 10px rgba(0,0,0,.15)"
          }}
        >

          <input
            type="text"
            placeholder="Enter IP Address (Example: 8.8.8.8)"
            value={ip}
            onChange={(e) => setIp(e.target.value)}
            style={{
              width: "300px",
              padding: "10px",
              marginRight: "10px"
            }}
          />

          <button
            onClick={analyzeIP}
            style={{
              padding: "10px 20px",
              cursor: "pointer"
            }}
          >
            Analyze
          </button>

        </div>

        {loading &&

          <p style={{ marginTop: "20px" }}>
            Checking threat intelligence...
          </p>

        }

        {result && (

          <div
            style={{
              background: "#fff",
              marginTop: "30px",
              padding: "20px",
              borderRadius: "10px",
              boxShadow: "0 4px 10px rgba(0,0,0,.15)"
            }}
          >

            <h2>Analysis Result</h2>

            <p><b>IP Address:</b> {result.ip}</p>

            <hr />

            <h3>AbuseIPDB</h3>

            <pre>
              {JSON.stringify(result.abuseipdb, null, 2)}
            </pre>

            <hr />

            <h3>VirusTotal</h3>

            <pre>
              {JSON.stringify(result.virustotal, null, 2)}
            </pre>

            <hr />

            <h3>AlienVault OTX</h3>

            <pre>
              {JSON.stringify(result.alienvault, null, 2)}
            </pre>

          </div>

        )}

      </div>

    </>

  );

}

export default ThreatIntel;