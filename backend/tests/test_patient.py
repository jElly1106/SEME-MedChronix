import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

@patch("api.patient.Disease.query")
@patch("api.patient.db")
@patch("api.patient.Patient")
@patch("api.patient.request")
def test_add_patient_success(mock_req, mock_patient, mock_db, mock_disease):
    # 病种存在
    mock_disease.filter_by.return_value.first.return_value = MagicMock(id=1)
    mock_patient.query.get_or_404.return_value = MagicMock(id=1)
    mock_db.session.add.return_value = None
    mock_db.session.commit.return_value = None
    mock_req.get_json.return_value = {
        "name": "李四", "gender": "男", "age": 55,
        "heart_history": "无", "diabete_history": "有", "EH_history": "有",
        "status": "脑卒中", "desease": "脑卒中", "in_icu": "2024-05-01 08:00:00"
    }
    from api.patient import add_patient
    resp, code = add_patient()
    assert code == 201

@patch("api.patient.Disease.query")
@patch("api.patient.db")
@patch("api.patient.Patient")
@patch("api.patient.request")
def test_add_patient_disease_not_found(mock_req, mock_patient, mock_db, mock_disease):
    mock_disease.filter_by.return_value.first.return_value = None
    mock_req.get_json.return_value = {
        "name": "李四", "desease": "未知疾病"
    }
    from api.patient import add_patient
    resp, code = add_patient()
    assert code == 404

@patch("api.patient.Patient.query")
@patch("api.patient.db")
@patch("api.patient.request")
def test_update_patient_success(mock_req, mock_db, mock_patient):
    fake_patient = MagicMock(id=1)
    mock_patient.get_or_404.return_value = fake_patient
    mock_db.session.commit.return_value = None
    mock_req.get_json.return_value = {
        "name": "新名字", "gender": "女", "age": 44,
        "heart_history": "有", "diabete_history": "无", "EH_history": "有",
        "status": "恢复", "in_icu": "2024-05-10 10:00:00", "out_icu": "2024-05-13 10:00:00"
    }
    from api.patient import update_patient
    resp, code = update_patient(1)
    assert code == 200

@patch("api.patient.Patient.query")
@patch("api.patient.db")
def test_delete_patient_success(mock_db, mock_patient):
    fake_patient = MagicMock(id=1)
    mock_patient.get_or_404.return_value = fake_patient
    mock_db.session.delete.return_value = None
    mock_db.session.commit.return_value = None
    from api.patient import delete_patient
    resp, code = delete_patient(1)
    assert code == 200

@patch("api.patient.Patient.query")
def test_update_patient_not_found(mock_patient):
    mock_patient.get_or_404.side_effect = Exception("not found")
    from api.patient import update_patient
    with pytest.raises(Exception):
        update_patient(999)
