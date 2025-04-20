"""The models for database."""
from common.extensions import db
from flask_jwt_extended import create_access_token
from flask import request
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import json

# 医院表单
class Hospital(db.Model):
    """医院信息表"""
    __tablename__ = 'hospital'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 医院名称
    region = db.Column(db.String(100), nullable=False)  # 医院所在地区
    created_at = db.Column(db.DateTime, default=datetime.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())  # 更新时间
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'region': self.region,
        }

# User Model
class User(db.Model):
    """User model wrapper."""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(256))
    qualificationStatus = db.Column(db.String(20),default='initial') #是否完成医师认证# 'approved','pending','rejected'
    qualificationSubmitTime = db.Column(db.DateTime, default=datetime.now(), nullable=True) # 提交时间
    qualificationApproveTime = db.Column(db.DateTime, default=datetime.now(), nullable=True) # 审核时间
    is_admin = db.Column(db.Boolean, default=False)
    hospital = db.Column(db.String(100), default='暂无',nullable=True)    # 所属医院名字
    department = db.Column(db.String(100), default='暂无',nullable=True)  # 所属科室
    title = db.Column(db.String(100), default='暂无',nullable=True) # 职称
    is_forbidden = db.Column(db.Boolean, default=False)

    
    def set_password(self, password: str):
        """Set the password.

        Args:
            password (str): The string for the password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        """The validation for the password.

        Args:
            password (str): The string for the password.
        """
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self):
        """Generate JWT for user authentication
        
        Returns:
            token (str): The JWT string.
        """
        identity_data = json.dumps({'id': self.id, 'is_admin': self.is_admin})
        return create_access_token(identity=identity_data)
    
    @validates
    def check_qualificationStatus(self, key, value):
        if value in ['initial','approved', 'pending', 'rejected']:
            return value
        else:
            raise ValueError('The qualificationStatus should be initial, approved, pending or rejected')
    
    def to_dict(self):
        if self.avatar:
            avatar_url = f"{request.host_url}{self.avatar}"
        else:
            avatar_url = None
        return {
            'id': self.id,
            'nickname': self.nickname,
            'email': self.email,
            'avatar': avatar_url,
            'qualificationStatus': self.qualificationStatus,
            'qualificationSubmitTime': self.qualificationSubmitTime.strftime('%Y-%m-%d %H:%M:%S') if self.qualificationSubmitTime else None,
            'qualificationApproveTime': self.qualificationApproveTime.strftime('%Y-%m-%d %H:%M:%S') if self.qualificationApproveTime else None,
            'is_admin': self.is_admin,
            'hospital': self.hospital,
            'department': self.department,
            'title':self.title
        }

# 医师资质认证表单
class Certification(db.Model):
    """医师资质认证表"""
    __tablename__ = 'certification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 用户ID
    license_number = db.Column(db.String(100), nullable=False)  # 医师执业证书编号
    license_image = db.Column(db.String(256), nullable=False)  # 医师执业证书图片
    work_proof = db.Column(db.String(256), nullable=False)  # 医院工作证明
    additional_documents = db.Column(db.Text, nullable=True)  # 其他补充资料
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 审核人ID
    review_comment = db.Column(db.Text, nullable=True)  # 审核意见
    is_approved = db.Column(db.Boolean, default=None, nullable=True)  # 是否通过审核
    review_date = db.Column(db.DateTime, nullable=True)  # 审核日期
    created_at = db.Column(db.DateTime, default=datetime.now())  # 创建时间
    
    def to_dict(self):
        if self.license_image:
            license_image_url = f"{request.host_url}{self.license_image}"
        else:
            license_image_url = None
        if self.work_proof:
            work_proof_url = f"{request.host_url}{self.work_proof}"
        else:
            work_proof_url = None
        return {
            'id': self.id,
            'user_id': self.user_id,
            'license_number': self.license_number,
            'license_image': license_image_url,
            'work_proof': work_proof_url,
            'additional_documents': self.additional_documents,
            'reviewer_id': self.reviewer_id,
            'review_comment': self.review_comment,
            'is_approved': self.is_approved,
            'review_date': self.review_date,
            'created_at': self.created_at,
        }

class Disease(db.Model):
    __tablename__ = 'disease'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 疾病名称
    description = db.Column(db.Text, nullable=True)  # 疾病描述
    target_event = db.Column(db.String(200), nullable=True)  # 预测目标事件
    created_at = db.Column(db.DateTime, default=datetime.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())  # 更新时间

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_event': self.target_event,
        }


class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey('disease.id'), nullable=False)  # 外键，关联到疾病
    name = db.Column(db.String(100), nullable=False)  # 患者姓名
    gender = db.Column(db.String(10), nullable=True)  # 性别
    age = db.Column(db.Integer, nullable=True)  # 年龄
    heart_history = db.Column(db.Text, nullable=True)  # 心脏病史
    diabete_history = db.Column(db.Text, nullable=True)  # 糖尿病史
    EH_history = db.Column(db.Text, nullable=True) # 高血压史
    other_history = db.Column(db.Text, nullable=True)  # 其他病史
    status = db.Column(db.String(50), nullable=True)  # 疾病状态
    in_icu = db.Column(db.DateTime, nullable=True)  # 入ICU时间
    out_icu = db.Column(db.DateTime, nullable=True)  # 出ICU时间
    # disease_stage = db.Column(db.String(50), nullable=True)  # 疾病阶段
    created_at = db.Column(db.DateTime, default=datetime.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())  # 更新时间

    disease = db.relationship('Disease', backref=db.backref('patients', lazy=True))
    # events = db.relationship('Event', backref=db.backref('patient', lazy=True))

    def to_dict(self):
        def format_datetime(dt):
            if dt:
                try:
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, AttributeError):
                    return None
            return None
        return {
            'id': self.id,
            'name': self.name,
            'desease': self.disease.to_dict(),
            'gender': self.gender,
            'age': self.age,
            'heart_history': self.heart_history,
            'diabete_history': self.diabete_history,
            'Eh_history': self.EH_history,
            'other_history': self.other_history,
            'status': self.status,
            'in_icu': format_datetime(self.in_icu),
            'out_icu': format_datetime(self.out_icu)
        }



# 异常事件
class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 事件名称
    description = db.Column(db.Text, nullable=True)  # 事件描述
    max_value = db.Column(db.Float, nullable=True)  # 最大值
    min_value = db.Column(db.Float, nullable=True)  # 最小值
    unit = db.Column(db.String(50), nullable=True)  # 单位
    disease_id = db.Column(db.Integer, db.ForeignKey('disease.id'), nullable=False)  # 疾病id
    created_at = db.Column(db.DateTime, default=datetime.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())  # 更新时间

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'max_value': self.max_value,
            'min_value': self.min_value,
            'unit': self.unit,
            'disease': self.disease.to_dict(),
        }


class Precondition(db.Model):
    __tablename__ = 'precondition'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)  # 前置条件描述

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
        }
    
# 疾病预测规则
class Rule(db.Model):
    __tablename__ = 'rule'
    id = db.Column(db.Integer, primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey('disease.id'), nullable=False)  # 疾病id
    name = db.Column(db.String(100), nullable=False)  # 规则名称
    # description = db.Column(db.Text, nullable=True)  # 规则描述
    weight = db.Column(db.Float, nullable=False)  # 权重
    category = db.Column(db.Integer, nullable=False)  # 类别
    precondition = db.Column(db.Integer, db.ForeignKey('precondition.id'), nullable=True)  # 前置条件
    event_id1 = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)  # 事件1id
    event_id2 = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)  # 事件2id
    time_delta = db.Column(db.Float, nullable=True)  # 时间差/小时
    created_at = db.Column(db.DateTime, default=datetime.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())  # 更新时间

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'weight': self.weight,
        }

    @validates('category')
    def validate_category(self, key, category):
        if category in [1, 2, 3]:
            return category
        else:
            raise ValueError('The category should be 1, 2 or 3')

    @validates('precondition')
    def validate_precondition(self, key, precondition):
        if self.category == 3:
            if precondition is None:
                raise ValueError('对于类别3，必须提供前置条件')
            return precondition
        else:
            if precondition is not None:
                raise ValueError('对于类别1和2，前置条件必须为None')
            return None

    
    @validates('event_id2')
    def validate_event_id2(self, key, event_id2):
        if self.category >= 2:
            if event_id2 is None:
                raise ValueError('对于类别2,3，必须提供事件2')
            return event_id2
        else:
            if event_id2 is not None:
                raise ValueError('对于类别1，事件2必须为None')
            return None
    



class PatientEvent(db.Model):
    __tablename__ = 'patient_event'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # 患者id
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)  # 事件id
    time = db.Column(db.DateTime, nullable=True)  # 事件发生时间
    value=db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())  # 更新时间

    patient = db.relationship('Patient', backref=db.backref('patient_events', lazy=True))
    event = db.relationship('Event', backref=db.backref('patient_events', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'patient': self.patient.to_dict(),
            'event': self.event.to_dict(),
            'time': self.time,
            'value': self.value,
        }

class PatientRule(db.Model):
    __tablename__ = 'patient_rule'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # 患者id
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=False)  # 规则id
    created_at = db.Column(db.DateTime, default=datetime.now())  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())  # 更新时间

    patient = db.relationship('Patient', backref=db.backref('patient_rules', lazy=True))
    rule = db.relationship('Rule', backref=db.backref('patient_rules', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'patient': self.patient.to_dict(),
            'rule': self.rule.to_dict(),
            'description': self.description,
            'status': self.status,
        }


class PatientCase(db.Model):
    __tablename__ = 'patient_case'
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(100), nullable=False, unique=True)  # 病例编号
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # 患者id
    visit_time = db.Column(db.DateTime, nullable=False)  # 就诊时间
    visit_location = db.Column(db.String(200), nullable=True)  # 就诊地点
    doctor_notes = db.Column(db.Text, nullable=True)  # 医生记录
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间

    # 建立与 Patient 表的关系
    patient = db.relationship('Patient', backref=db.backref('cases', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'case_number': self.case_number,
            'patient_id': self.patient_id,
            'visit_time': self.visit_time,
            'visit_location': self.visit_location,
            'doctor_notes': self.doctor_notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class PatientCluster(db.Model):
    __tablename__ = 'patient_cluster'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    cluster_id = db.Column(db.Integer, nullable=False)  # 聚类结果
    time = db.Column(db.Float, nullable=True)  # 聚类代表的时间

    created_at = db.Column(db.DateTime, default=datetime.now())  # 创建时间
    patient = db.relationship('Patient', backref=db.backref('patient_clusters', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'patient': self.patient.to_dict(),
            'cluster_id': self.cluster_id,
            'time': self.time,
        }
# 患者事件预测表
class PatientPrediction(db.Model):
    __tablename__ = 'patient_prediction'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # 患者id
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)  # 事件id
    time = db.Column(db.DateTime, nullable=True)  # 预测事件发生时间
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间

    patient = db.relationship('Patient', backref=db.backref('patient_predictions', lazy=True))
    event = db.relationship('Event', backref=db.backref('patient_predictions', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'patient': self.patient.to_dict(),
            'event': self.event.to_dict(),
            'time': self.time.strftime('%Y-%m-%d %H:%M:%S') if self.time else None,
        }

# 事件预测概率表
class EventPrediction(db.Model):
    __tablename__ = 'event_prediction'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # 患者id
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)  # 事件id
    probability = db.Column(db.Float, nullable=True)  # 预测概率
    time = db.Column(db.DateTime, nullable=True)  # 预测事件发生时间
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间

    patient = db.relationship('Patient', backref=db.backref('event_predictions', lazy=True))
    event = db.relationship('Event', backref=db.backref('event_predictions', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'patient': self.patient.to_dict(),
            'event': self.event.to_dict(),
            'probability': self.probability,
            'time': self.time.strftime('%Y-%m-%d %H:%M:%S') if self.time else None,
        }

# CT图像病例表
class CTScan(db.Model):
    __tablename__ = 'ct_scan'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # 患者id
    image_url = db.Column(db.String(256), nullable=False)  # CT图像URL
    ai_diagnosis = db.Column(db.Text, nullable=True)  # AI诊断结果
    diagnosis_date = db.Column(db.DateTime, nullable=True)  # 诊断日期
    status = db.Column(db.String(10), nullable=True)  # 正常/异常

    patient = db.relationship('Patient', backref=db.backref('ct_scans', lazy=True))

    def to_dict(self):
        if self.image_url:
            image_url = f"{request.host_url}{self.image_url}"
        else:
            image_url = None
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'image_url': image_url,
            'ai_diagnosis': self.ai_diagnosis,
            'diagnosis_date': self.diagnosis_date.strftime('%Y-%m-%d %H:%M:%S') if self.diagnosis_date else None,
            'status': self.status,
        }

# 修改 AuditLog 类定义
class AuditLog(db.Model):
    """审计日志模型类"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)  # 操作用户ID，可能为空（如未登录用户）
    user_email = db.Column(db.String(100), nullable=True)  # 操作用户邮箱
    action = db.Column(db.String(50), nullable=False)  # 操作类型
    details = db.Column(db.Text, nullable=True)  # 操作详情
    ip_address = db.Column(db.String(50), nullable=True)  # IP地址
    user_agent = db.Column(db.String(255), nullable=True)  # 用户代理
    timestamp = db.Column(db.DateTime, default=datetime.now)  # 操作时间
    
    def __init__(self, user_id=None, user_email=None, action=None, details=None, 
                 ip_address=None, user_agent=None):
        self.user_id = user_id
        self.user_email = user_email
        self.action = action
        self.details = details
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.timestamp = datetime.now()
    
    def to_dict(self):
        """将对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat()
        }