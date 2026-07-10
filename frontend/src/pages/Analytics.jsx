import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

function Analytics() {
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
        <h1>📈 Security Analytics</h1>

        <p>Analytics dashboard is under development.</p>
      </div>
    </>
  );
}

export default Analytics;