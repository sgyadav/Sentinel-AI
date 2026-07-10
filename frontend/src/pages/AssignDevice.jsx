import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import AssignDevice from "../components/AssignDevice";

function AssignDevicePage() {

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
        <h1>🔗 Device Assignment</h1>

        <AssignDevice />
      </div>
    </>
  );
}

export default AssignDevicePage;