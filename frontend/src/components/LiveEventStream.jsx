import { useEffect, useState } from "react";
import { connectWebSocket, closeWebSocket } from "../services/websocket";

function LiveEventStream() {

    const [events, setEvents] = useState([]);

    useEffect(() => {

        connectWebSocket((message) => {

            if (message.type === "incident") {

                setEvents(prev => [

                    {
                        time: new Date().toLocaleTimeString(),
                        attack: message.incident.attack_type,
                        hostname: message.incident.hostname,
                        risk: message.incident.risk_score
                    },

                    ...prev

                ]);

            }

        });

        return () => {

            closeWebSocket();

        };

    }, []);

    return (

        <div
            style={{
                background: "white",
                padding: "20px",
                borderRadius: "12px",
                marginTop: "25px",
                boxShadow: "0 4px 10px rgba(0,0,0,.15)"
            }}
        >

            <h2>⚡ Live Security Events</h2>

            <table width="100%">

                <thead>

                    <tr>

                        <th>Time</th>

                        <th>Host</th>

                        <th>Attack</th>

                        <th>Risk</th>

                    </tr>

                </thead>

                <tbody>

                    {events.map((event,index)=>(

                        <tr key={index}>

                            <td>{event.time}</td>

                            <td>{event.hostname}</td>

                            <td>{event.attack}</td>

                            <td>{event.risk}</td>

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>

    );

}

export default LiveEventStream;