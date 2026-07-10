import { useEffect, useState } from "react";
import api from "../services/api";

import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
} from "chart.js";

import { Bar } from "react-chartjs-2";

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

function AttackTrendChart() {

    const [chartData, setChartData] = useState({
        labels: [],
        datasets: []
    });

    const loadChart = async () => {

        try {

            const response = await api.get("/events");

            const attacks = {};

            response.data.forEach(event => {

                attacks[event.event_type] =
                    (attacks[event.event_type] || 0) + 1;

            });

            setChartData({

                labels: Object.keys(attacks),

                datasets: [

                    {

                        label: "Attack Count",

                        data: Object.values(attacks)

                    }

                ]

            });

        }

        catch (error) {

            console.log(error);

        }

    };

    useEffect(() => {

        loadChart();

        const timer = setInterval(loadChart,3000);

        return () => clearInterval(timer);

    }, []);

    return (

        <div
            style={{
                background:"white",
                padding:"20px",
                marginTop:"30px",
                borderRadius:"10px"
            }}
        >

            <h2>Attack Trend</h2>

            <Bar data={chartData} />

        </div>

    );

}

export default AttackTrendChart;