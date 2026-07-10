import { useState } from "react";
import api from "../services/api";

function RegisterDevice() {

  const [device, setDevice] = useState({
    hostname: "",
    ip_address: "",
    operating_system: ""
  });

  const registerDevice = async () => {

    try {

      await api.post("/device/register", device);

      alert("✅ Device Registered Successfully");

      setDevice({
        hostname: "",
        ip_address: "",
        operating_system: ""
      });

    }

    catch(err){

      console.log(err);

      alert("Registration Failed");

    }

  };

  return (

    <div
    style={{
      background:"white",
      padding:"20px",
      marginBottom:"30px",
      borderRadius:"10px",
      boxShadow:"0 2px 8px rgba(0,0,0,.2)"
    }}
    >

    <h2>Register Device</h2>

    <input

    placeholder="Hostname"

    value={device.hostname}

    onChange={(e)=>
      setDevice({
        ...device,
        hostname:e.target.value
      })
    }

    />

    <br/><br/>

    <input

    placeholder="IP Address"

    value={device.ip_address}

    onChange={(e)=>
      setDevice({
        ...device,
        ip_address:e.target.value
      })
    }

    />

    <br/><br/>

    <input

    placeholder="Operating System"

    value={device.operating_system}

    onChange={(e)=>
      setDevice({
        ...device,
        operating_system:e.target.value
      })
    }

    />

    <br/><br/>

    <button
    onClick={registerDevice}
    >
      Register Device
    </button>

    </div>

  );

}

export default RegisterDevice;