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