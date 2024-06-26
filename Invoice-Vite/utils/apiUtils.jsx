import axios from "axios";

const baseurl = "http://localhost:5500";

const api = axios.create({
    withCredentials: true,
    baseURL: baseurl,
    
})

export default api;