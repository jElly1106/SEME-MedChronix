"""CT扫描相关的路由处理。"""
from flask import Blueprint, request, jsonify
from common.extensions import db
from database.models import CTScan
from flask_jwt_extended import jwt_required
from datetime import datetime
from common.utils import upload_images
import os
ct_scan_bp = Blueprint('ct_scan', __name__)

@ct_scan_bp.route('/ct_scans', methods=['POST'])
@jwt_required()
def create_ct_scan():
    """创建新的CT扫描记录。"""
    try:
        data = request.form
        new_ct_scan = CTScan(
            patient_id=data['patient_id'],
            image_url='',
            ai_diagnosis=data.get('ai_diagnosis',''),
            diagnosis_date=datetime.strptime(data['diagnosis_date'], '%Y-%m-%d %H:%M:%S') if data.get('diagnosis_date') else None,
            status=data.get('status')
        )
        # 处理上传的图片
        image_file = request.files['ct_image']
        if not image_file:
            return jsonify({'message': '缺少CT扫描图片'}), 400
        # 假设upload_images是一个处理图片上传的函数
        file_path = upload_images(image_file, data['patient_id'],'ct_scans')
        if not file_path:
            return jsonify({'message': '上传CT扫描图片失败'}), 400
        new_ct_scan.image_url = file_path
        # 添加到数据库
        db.session.add(new_ct_scan)
        db.session.commit()
        return jsonify({'message': '成功创建CT扫描记录', 'data': new_ct_scan.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建CT扫描记录失败: {str(e)}'}), 400

@ct_scan_bp.route('/ct_scans/<int:ct_scan_id>', methods=['DELETE'])
@jwt_required()
def delete_ct_scan(ct_scan_id):
    """删除指定的CT扫描记录。"""
    try:
        ct_scan = CTScan.query.get_or_404(ct_scan_id)
        # 删除图片文件
        if ct_scan.image_url:
            # 但如果文件不存在，不报错
            try:
                os.remove(ct_scan.image_url)
            except FileNotFoundError:
                pass
            # 如果文件夹为空，可以选择删除文件夹
            folder_path = os.path.dirname(ct_scan.image_url)
            if not os.listdir(folder_path):
                os.rmdir(folder_path)
        # 删除数据库记录
        db.session.delete(ct_scan)
        db.session.commit()
        return jsonify({'message': '成功删除CT扫描记录'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除CT扫描记录失败: {str(e)}'}), 400

# @ct_scan_bp.route('/ct_scans/<int:ct_scan_id>', methods=['PUT'])
# @jwt_required()
# def update_ct_scan(ct_scan_id):
#     """更新指定的CT扫描记录。"""
#     try:
#         ct_scan = CTScan.query.get_or_404(ct_scan_id)
#         data = request.get_json()
        
#         if 'image_url' in data:
#             ct_scan.image_url = data['image_url']
#         if 'ai_diagnosis' in data:
#             ct_scan.ai_diagnosis = data['ai_diagnosis']
#         if 'diagnosis_date' in data:
#             ct_scan.diagnosis_date = datetime.strptime(data['diagnosis_date'], '%Y-%m-%d %H:%M:%S')
#         if 'status' in data:
#             ct_scan.status = data['status']
            
#         db.session.commit()
#         return jsonify({'message': '成功更新CT扫描记录', 'data': ct_scan.to_dict()}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'message': f'更新CT扫描记录失败: {str(e)}'}), 400

# @ct_scan_bp.route('/ct_scans/<int:ct_scan_id>', methods=['GET'])
# @jwt_required()
# def get_ct_scan(ct_scan_id):
#     """获取指定的CT扫描记录详情。"""
#     try:
#         ct_scan = CTScan.query.get_or_404(ct_scan_id)
#         return jsonify({'data': ct_scan.to_dict()}), 200
#     except Exception as e:
#         return jsonify({'message': f'获取CT扫描记录失败: {str(e)}'}), 400

@ct_scan_bp.route('/ct_scans/patient/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_ct_scans_by_patient(patient_id):
    """根据病人ID获取所有CT扫描记录。"""
    try:
        ct_scans = CTScan.query.filter_by(patient_id=patient_id).all()
        ct_scans_list = [ct.to_dict() for ct in ct_scans]
        return jsonify({'data': ct_scans_list}), 200
    except Exception as e:
        return jsonify({'message': f'根据病人ID获取CT扫描记录失败: {str(e)}'}), 400
    

# TODO: 还有一个前端调用AI大模型的接口在这里需要加一下，需要更新CTScan表的ai_diagnosis字段
# 添加新接口：更新CT扫描的AI诊断结果
@ct_scan_bp.route('/ct_scans/<int:ct_scan_id>/update_diagnosis', methods=['POST'])
@jwt_required()
def update_ct_scan_diagnosis(ct_scan_id):
    """更新指定CT扫描记录的AI诊断结果。"""
    try:
        ct_scan = CTScan.query.get_or_404(ct_scan_id)
        data = request.get_json()
        
        if 'ai_diagnosis' not in data:
            return jsonify({'message': '缺少AI诊断结果'}), 400
            
        ct_scan.ai_diagnosis = data['ai_diagnosis']
        db.session.commit()
        
        return jsonify({
            'message': '成功更新CT扫描的AI诊断结果', 
            'data': ct_scan.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新CT扫描AI诊断结果失败: {str(e)}'}), 400

# 添加新接口：获取CT扫描的AI诊断结果
@ct_scan_bp.route('/ct_scans/<int:ct_scan_id>/diagnosis', methods=['GET'])
@jwt_required()
def get_ct_scan_diagnosis(ct_scan_id):
    """获取指定CT扫描记录的AI诊断结果。"""
    try:
        ct_scan = CTScan.query.get_or_404(ct_scan_id)
        
        if not ct_scan.ai_diagnosis:
            return jsonify({
                'message': '该CT扫描暂无AI诊断结果',
                'has_diagnosis': False,
                'data': None
            }), 200
            
        return jsonify({
            'message': '成功获取CT扫描的AI诊断结果',
            'has_diagnosis': True,
            'data': {
                'id': ct_scan.id,
                'ai_diagnosis': ct_scan.ai_diagnosis
            }
        }), 200
    except Exception as e:
        return jsonify({'message': f'获取CT扫描AI诊断结果失败: {str(e)}'}), 400

