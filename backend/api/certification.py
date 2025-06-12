"""The route functions for the certification management."""
from flask import Blueprint, request, jsonify, current_app
from database.models import Certification, User, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.utils import upload_images
from common.decorators import admin_required
import json
from datetime import datetime
import os

certification_bp = Blueprint('certification', __name__)

@certification_bp.route('/get_my_certification', methods=['GET'])
@jwt_required()
def get_my_certification():
    """获取当前用户的资质认证信息"""
    # 从JWT中获取用户ID
    identity = json.loads(get_jwt_identity())
    user_id = identity['id']
    
    # 查询用户的认证信息
    certification = Certification.query.filter_by(user_id=user_id).first()
    
    if not certification:
        return jsonify({"message": "您尚未提交资质认证申请"}), 404
    
    # 返回认证信息
    return jsonify(certification.to_dict()), 200

@certification_bp.route('/submit_certification', methods=['POST'])
@jwt_required()
def submit_certification():
    """提交资质认证申请"""
    # 从JWT中获取用户ID
    identity = json.loads(get_jwt_identity())
    user_id = identity['id']
    
    # 检查用户是否已经提交过认证申请并且is_approved为False
    existing_certification = Certification.query.filter_by(user_id=user_id, is_approved=True).first()
    if existing_certification:
        return jsonify({"error": "您通过认证，无需重复认证"}), 400
    
    # 获取表单数据
    license_number = request.form.get('license_number')
    additional_documents = request.form.get('additional_documents')
    
    # 验证必填字段
    if not license_number:
        return jsonify({"error": "医师执业证书编号不能为空"}), 400
    
    # 处理上传的图片
    license_image = None
    work_proof = None
    
    if 'license_image' in request.files:
        license_image_file = request.files['license_image']
        license_image = upload_images(license_image_file, 'certifications')
    else:
        return jsonify({"error": "请上传医师执业证书图片"}), 400
    
    if 'work_proof' in request.files:
        work_proof_file = request.files['work_proof']
        work_proof = upload_images(work_proof_file, 'certifications')
    else:
        return jsonify({"error": "请上传医院工作证明"}), 400
    
    # 创建新的认证记录
    new_certification = Certification(
        user_id=user_id,
        license_number=license_number,
        license_image=license_image,
        work_proof=work_proof,
        additional_documents=additional_documents
    )
    
    # 更新用户的认证状态为待审核
    user = User.query.get(user_id)
    user.qualificationStatus = 'pending'     
    user.qualificationSubmitTime = datetime.now()
    
    # 保存到数据库
    db.session.add(new_certification)
    db.session.commit()
    return jsonify({
        "message": "资质认证申请提交成功，请等待管理员审核",
        "certification_id": new_certification.id,
        "qualificationSubmitTime":user.qualificationSubmitTime.strftime('%Y-%m-%d %H:%M:%S'),
        "qualificationStatus": user.qualificationStatus
    }), 201

@certification_bp.route('/get_all_certifications', methods=['GET'])
@admin_required
def get_all_certifications():
    """管理员获取所有资质认证申请（可按状态筛选）"""
    # 获取查询参数
    status = request.args.get('status')  # 可选参数，用于筛选认证状态
    
    # 构建查询
    query = Certification.query
    
    # 如果指定了状态，则按状态筛选
    if status:
        if status == 'pending':
            query = query.filter(Certification.is_approved == None)
        elif status == 'approved':
            query = query.filter(Certification.is_approved == True)
        elif status == 'rejected':
            query = query.filter(Certification.is_approved == False)
    
    # 执行查询
    certifications = query.all()
    
    # 构建结果列表
    result = []
    for cert in certifications:
        # 获取申请用户信息
        user = User.query.get(cert.user_id)
        cert_dict = cert.to_dict()
        cert_dict['user_nickname'] = user.nickname if user else "未知用户"
        cert_dict['user_email'] = user.email if user else "未知邮箱"
        result.append(cert_dict)
    
    return jsonify(result), 200

@certification_bp.route('/review_certification/<int:certification_id>', methods=['POST'])
@admin_required
def review_certification(certification_id):
    """管理员审核资质认证申请"""
    # 从JWT中获取管理员ID
    identity = json.loads(get_jwt_identity())
    admin_id = identity['id']
    
    # 获取认证记录
    certification = Certification.query.get(certification_id)
    if not certification:
        return jsonify({"error": "认证申请不存在"}), 404
    
    # 获取请求数据
    data = request.get_json()
    is_approved = data.get('is_approved')
    review_comment = data.get('review_comment', '')
    
    # 验证必填字段
    if is_approved is None:
        return jsonify({"error": "审核结果不能为空"}), 400
    
    # 更新认证记录
    certification.is_approved = is_approved
    certification.review_comment = review_comment
    certification.reviewer_id = admin_id
    certification.review_date = datetime.now()
    
    # 更新用户的认证状态
    user = User.query.get(certification.user_id)
    if user:
        user.qualificationStatus = 'approved' if is_approved else 'rejected'
        user.qualificationApproveTime = datetime.now() if is_approved else None
    
    # 保存到数据库
    db.session.commit()
    
    return jsonify({
        "message": "审核完成",
        "certification_id": certification_id,
        "is_approved": is_approved
    }), 200

@certification_bp.route('/get_certification_detail/<int:certification_id>', methods=['GET'])
@jwt_required()
def get_certification_detail(certification_id):
    """获取资质认证详情（管理员可查看所有，用户只能查看自己的）"""
    # 从JWT中获取用户ID和管理员状态
    identity = json.loads(get_jwt_identity())
    user_id = identity['id']
    is_admin = identity['is_admin']
    
    # 获取认证记录
    certification = Certification.query.get(certification_id)
    if not certification:
        return jsonify({"error": "认证申请不存在"}), 404
    
    # 检查权限：只有管理员或认证所有者可以查看详情
    if not is_admin and certification.user_id != user_id:
        return jsonify({"error": "您没有权限查看此认证申请"}), 403
    
    # 获取申请用户和审核人信息
    applicant = User.query.get(certification.user_id)
    reviewer = User.query.get(certification.reviewer_id) if certification.reviewer_id else None
    
    # 构建详细信息
    cert_dict = certification.to_dict()
    cert_dict['applicant_nickname'] = applicant.nickname if applicant else "未知用户"
    cert_dict['applicant_email'] = applicant.email if applicant else "未知邮箱"
    
    if reviewer:
        cert_dict['reviewer_nickname'] = reviewer.nickname
        cert_dict['reviewer_email'] = reviewer.email
    
    return jsonify(cert_dict), 200