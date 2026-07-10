import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

function Organization() {
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
        <h1>🏢 Organization</h1>
        <p>Organization Management</p>
      </div>
    </>
  );
}

export default Organization;