import pytest
from unittest.mock import patch, MagicMock
from check_rule import check_rules_for_patients
from database.models import Patient, Rule, PatientEvent, PatientRule
from datetime import datetime, timedelta

# 假定：Patient, Rule, PatientEvent, PatientRule已import
# 你的check_rules_for_patients函数依赖Flask app context和SQLAlchemy
from check_rule import check_rules_for_patients

@pytest.fixture
def fake_app_ctx(monkeypatch):
    """强制app.app_context为mock，避免真实依赖"""
    monkeypatch.setattr("check_rule.app.app_context", lambda: MagicMock(__enter__=lambda s: None, __exit__=lambda s, t, v, tb: False))

def build_patient(id, heart="有", diabete="有", eh="有"):
    p = MagicMock()
    p.id = id
    p.heart_history = heart
    p.diabete_history = diabete
    p.EH_history = eh
    return p

def build_rule(id, category=1, precondition=None, eid1=1, eid2=None, td=0):
    r = MagicMock()
    r.id = id
    r.category = category
    r.precondition = precondition
    r.event_id1 = eid1
    r.event_id2 = eid2
    r.time_delta = td
    return r

def build_event(pid, eid, t):
    e = MagicMock()
    e.event_id = eid
    e.patient_id = pid
    e.time = t
    return e

@patch("check_rule.PatientRule")
@patch("check_rule.db.session")
@patch("check_rule.PatientEvent")
@patch("check_rule.Rule")
@patch("check_rule.Patient")
def test_no_patient_rule(mock_patient, mock_rule, mock_pevent, mock_db, mock_prule, fake_app_ctx):
    # 1. 空库安全
    mock_patient.query.all.return_value = []
    mock_rule.query.all.return_value = []
    mock_pevent.query.filter_by.return_value.order_by.return_value.all.return_value = []
    check_rules_for_patients()
    mock_prule.query.delete.assert_called()
    mock_db.commit.assert_called()

@patch("check_rule.PatientRule")
@patch("check_rule.db.session")
@patch("check_rule.PatientEvent")
@patch("check_rule.Rule")
@patch("check_rule.Patient")
def test_no_event_rule(mock_patient, mock_rule, mock_pevent, mock_db, mock_prule, fake_app_ctx):
    # 2. 有患者无事件，有规则
    mock_patient.query.all.return_value = [build_patient(1)]
    mock_rule.query.all.return_value = [build_rule(1)]
    mock_pevent.query.filter_by.return_value.order_by.return_value.all.return_value = []
    check_rules_for_patients()
    mock_prule.query.delete.assert_called()
    mock_db.commit.assert_called()

@patch("check_rule.PatientRule")
@patch("check_rule.db.session")
@patch("check_rule.PatientEvent")
@patch("check_rule.Rule")
@patch("check_rule.Patient")
def test_precondition_not_met(mock_patient, mock_rule, mock_pevent, mock_db, mock_prule, fake_app_ctx):
    # 3. 患者心脏病史不符
    mock_patient.query.all.return_value = [build_patient(1, heart="无")]
    mock_rule.query.all.return_value = [build_rule(1, category=3, precondition=1)]
    mock_pevent.query.filter_by.return_value.order_by.return_value.all.return_value = [build_event(1, 1, MagicMock())]
    check_rules_for_patients()
    mock_db.commit.assert_called()

@patch("check_rule.PatientRule")
@patch("check_rule.db.session")
@patch("check_rule.PatientEvent")
@patch("check_rule.Rule")
@patch("check_rule.Patient")
def test_rule_satisfied_equal(mock_patient, mock_rule, mock_pevent, mock_db, mock_prule, fake_app_ctx):
    # 4. 双事件规则 equal 分支，事件在5分钟之内
    patient = build_patient(1)
    rule = build_rule(1, category=2, eid1=1, eid2=2, td=0)
    e1 = build_event(1, 1, datetime.now())
    e2 = build_event(1, 2, datetime.now() + timedelta(minutes=4))
    events1 = [e1]
    events2 = [e2]
    def event_filter_by(patient_id=None):
        class Q:
            def order_by(self, _):
                # 返回所有事件
                if patient_id == 1:
                    return events1 + events2
                return []
        return Q()
    mock_pevent.query.filter_by.side_effect = event_filter_by
    mock_patient.query.all.return_value = [patient]
    mock_rule.query.all.return_value = [rule]
    check_rules_for_patients()
    mock_db.commit.assert_called()
