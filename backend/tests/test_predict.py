import pytest
from unittest.mock import patch, MagicMock
from api.predict import query_and_prepare_data

def test_query_and_prepare_data_normal(tmp_path):
    fake_event = MagicMock()
    fake_event.patient.id = 1
    fake_event.time = 1.0
    fake_event.event.id = 1
    fake_event.event.name = "发热"
    fake_event.patient.heart_history = 1
    fake_event.patient.diabate_history = 1
    fake_event.patient.EH_history = 0
    with patch("api.predict.PatientEvent.query") as mock_query:
        mock_query.options.return_value.filter.return_value.all.return_value = [fake_event]
        outfile = tmp_path / "test.pkl"
        query_and_prepare_data(str(outfile), 1)
        assert outfile.exists()

def test_query_and_prepare_data_no_patient(tmp_path):
    with patch("api.predict.PatientEvent.query") as mock_query:
        mock_query.options.return_value.filter.return_value.all.return_value = []
        outfile = tmp_path / "empty.pkl"
        query_and_prepare_data(str(outfile), 999)
        assert outfile.exists()

def test_query_and_prepare_data_df_exception(tmp_path):
    fake_event = MagicMock()
    fake_event.patient.id = 1
    fake_event.time = 1.0
    fake_event.event.id = 1
    fake_event.event.name = "发热"
    fake_event.patient.heart_history = 1
    fake_event.patient.diabate_history = 1
    fake_event.patient.EH_history = 0
    with patch("api.predict.PatientEvent.query") as mock_query, \
         patch("api.predict.pd.DataFrame", side_effect=Exception("DataFrame error")):
        mock_query.options.return_value.filter.return_value.all.return_value = [fake_event]
        with pytest.raises(Exception):
            query_and_prepare_data(str(tmp_path / "fail.pkl"), 1)
