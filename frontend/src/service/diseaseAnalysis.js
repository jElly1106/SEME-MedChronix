import Axios from "@/utils/axios.js"

export function getAllEvents() {
    return Axios.get('/disease/get_all_events')
}

