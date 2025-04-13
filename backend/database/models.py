"""The models for database."""
from common.extensions import db
from flask_jwt_extended import create_access_token
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import json

# User Model
class User(db.Model):
    """User model wrapper."""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
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
    

    def to_dict(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'email': self.email,
            'avatar': self.avatar,
            'is_admin': self.is_admin,
            'is_forbidden': self.is_forbidden,
        }

class Disease(db.Model):
    __tablename__ = 'disease'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 疾病名称
    description = db.Column(db.Text, nullable=True)  # 疾病描述
    target_event = db.Column(db.String(200), nullable=True)  # 预测目标事件
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间

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
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间

    disease = db.relationship('Disease', backref=db.backref('patients', lazy=True))
    # events = db.relationship('Event', backref=db.backref('patient', lazy=True))

    def to_dict(self):
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
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间

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
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间

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
        if key.category == 3 and precondition is not None:
            return precondition
        else:
            raise ValueError('The precondition should be None for category 1 and 2')
    
    @validates('event_id2')
    def validate_event_id2(self, key, event_id2):
        if self.category >= 2 and event_id2 is not None:
            return event_id2
        else:
            raise ValueError('The event_id2 should be None for category 1')
    



class PatientEvent(db.Model):
    __tablename__ = 'patient_event'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # 患者id
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)  # 事件id
    time = db.Column(db.DateTime, nullable=True)  # 事件发生时间
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间
    value = db.Column(db.Float, nullable=True)  # 事件数值

    patient = db.relationship('Patient', backref=db.backref('patient_events', lazy=True))
    event = db.relationship('Event', backref=db.backref('patient_events', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'patient': self.patient.to_dict(),
            'event': self.event.to_dict(),
            'time': self.time,
        }

class PatientRule(db.Model):
    __tablename__ = 'patient_rule'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # 患者id
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=False)  # 规则id
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间

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


    
class PatientCluster(db.Model):
    __tablename__ = 'patient_cluster'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    cluster_id = db.Column(db.Integer, nullable=False)  # 聚类结果
    time = db.Column(db.DateTime, nullable=True)  # 聚类代表的时间

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    patient = db.relationship('Patient', backref=db.backref('patient_clusters', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'patient': self.patient.to_dict(),
            'cluster_id': self.cluster_id,
            'time': self.time,
        }

