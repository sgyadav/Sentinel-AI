import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import AttackForm from "../components/AttackForm";

function AttackSimulation() {

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

        <AttackForm />

      </div>

    </>

  );

}

export default AttackSimulation;