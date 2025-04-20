import Axios from "@/utils/axios.js"

// 获取所有患者信息
export function getPatients() {
    return Axios.get('/patient/all')
}

// 删除患者
export function deletePatient(patientId) {
    return Axios.delete(`/patient/delete/${patientId}`)
}

// 更新患者信息
export function updatePatient(patientId, patientData) {
    return Axios.put(`/patient/update/${patientId}`, patientData)
}

// 添加新患者
export function addPatient(patientData) {
    return Axios.post('/patient/add', patientData)
}

// 根据条件筛选患者
export function filterPatients(filterData) {
    return Axios.post('/patient/filter', filterData)
}

// 获取患者的最新异常事件数值
export function getLatestPatientEvents(patientIds, eventIds) {
    return Axios.post('/patient/get_latest_patient_events', {
        patient_ids: patientIds,
        event_ids: eventIds
    })
}

// 获取患者的聚类结果
export function getPatientClusterResult(patientIds) {
    return Axios.post('/patient/cluster_result', {
        patient_ids: patientIds
    })
}

// 获取患者的事件完整信息
export function getPatientEventFullInfo(patientId) {
    return Axios.post('/patient/event_full_info', {
        patient_id: patientId
    })
}

// 获取患者性别统计
export function getGenderStats() {
    return Axios.get('/patient/gender_stats')
}

// 获取患者年龄分布
export function getAgeStats() {
    return Axios.get('/patient/age_stats')
}

// 获取带事件的患者信息
export function getPatientsWithEvents() {
    return Axios.get('/patient/details')
}
