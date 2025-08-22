import axios from "axios";

const api = axios.create({
  baseURL: "/api", // Nginx faz proxy para a API Flask
  timeout: 15000,
});

export default api;
