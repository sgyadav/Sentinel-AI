import { useEffect, useState } from "react";
import api from "../services/api";

function IncidentAnalytics() {

    const [stats, setStats] = useState({
        malware: 0,
        bruteForce: 0,
        ransomware: 0,
        usb: 0,
        portScan: 0
    });

    const loadAnalytics = async () => {

        try {

            const res = await api.get("/incidents");

            const incidents = res.data;

            let analytics = {
                malware: 0,
                bruteForce: 0,
                ransomware: 0,
                usb: 0,
                portScan: 0
            };

            incidents.forEach((item) => {

                switch(item.attack_type){

                    case "Malware":
                        analytics.malware++;
                        break;

                    case "Brute Force":
                        analytics.bruteForce++;
                        break;

                    case "Ransomware":
                        analytics.ransomware++;
                        break;

                    case "USB Attack":
                        analytics.usb++;
                        break;

                    case "Reconnaissance":
                        analytics.portScan++;
                        break;

                    default:
                        break;
                }

            });

            setStats(analytics);

        } catch(err){

            console.log(err);

        }

    };

    useEffect(()=>{

        loadAnalytics();

        const timer = setInterval(loadAnalytics,3000);

        return ()=>clearInterval(timer);

    },[]);

   return (

    <div
        style={{
            background: "white",
            padding: "20px",
            marginTop: "30px",
            borderRadius: "10px",
            boxShadow: "0 3px 10px rgba(0,0,0,.2)"
        }}
    >

        <h2>📈 Incident Analytics</h2>

        <div
            style={{
                display: "grid",
                gridTemplateColumns: "repeat(5,1fr)",
                gap: "15px",
                marginTop: "20px"
            }}
        >

            <Card
                title="🦠 Malware"
                value={stats.malware}
                color="#dc2626"
            />

            <Card
                title="🔐 Brute Force"
                value={stats.bruteForce}
                color="#2563eb"
            />

            <Card
                title="💾 USB Attack"
                value={stats.usb}
                color="#16a34a"
            />

            <Card
                title="🌐 Port Scan"
                value={stats.portScan}
                color="#f59e0b"
            />

            <Card
                title="💀 Ransomware"
                value={stats.ransomware}
                color="#7c3aed"
            />

        </div>

    </div>

);

}

function Card({ title, value, color }) {

    return (

        <div
            style={{
                background: color,
                color: "white",
                borderRadius: "12px",
                padding: "20px",
                textAlign: "center"
            }}
        >

            <h3>{title}</h3>

            <h1>{value}</h1>

        </div>

    );

}
export default IncidentAnalytics;