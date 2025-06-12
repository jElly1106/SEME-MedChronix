<<<<<<< HEAD
<<<<<<< HEAD
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from datetime import datetime
from sqlalchemy import desc
from database.models import AuditLog
from common.decorators import admin_required

audit_log_bp = Blueprint('audit_log', __name__)

@audit_log_bp.route('/admin/audit-logs', methods=['GET'])
@jwt_required()
# @admin_required
def get_audit_logs():
    """获取审计日志列表（仅管理员可用）
    
    Returns:
        包含审计日志列表和总数的JSON对象
    """
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    
    # 获取筛选参数
    action_type = request.args.get('action_type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # 构建查询
    db = current_app.config['db']
    query = db.session.query(AuditLog)
    
    # 应用筛选条件
    if action_type:
        query = query.filter(AuditLog.action == action_type)
    
    if start_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(AuditLog.timestamp >= start_datetime)
    
    if end_date:
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        query = query.filter(AuditLog.timestamp <= end_datetime)
    
    # 获取总记录数
    total = query.count()
    
    # 应用排序和分页
    logs = query.order_by(desc(AuditLog.timestamp)).offset((page - 1) * page_size).limit(page_size).all()
    
    # 转换为字典列表
    logs_dict = [log.to_dict() for log in logs]
    
    return jsonify({
        'logs': logs_dict,
        'total': total
    }), 200

# 记录审计日志的辅助函数
def log_activity(user_id, user_email, action, details=None):
    """记录用户活动到审计日志
    
    Args:
        user_id: 用户ID
        user_email: 用户邮箱
        action: 操作类型
        details: 操作详情
    """
    try:
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        db = current_app.config['db']
        log = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(log)
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"记录审计日志失败: {str(e)}")
        return False
=======
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import desc
from database.models import AuditLog
from common.decorators import admin_required

# ==========================
# Blueprint 初始化
# ==========================
audit_log_bp = Blueprint('audit_log', __name__)

# ==========================
# 工具函数
# ==========================

# 格式化通用响应结构
def format_response(code=200, message="Success", data=None):
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    }), code

# 安全解析日期字符串为 datetime 对象（支持是否设置为当天结束时间）
def parse_date_safe(date_str, with_end=False):
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        if with_end:
            dt = dt.replace(hour=23, minute=59, second=59)
        return dt
    except Exception:
        return None

# ==========================
# 审计日志查询接口（仅限管理员）
# ==========================

@audit_log_bp.route('/admin/audit-logs', methods=['GET'])
@jwt_required()
# @admin_required  # 可根据实际需求开启管理员验证
def get_audit_logs():
    """
    获取审计日志列表

    功能说明：
    - 提供分页查询审计日志的能力
    - 支持按行为类型（action_type）与日期范围（start_date/end_date）筛选
    - 结果按时间倒序排列

    查询参数（Query Params）:
    - page: 页码（默认1）
    - page_size: 每页条数（默认10）
    - action_type: 行为类型过滤（可选）
    - start_date: 起始日期，格式 'YYYY-MM-DD'（可选）
    - end_date: 截止日期，格式 'YYYY-MM-DD'（可选）

    返回：
    - JSON 格式的日志列表及总数
    """
    db = current_app.config['db']

    # 分页参数处理
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
    except ValueError:
        page, page_size = 1, 10

    # 获取筛选参数
    action_type = request.args.get('action_type', '').strip()
    start_date = parse_date_safe(request.args.get('start_date', ''))
    end_date = parse_date_safe(request.args.get('end_date', ''), with_end=True)

    # 构建查询
    query = db.session.query(AuditLog)
    if action_type:
        query = query.filter(AuditLog.action == action_type)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)

    total = query.count()

    # 分页 + 排序
    logs = query.order_by(desc(AuditLog.timestamp))\
                .offset((page - 1) * page_size)\
                .limit(page_size)\
                .all()

    # 转换为字典用于 JSON 返回
    logs_dict = [log.to_dict() for log in logs]

    return format_response(data={
        "logs": logs_dict,
        "total": total
    })

# ==========================
# 审计日志记录函数（在用户行为关键点调用）
# ==========================

def log_activity(user_id, user_email, action, details=None):
    """
    记录用户行为至审计日志表

    功能说明：
    - 在用户执行重要操作时记录其行为信息，提升系统可追踪性与安全性
    - 自动采集请求IP和User-Agent
    - 建议在登录、修改、删除、审批等动作中调用本函数

    参数：
    - user_id: 用户唯一标识
    - user_email: 用户邮箱
    - action: 操作类型（如 'login', 'edit_profile', 'approve_cert' 等）
    - details: 操作具体说明（可选）

    返回：
    - True 表示记录成功，False 表示失败（并写入日志）
    """
    try:
        db = current_app.config['db']
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')

        # 构建日志对象
        log = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.session.add(log)
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"[AuditLog] 记录失败: {str(e)}")
        return False
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
=======
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import desc
from database.models import AuditLog
from common.decorators import admin_required

# ==========================
# Blueprint 初始化
# ==========================
audit_log_bp = Blueprint('audit_log', __name__)

# ==========================
# 工具函数
# ==========================

# 格式化通用响应结构
def format_response(code=200, message="Success", data=None):
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    }), code

# 安全解析日期字符串为 datetime 对象（支持是否设置为当天结束时间）
def parse_date_safe(date_str, with_end=False):
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        if with_end:
            dt = dt.replace(hour=23, minute=59, second=59)
        return dt
    except Exception:
        return None

# ==========================
# 审计日志查询接口（仅限管理员）
# ==========================

@audit_log_bp.route('/admin/audit-logs', methods=['GET'])
@jwt_required()
# @admin_required  # 可根据实际需求开启管理员验证
def get_audit_logs():
    """
    获取审计日志列表

    功能说明：
    - 提供分页查询审计日志的能力
    - 支持按行为类型（action_type）与日期范围（start_date/end_date）筛选
    - 结果按时间倒序排列

    查询参数（Query Params）:
    - page: 页码（默认1）
    - page_size: 每页条数（默认10）
    - action_type: 行为类型过滤（可选）
    - start_date: 起始日期，格式 'YYYY-MM-DD'（可选）
    - end_date: 截止日期，格式 'YYYY-MM-DD'（可选）

    返回：
    - JSON 格式的日志列表及总数
    """
    db = current_app.config['db']

    # 分页参数处理
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
    except ValueError:
        page, page_size = 1, 10

    # 获取筛选参数
    action_type = request.args.get('action_type', '').strip()
    start_date = parse_date_safe(request.args.get('start_date', ''))
    end_date = parse_date_safe(request.args.get('end_date', ''), with_end=True)

    # 构建查询
    query = db.session.query(AuditLog)
    if action_type:
        query = query.filter(AuditLog.action == action_type)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)

    total = query.count()

    # 分页 + 排序
    logs = query.order_by(desc(AuditLog.timestamp))\
                .offset((page - 1) * page_size)\
                .limit(page_size)\
                .all()

    # 转换为字典用于 JSON 返回
    logs_dict = [log.to_dict() for log in logs]

    return format_response(data={
        "logs": logs_dict,
        "total": total
    })

# ==========================
# 审计日志记录函数（在用户行为关键点调用）
# ==========================

def log_activity(user_id, user_email, action, details=None):
    """
    记录用户行为至审计日志表

    功能说明：
    - 在用户执行重要操作时记录其行为信息，提升系统可追踪性与安全性
    - 自动采集请求IP和User-Agent
    - 建议在登录、修改、删除、审批等动作中调用本函数

    参数：
    - user_id: 用户唯一标识
    - user_email: 用户邮箱
    - action: 操作类型（如 'login', 'edit_profile', 'approve_cert' 等）
    - details: 操作具体说明（可选）

    返回：
    - True 表示记录成功，False 表示失败（并写入日志）
    """
    try:
        db = current_app.config['db']
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')

        # 构建日志对象
        log = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.session.add(log)
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"[AuditLog] 记录失败: {str(e)}")
        return False
>>>>>>> parent of 4eedc2b (feat-2026/06/06)
