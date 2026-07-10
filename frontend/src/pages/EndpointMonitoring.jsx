import { useCallback, useEffect, useMemo, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import api from "../services/api";
import { connectWebSocket, closeWebSocket } from "../services/websocket";

function EndpointMonitoring() {
  const [agents, setAgents] = useState([]);
  const [selectedHost, setSelectedHost] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadAgents = useCallback(async () => {
    try {
      const response = await api.get("/agent/status");

      setAgents(response.data);
      setLastUpdated(new Date());

      setSelectedHost((current) => current || response.data[0]?.hostname || "");
    } catch (error) {
      console.log(error);
    }
  }, []);

  useEffect(() => {
    loadAgents();

    const timer = setInterval(loadAgents, 5000);

    connectWebSocket((message) => {
      if (message.type === "agent_status") {
        setAgents((current) => upsertAgent(current, message.agent));
        setSelectedHost((current) => current || message.agent.hostname);
        setLastUpdated(new Date());
      }
    });

    return () => {
      clearInterval(timer);
      closeWebSocket();
    };
  }, [loadAgents]);

  const selectedAgent = useMemo(
    () =>
      agents.find((agent) => agent.hostname === selectedHost) ||
      agents[0] ||
      null,
    [agents, selectedHost]
  );

  return (
    <>
      <Sidebar />
      <Topbar />

      <main
        style={{
          marginLeft: "260px",
          marginTop: "90px",
          padding: "30px",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "16px",
            marginBottom: "24px",
          }}
        >
          <div>
            <h1 style={{ marginBottom: "6px" }}>Endpoint Monitoring</h1>
            <p style={{ margin: 0, color: "#475569" }}>
              Live telemetry from installed endpoint agents.
            </p>
          </div>

          <div
            style={{
              background: "#e0f2fe",
              color: "#075985",
              padding: "10px 14px",
              borderRadius: "8px",
              fontWeight: 700,
            }}
          >
            {agents.length} agent{agents.length === 1 ? "" : "s"} online
          </div>
        </div>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "16px",
            marginBottom: "24px",
          }}
        >
          <MetricCard
            label="CPU Usage"
            value={selectedAgent ? `${selectedAgent.cpu_usage}%` : "--"}
            accent="#2563eb"
          />
          <MetricCard
            label="RAM Usage"
            value={selectedAgent ? `${selectedAgent.ram_usage}%` : "--"}
            accent="#16a34a"
          />
          <MetricCard
            label="Disk Usage"
            value={selectedAgent ? `${selectedAgent.disk_usage}%` : "--"}
            accent="#f97316"
          />
          <MetricCard
            label="Local Detections"
            value={selectedAgent?.incidents?.length || 0}
            accent="#dc2626"
          />
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "minmax(260px, 360px) 1fr",
            gap: "20px",
            alignItems: "start",
          }}
        >
          <div style={panelStyle}>
            <h2>Live Agents</h2>

            {agents.length === 0 && (
              <p style={{ color: "#64748b" }}>
                No endpoint heartbeat received yet. Start the endpoint agent to
                populate this screen.
              </p>
            )}

            {agents.map((agent) => (
              <button
                key={agent.hostname}
                onClick={() => setSelectedHost(agent.hostname)}
                style={{
                  width: "100%",
                  textAlign: "left",
                  background:
                    selectedAgent?.hostname === agent.hostname
                      ? "#dbeafe"
                      : "#f8fafc",
                  border: "1px solid #cbd5e1",
                  borderRadius: "8px",
                  padding: "12px",
                  marginBottom: "10px",
                  cursor: "pointer",
                }}
              >
                <strong>{agent.hostname}</strong>
                <div style={{ color: "#475569", marginTop: "4px" }}>
                  {agent.ip_address} | {agent.username}
                </div>
                <div style={{ color: "#15803d", marginTop: "4px" }}>
                  {agent.status}
                </div>
              </button>
            ))}

            {lastUpdated && (
              <p style={{ color: "#64748b", fontSize: "13px" }}>
                Last update: {lastUpdated.toLocaleTimeString()}
              </p>
            )}
          </div>

          <div style={panelStyle}>
            <h2>Endpoint Details</h2>

            {!selectedAgent && (
              <p style={{ color: "#64748b" }}>
                Waiting for live endpoint telemetry.
              </p>
            )}

            {selectedAgent && (
              <>
                <InfoGrid agent={selectedAgent} />

                <h3>Detected Incidents</h3>
                <SimpleTable
                  columns={["Severity", "Type", "Description"]}
                  rows={(selectedAgent.incidents || []).map((incident) => [
                    incident.severity,
                    incident.type || incident.attack_type,
                    incident.description,
                  ])}
                  empty="No local endpoint incidents detected."
                />

                <h3>Running Processes</h3>
                <SimpleTable
                  columns={["PID", "Name", "User", "CPU", "Memory"]}
                  rows={(selectedAgent.running_processes || [])
                    .slice(0, 12)
                    .map((process) => [
                      process.pid,
                      process.name,
                      process.username,
                      process.cpu,
                      `${process.memory}%`,
                    ])}
                  empty="No process data received."
                />

                <h3>Network Connections</h3>
                <SimpleTable
                  columns={["Local", "Remote", "Status", "PID"]}
                  rows={(selectedAgent.network_connections || [])
                    .slice(0, 12)
                    .map((connection) => [
                      connection.local,
                      connection.remote || "-",
                      connection.status,
                      connection.pid || "-",
                    ])}
                  empty="No network connections received."
                />

                <h3>Recent Windows Security Events</h3>
                <SimpleTable
                  columns={["Event ID", "Source", "Time"]}
                  rows={(selectedAgent.security_events || [])
                    .slice(0, 10)
                    .map((event) => [
                      event.event_id,
                      event.source,
                      event.time,
                    ])}
                  empty="No security event log data received."
                />
              </>
            )}
          </div>
        </section>
      </main>
    </>
  );
}

function upsertAgent(current, nextAgent) {
  const existing = current.find((agent) => agent.hostname === nextAgent.hostname);

  if (!existing) {
    return [nextAgent, ...current];
  }

  return current.map((agent) =>
    agent.hostname === nextAgent.hostname ? nextAgent : agent
  );
}

function MetricCard({ label, value, accent }) {
  return (
    <div
      style={{
        background: "white",
        borderRadius: "8px",
        padding: "18px",
        borderTop: `4px solid ${accent}`,
        boxShadow: "0 2px 8px rgba(15,23,42,.12)",
      }}
    >
      <div style={{ color: "#64748b", fontSize: "14px" }}>{label}</div>
      <div style={{ fontSize: "28px", fontWeight: 800, marginTop: "8px" }}>
        {value}
      </div>
    </div>
  );
}

function InfoGrid({ agent }) {
  const rows = [
    ["Hostname", agent.hostname],
    ["IP Address", agent.ip_address],
    ["Operating System", agent.operating_system],
    ["Username", agent.username],
    ["Status", agent.status],
    ["MAC Address", agent.mac_address || "Not provided"],
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
        gap: "10px",
        marginBottom: "20px",
      }}
    >
      {rows.map(([label, value]) => (
        <div
          key={label}
          style={{
            background: "#f8fafc",
            border: "1px solid #e2e8f0",
            borderRadius: "8px",
            padding: "10px",
          }}
        >
          <div style={{ color: "#64748b", fontSize: "13px" }}>{label}</div>
          <strong>{value}</strong>
        </div>
      ))}
    </div>
  );
}

function SimpleTable({ columns, rows, empty }) {
  return (
    <table
      style={{
        width: "100%",
        borderCollapse: "collapse",
        marginBottom: "22px",
      }}
    >
      <thead>
        <tr>
          {columns.map((column) => (
            <th
              key={column}
              style={{
                textAlign: "left",
                borderBottom: "1px solid #cbd5e1",
                padding: "8px",
              }}
            >
              {column}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {row.map((cell, cellIndex) => (
              <td
                key={`${rowIndex}-${cellIndex}`}
                style={{
                  borderBottom: "1px solid #e2e8f0",
                  padding: "8px",
                  verticalAlign: "top",
                }}
              >
                {cell}
              </td>
            ))}
          </tr>
        ))}

        {rows.length === 0 && (
          <tr>
            <td colSpan={columns.length} style={{ padding: "12px" }}>
              {empty}
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

const panelStyle = {
  background: "white",
  borderRadius: "8px",
  padding: "20px",
  boxShadow: "0 2px 8px rgba(15,23,42,.12)",
};

export default EndpointMonitoring;
