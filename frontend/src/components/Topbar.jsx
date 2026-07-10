function Topbar() {
  return (
    <div
      style={{
        height: "70px",
        background: "#1e293b",
        color: "white",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 30px",
        marginLeft: "250px",
      }}
    >
      <h2>Sentinel AI Dashboard</h2>

      <div>
        <strong>Admin</strong>
      </div>
    </div>
  );
}

export default Topbar;