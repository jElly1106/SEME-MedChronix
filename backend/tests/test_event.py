import pytest
from unittest.mock import patch, MagicMock

@patch("api.event.db")
@patch("api.event.Event")
def test_get_num_of_events(mock_event, mock_db):
    from api.event import get_num_of_events
    fake_event = MagicMock(event_id=1, event_name="发热", count=2)
    mock_db.session.query.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.all.return_value = [fake_event]
    resp, code = get_num_of_events()
    assert code == 200
    assert isinstance(resp, list)
    assert resp[0]["event_id"] == 1

@patch("api.event.db")
@patch("api.event.Event")
@patch("api.event.PatientEvent")
@patch("api.event.request")
def test_get_events_by_patientsIDList(mock_req, mock_pe, mock_event, mock_db):
    from api.event import get_events_by_patientsIDList
    fake_event = MagicMock(event_id=1, event_name="发热", count=1)
    mock_db.session.query.return_value.join.return_value.filter.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = [fake_event]
    mock_req.get_json.return_value = {"patient_ids": [1]}
    resp, code = get_events_by_patientsIDList()
    assert code == 200
    assert resp[0]["event_id"] == 1

@patch("api.event.db")
@patch("api.event.Event")
@patch("api.event.or_")
def test_get_event_ids_by_category(mock_or, mock_event, mock_db):
    from api.event import get_event_ids_by_category
    mock_db.session.query.return_value.filter.return_value.all.side_effect = [
        [MagicMock(id=1)], [MagicMock(id=2)], [MagicMock(id=3)], [MagicMock(id=4)], [MagicMock(id=5)], [MagicMock(id=6)]
    ]
    resp, code = get_event_ids_by_category()
    assert code == 200
    assert "sodium" in resp
