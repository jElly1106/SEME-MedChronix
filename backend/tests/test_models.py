from database.models import User, Disease, Patient, Certification

def test_user_to_dict_all_fields():
    u = User(nickname="张三", email="zs@test.com", is_admin=True)
    d = u.to_dict()
    assert "nickname" in d and "is_admin" in d

def test_patient_to_dict_edge():
    d = Disease(name="脑卒中")
    p = Patient(name="小李", disease_id=1, disease=d)
    res = p.to_dict()
    assert res["name"] == "小李"
    assert isinstance(res["desease"], dict)
    p.in_icu = None
    p.out_icu = None
    assert p.to_dict()["in_icu"] is None

def test_certification_to_dict_partial():
    c = Certification(user_id=1, license_number="111", license_image="img.jpg", work_proof="")
    result = c.to_dict()
    assert result["user_id"] == 1
