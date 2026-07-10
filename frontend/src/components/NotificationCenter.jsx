import { useEffect, useState } from "react";
import { connectWebSocket, closeWebSocket } from "../services/websocket";

function NotificationCenter() {

    const [notifications, setNotifications] = useState([]);

    useEffect(() => {

        connectWebSocket((message) => {

            if (message.type === "incident") {

                const notification = {

                    id: Date.now(),

                    text: `🚨 ${message.incident.attack_type} detected on ${message.incident.hostname}`

                };

                setNotifications(prev => [
                    notification,
                    ...prev
                ]);

            }

        });

        return () => closeWebSocket();

    }, []);

    return (

        <div
            style={{
                background: "white",
                padding: "20px",
                borderRadius: "10px",
                boxShadow: "0 4px 10px rgba(0,0,0,.2)"
            }}
        >

            <h2>🔔 Live Notifications</h2>

            {notifications.length === 0 &&

                <p>No Notifications</p>

            }

            {notifications.map(item => (

                <div
                    key={item.id}
                    style={{
                        marginTop: "10px",
                        padding: "10px",
                        borderBottom: "1px solid #ddd"
                    }}
                >

                    {item.text}

                </div>

            ))}

        </div>

    );

}

export default NotificationCenter;