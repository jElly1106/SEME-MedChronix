"""数据访问层，提供统一的数据操作接口"""
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
import logging

class DataAccess:
    """数据访问类，提供统一的数据操作方法"""
    
    @staticmethod
    def get_db():
        """获取数据库实例"""
        return current_app.config['db']
    
    @staticmethod
    def add(model_instance):
        """添加数据
        
        Args:
            model_instance: 模型实例
            
        Returns:
            bool: 操作是否成功
        """
        try:
            db = DataAccess.get_db()
            db.session.add(model_instance)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"数据添加失败: {str(e)}")
            return False
    
    @staticmethod
    def update():
        """更新数据
        
        Returns:
            bool: 操作是否成功
        """
        try:
            db = DataAccess.get_db()
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"数据更新失败: {str(e)}")
            return False
    
    @staticmethod
    def delete(model_instance):
        """删除数据
        
        Args:
            model_instance: 模型实例
            
        Returns:
            bool: 操作是否成功
        """
        try:
            db = DataAccess.get_db()
            db.session.delete(model_instance)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"数据删除失败: {str(e)}")
            return False
    
    @staticmethod
    def query(model_class, **filters):
        """查询数据
        
        Args:
            model_class: 模型类
            **filters: 过滤条件
            
        Returns:
            查询结果
        """
        try:
            return model_class.query.filter_by(**filters).all()
        except SQLAlchemyError as e:
            logging.error(f"数据查询失败: {str(e)}")
            return []