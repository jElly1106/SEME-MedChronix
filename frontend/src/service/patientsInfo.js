import Axios from "@/utils/axios.js"

export function getPatients() {
    return Axios.get('/patient/get_all_patients')
        // {
        //     headers: {
        //         'Content-Type': 'application/json',
        //         'Authorization': localStorage.getItem('token')
        //     }
        // }
}