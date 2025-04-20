<template>
  <div class="audit-log">
    <AdminTopNavbar />
    <el-card class="box-card">
      <template v-slot:header>
        <div class="clearfix">
          <span>审计日志</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="float: right; margin-left: 10px;"
            @change="handleDateChange"
          />
          <el-select v-model="actionType" placeholder="操作类型" style="float: right; width: 120px;" @change="handleFilterChange">
            <el-option label="全部" value=""></el-option>
            <el-option label="登录" value="login"></el-option>
            <el-option label="添加用户" value="add_user"></el-option>
            <el-option label="修改用户" value="update_user"></el-option>
            <el-option label="删除用户" value="delete_user"></el-option>
          </el-select>
        </div>
      </template>
      
      <el-table :data="logs" v-loading="loading" style="width: 100%">
        <el-table-column prop="timestamp" label="时间" width="180">
          <template v-slot="scope">
            {{ formatDate(scope.row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="user_email" label="操作用户"></el-table-column>
        <el-table-column prop="action" label="操作类型">
          <template v-slot="scope">
            {{ getActionName(scope.row.action) }}
          </template>
        </el-table-column>
        <el-table-column prop="details" label="详细信息"></el-table-column>
        <el-table-column prop="ip_address" label="IP地址"></el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-size="pageSize"
          layout="total, prev, pager, next"
          :total="totalLogs"
        >
        </el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script>
import Axios from "@/utils/axios";
import { ElMessage } from 'element-plus';
import AdminTopNavbar from '@/components/AdminTopNavbar.vue';

export default {
  name: 'AuditLog',
  components: {
    AdminTopNavbar
  },
  data() {
    return {
      logs: [],
      loading: false,
      currentPage: 1,
      pageSize: 10,
      totalLogs: 0,
      dateRange: null,
      actionType: '',
      actionTypes: {
        login: '登录',
        add_user: '添加用户',
        update_user: '修改用户',
        delete_user: '删除用户'
      }
    };
  },
  created() {
    // 检查用户是否有权限访问此页面
    // this.checkAdminPermission();
    this.fetchLogs();
  },
  methods: {
    // 检查管理员权限
    checkAdminPermission() {
      const isAdmin = localStorage.getItem('isAdmin');
      if (isAdmin !== 'true') {
        ElMessage.error('您没有权限访问此页面');
        this.$router.push('/');
      }
    },
    // 获取审计日志数据
    async fetchLogs() {
      this.loading = true;
      try {
        // 构建查询参数
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        };
        
        if (this.actionType) {
          params.action_type = this.actionType;
        }
        
        if (this.dateRange && this.dateRange.length === 2) {
          params.start_date = this.formatDateForAPI(this.dateRange[0]);
          params.end_date = this.formatDateForAPI(this.dateRange[1]);
        }
        
        const response = await Axios.get('/audit_log/admin/audit-logs', { params });
        this.logs = response.data.logs;
        this.totalLogs = response.data.total;
      } catch (error) {
        ElMessage.error('获取审计日志失败');
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    
    // 格式化日期显示
    formatDate(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleString('zh-CN');
    },
    
    // 格式化日期为API参数
    formatDateForAPI(date) {
      return date.toISOString().split('T')[0];
    },
    
    // 获取操作类型名称
    getActionName(action) {
      return this.actionTypes[action] || action;
    },
    
    // 处理页码变化
    handleCurrentChange(page) {
      this.currentPage = page;
      this.fetchLogs();
    },
    
    // 处理日期范围变化
    handleDateChange() {
      this.currentPage = 1; // 重置到第一页
      this.fetchLogs();
    },
    
    // 处理筛选条件变化
    handleFilterChange() {
      this.currentPage = 1; // 重置到第一页
      this.fetchLogs();
    }
  }
};
</script>

<style scoped>
.audit-log {
  padding: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>