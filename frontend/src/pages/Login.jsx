import { Link } from "react-router-dom";

function Login() {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        background: "#0f172a",
      }}
    >
      <div
        style={{
          background: "white",
          padding: "40px",
          borderRadius: "10px",
          width: "350px",
          textAlign: "center",
        }}
      >
        <h1>🛡 Sentinel AI</h1>

        <input
          placeholder="Username"
          style={{
            width: "100%",
            padding: "10px",
            marginTop: "20px",
          }}
        />

        <input
          type="password"
          placeholder="Password"
          style={{
            width: "100%",
            padding: "10px",
            marginTop: "10px",
          }}
        />

        <Link to="/dashboard">
          <button
            style={{
              marginTop: "20px",
              width: "100%",
              padding: "12px",
              background: "#2563eb",
              color: "white",
              border: "none",
              cursor: "pointer",
            }}
          >
            Login
          </button>
        </Link>
      </div>
    </div>
  );
}

export default Login;