import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import api from "../services/api";

function Settings() {

  const [policy, setPolicy] = useState({
    cpu_threshold: 90,
    ram_threshold: 90,
    disk_threshold: 95,
    heartbeat_interval: 10,
    alert_level: "Medium"
  });

  const loadPolicy = async () => {

    try {

      const response = await api.get("/security-policy");

      setPolicy(response.data);

    } catch (err) {

      console.log(err);

    }

  };

  useEffect(() => {

    loadPolicy();

  }, []);

  const savePolicy = async () => {

    try {

      await api.put("/security-policy", policy);

      alert("Security Policy Updated Successfully");

    } catch (err) {

      console.log(err);

      alert("Unable to Save Policy");

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

        <h1>⚙ Security Policy Settings</h1>

        <div
          style={{
            background: "white",
            padding: "25px",
            borderRadius: "10px",
            marginTop: "20px",
            width: "500px",
            boxShadow: "0 4px 10px rgba(0,0,0,.15)"
          }}
        >

          <label>CPU Threshold (%)</label>

          <input
            type="number"
            value={policy.cpu_threshold}
            onChange={(e) =>
              setPolicy({
                ...policy,
                cpu_threshold: Number(e.target.value)
              })
            }
            style={{ width: "100%", padding: "10px", marginBottom: "15px" }}
          />

          <label>RAM Threshold (%)</label>

          <input
            type="number"
            value={policy.ram_threshold}
            onChange={(e) =>
              setPolicy({
                ...policy,
                ram_threshold: Number(e.target.value)
              })
            }
            style={{ width: "100%", padding: "10px", marginBottom: "15px" }}
          />

          <label>Disk Threshold (%)</label>

          <input
            type="number"
            value={policy.disk_threshold}
            onChange={(e) =>
              setPolicy({
                ...policy,
                disk_threshold: Number(e.target.value)
              })
            }
            style={{ width: "100%", padding: "10px", marginBottom: "15px" }}
          />

          <label>Heartbeat Interval (seconds)</label>

          <input
            type="number"
            value={policy.heartbeat_interval}
            onChange={(e) =>
              setPolicy({
                ...policy,
                heartbeat_interval: Number(e.target.value)
              })
            }
            style={{ width: "100%", padding: "10px", marginBottom: "15px" }}
          />

          <label>Alert Level</label>

          <select
            value={policy.alert_level}
            onChange={(e) =>
              setPolicy({
                ...policy,
                alert_level: e.target.value
              })
            }
            style={{ width: "100%", padding: "10px", marginBottom: "20px" }}
          >
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
            <option>Critical</option>
          </select>

          <button
            onClick={savePolicy}
            style={{
              padding: "12px 25px",
              cursor: "pointer",
              background: "#2563eb",
              color: "white",
              border: "none",
              borderRadius: "6px"
            }}
          >
            Save Policy
          </button>

        </div>

      </div>

    </>

  );

}

export default Settings;