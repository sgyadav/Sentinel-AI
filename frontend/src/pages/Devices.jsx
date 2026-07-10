import { useEffect, useMemo, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import api from "../services/api";
import RegisterDevice from "../components/RegisterDevice";

function Devices() {
  const [devices, setDevices] = useState([]);
  const [agentStatus, setAgentStatus] = useState([]);

  const loadData = async () => {
    try {
      const [devicesResponse, agentsResponse] = await Promise.all([
        api.get("/device/"),
        api.get("/agent/status"),
      ]);

      setDevices(devicesResponse.data);
      setAgentStatus(agentsResponse.data);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    loadData();

    const timer = setInterval(loadData, 3000);

    return () => clearInterval(timer);
  }, []);

  const rows = useMemo(() => {
    const liveByHost = new Map(
      agentStatus.map((agent) => [agent.hostname, agent])
    );

    const registeredRows = devices.map((device) => ({
      ...device,
      agent: liveByHost.get(device.hostname),
    }));

    const registeredHosts = new Set(devices.map((device) => device.hostname));
    const liveOnlyRows = agentStatus
      .filter((agent) => !registeredHosts.has(agent.hostname))
      .map((agent) => ({
        hostname: agent.hostname,
        ip_address: agent.ip_address,
        operating_system: agent.operating_system,
        agent,
      }));

    return [...registeredRows, ...liveOnlyRows];
  }, [devices, agentStatus]);

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
        <h1>Device Monitoring</h1>

        <RegisterDevice />

        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            background: "white",
            marginTop: "20px",
            boxShadow: "0 3px 10px rgba(0,0,0,.2)",
          }}
        >
          <thead
            style={{
              background: "#0f172a",
              color: "white",
            }}
          >
            <tr>
              <th style={{ padding: "12px" }}>Hostname</th>
              <th>IP Address</th>
              <th>Operating System</th>
              <th>CPU</th>
              <th>RAM</th>
              <th>Disk</th>
              <th>User</th>
              <th>Status</th>
              <th>Threat</th>
            </tr>
          </thead>

          <tbody>
            {rows.map((device) => {
              const agent = device.agent;
              const hasThreat = agent?.incidents?.length > 0;

              return (
                <tr
                  key={device.hostname}
                  style={{
                    textAlign: "center",
                    borderBottom: "1px solid #ddd",
                  }}
                >
                  <td>{device.hostname}</td>
                  <td>{device.ip_address}</td>
                  <td>{device.operating_system}</td>
                  <td>{agent ? `${agent.cpu_usage}%` : "--"}</td>
                  <td>{agent ? `${agent.ram_usage}%` : "--"}</td>
                  <td>{agent ? `${agent.disk_usage}%` : "--"}</td>
                  <td>{agent ? agent.username : "--"}</td>
                  <td>{agent ? "Online" : "Offline"}</td>
                  <td>{hasThreat ? "Needs attention" : "Protected"}</td>
                </tr>
              );
            })}

            {rows.length === 0 && (
              <tr>
                <td colSpan="9" style={{ padding: "18px", textAlign: "center" }}>
                  No devices or live endpoint agents found yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default Devices;
