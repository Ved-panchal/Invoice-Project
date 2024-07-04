import axios from "axios";
import { apiurl } from "./config";

const baseurl = `${apiurl}`;

const api = axios.create({
    withCredentials: true,
    baseURL: baseurl,
    
})

api.interceptors.response.use(
    response => response,
    error => {
      if (error.response.status === 401 && error.response.data['detail'] == "Invalid credentials") {
        console.log(error)
        localStorage.setItem('Failed', true)
        window.location.href = '/';
      }
    });


export default api;