import { Link } from "react-router-dom";

function Sidebar() {
  return (
    <div
      style={{
        width: "250px",
        height: "100vh",
        background: "#0f172a",
        color: "white",
        padding: "20px",
        position: "fixed",
        left: 0,
        top: 0,
      }}
    >
      <h2 style={{ color: "#38bdf8" }}>Sentinel AI</h2>

      <hr />

      <nav
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "18px",
          marginTop: "30px",
        }}
      >
        <Link to="/dashboard" style={linkStyle}>
          Dashboard
        </Link>

        <Link to="/endpoint-monitoring" style={linkStyle}>
          Endpoint Monitoring
        </Link>

        <Link to="/devices" style={linkStyle}>
          Devices
        </Link>

        <Link to="/employees" style={linkStyle}>
          Employees
        </Link>

        <Link to="/incidents" style={linkStyle}>
          Incidents
        </Link>

        <Link to="/assign-device" style={linkStyle}>
          Assign Device
        </Link>

        <Link to="/threat-intel" style={linkStyle}>
          Threat Intelligence
        </Link>

        <Link to="/simulation" style={linkStyle}>
          Attack Simulation
        </Link>

        <Link to="/organization" style={linkStyle}>
          Organization
        </Link>

        <Link to="/analytics" style={linkStyle}>
          Analytics
        </Link>

        <Link to="/settings" style={linkStyle}>
          Settings
        </Link>
      </nav>
    </div>
  );
}

const linkStyle = {
  color: "white",
  textDecoration: "none",
  fontSize: "18px",
};

export default Sidebar;
