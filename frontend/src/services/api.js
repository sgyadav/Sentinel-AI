import axios from "axios";

const apiBaseUrl =
    import.meta.env.VITE_API_URL ||
    `${window.location.protocol}//${window.location.hostname}:8000`;

const api = axios.create({
    baseURL: apiBaseUrl,
    timeout: 10000,
    headers: {
        "Content-Type": "application/json"
    }
});

export default api;
