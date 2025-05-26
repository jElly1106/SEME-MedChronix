from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import Certification, User, db
from common.utils import upload_images
from common.decorators import admin_required
from datetime import datetime
import json

# ==========================
# Blueprint 初始化
# ==========================
certification_bp = Blueprint('certification', __name__)

# ==========================
# 工具函数
# ==========================

# 格式化返回响应结果
def format_response(code=200, message="Success", data=None):
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    }), code

# 从 JWT 中解析当前用户身份信息
def get_current_user():
    identity = json.loads(get_jwt_identity())
    return identity.get("id"), identity.get("is_admin", False)

# ==========================
# 用户端接口：获取自己的认证记录
# ==========================
@certification_bp.route('/get_my_certification', methods=['GET'])
@jwt_required()
def get_my_certification():
    user_id, _ = get_current_user()
    certification = Certification.query.filter_by(user_id=user_id).first()
    if not certification:
        return format_response(404, "您尚未提交资质认证申请")
    return format_response(data=certification.to_dict())

# ==========================
# 用户端接口：提交资质认证申请
# ==========================
@certification_bp.route('/submit_certification', methods=['POST'])
@jwt_required()
def submit_certification():
    user_id, _ = get_current_user()

    # 检查是否已经认证通过
    existing = Certification.query.filter_by(user_id=user_id, is_approved=True).first()
    if existing:
        return format_response(400, "您已通过认证，无需重复提交")

    # 提取表单字段
    license_number = request.form.get('license_number')
    additional_documents = request.form.get('additional_documents')

    if not license_number:
        return format_response(400, "医师执业证书编号不能为空")

    # 验证是否上传了图片
    if 'license_image' not in request.files or 'work_proof' not in request.files:
        return format_response(400, "请上传必要的认证图片")

    # 上传图片
    license_image = upload_images(request.files['license_image'], 'certifications')
    work_proof = upload_images(request.files['work_proof'], 'certifications')

    # 创建认证记录
    cert = Certification(
        user_id=user_id,
        license_number=license_number,
        license_image=license_image,
        work_proof=work_proof,
        additional_documents=additional_documents
    )

    # 设置用户认证状态为待审核
    user = User.query.get(user_id)
    user.qualificationStatus = 'pending'
    user.qualificationSubmitTime = datetime.now()

    db.session.add(cert)
    db.session.commit()

    return format_response(201, "资质认证申请提交成功，请等待管理员审核", {
        "certification_id": cert.id,
        "qualificationSubmitTime": user.qualificationSubmitTime.strftime('%Y-%m-%d %H:%M:%S'),
        "qualificationStatus": user.qualificationStatus
    })

# ==========================
# 管理员接口：获取所有认证申请（支持筛选）
# ==========================
@certification_bp.route('/get_all_certifications', methods=['GET'])
@admin_required
def get_all_certifications():
    status = request.args.get('status')
    query = Certification.query

    # 按认证状态筛选
    if status == 'pending':
        query = query.filter(Certification.is_approved == None)
    elif status == 'approved':
        query = query.filter(Certification.is_approved == True)
    elif status == 'rejected':
        query = query.filter(Certification.is_approved == False)

    certs = query.all()
    result = []

    for c in certs:
        user = User.query.get(c.user_id)
        cert_dict = c.to_dict()
        cert_dict["user_nickname"] = user.nickname if user else "未知用户"
        cert_dict["user_email"] = user.email if user else "未知邮箱"
        result.append(cert_dict)

    return format_response(data=result)

# ==========================
# 管理员接口：审核认证申请
# ==========================
@certification_bp.route('/review_certification/<int:certification_id>', methods=['POST'])
@admin_required
def review_certification(certification_id):
    admin_id, _ = get_current_user()

    certification = Certification.query.get(certification_id)
    if not certification:
        return format_response(404, "认证申请不存在")

    data = request.get_json()
    is_approved = data.get('is_approved')
    review_comment = data.get('review_comment', '')

    if is_approved is None:
        return format_response(400, "审核结果不能为空")

    # 更新审核记录
    certification.is_approved = is_approved
    certification.review_comment = review_comment
    certification.reviewer_id = admin_id
    certification.review_date = datetime.now()

    # 同步更新用户认证状态
    user = User.query.get(certification.user_id)
    if user:
        user.qualificationStatus = 'approved' if is_approved else 'rejected'
        if is_approved:
            user.qualificationApproveTime = datetime.now()

    db.session.commit()

    return format_response(message="审核完成", data={
        "certification_id": certification_id,
        "is_approved": is_approved
    })

# ==========================
# 通用接口（用户/管理员）：获取认证申请详情
# ==========================
@certification_bp.route('/get_certification_detail/<int:certification_id>', methods=['GET'])
@jwt_required()
def get_certification_detail(certification_id):
    user_id, is_admin = get_current_user()
    cert = Certification.query.get(certification_id)

    if not cert:
        return format_response(404, "认证申请不存在")

    # 非管理员不能查看他人申请记录
    if not is_admin and cert.user_id != user_id:
        return format_response(403, "您无权限查看此申请")

    applicant = User.query.get(cert.user_id)
    reviewer = User.query.get(cert.reviewer_id) if cert.reviewer_id else None

    detail = cert.to_dict()
    detail["applicant_nickname"] = applicant.nickname if applicant else "未知用户"
    detail["applicant_email"] = applicant.email if applicant else "未知邮箱"

    if reviewer:
        detail["reviewer_nickname"] = reviewer.nickname
        detail["reviewer_email"] = reviewer.email

    return format_response(data=detail)
