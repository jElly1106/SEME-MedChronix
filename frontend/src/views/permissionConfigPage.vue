<template>
  <div class="permission-config">
    <AdminTopNavbar />
    <el-card class="box-card">
      <template v-slot:header>
        <div class="clearfix">
          <span>权限配置</span>
          <el-button style="float: right; padding: 3px 0" type="text" @click="handleAddUser">添加用户</el-button>
        </div>
      </template>
      
      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="email" label="邮箱"></el-table-column>
        <el-table-column prop="nickname" label="昵称"></el-table-column>
        <el-table-column prop="is_admin" label="角色">
          <template v-slot="scope">
            {{ getRoleName(scope.row.is_admin) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template v-slot="scope">
            <div class="action-buttons">
              <button class="edit-btn" @click.stop=handleEdit(scope.row)>
                  <i class="fa fa-edit"></i>
              </button>
              <button class="delete-btn" @click="handleDelete(scope.row)">
                  <i class="fa fa-trash"></i>
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑用户权限对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="30%">
      <el-form :model="form" :rules="rules" ref="form" label-width="80px">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" :disabled="isEdit"></el-input>
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" type="password"></el-input>
        </el-form-item>
        <el-form-item label="角色" prop="is_admin">
          <el-select v-model="form.is_admin" placeholder="请选择角色">
            <el-option v-for="item in roleOptions" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template v-slot:footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import Axios from "@/utils/axios";
import { ElMessageBox } from 'element-plus'; // 添加这一行导入
import AdminTopNavbar from "@/components/AdminTopNavbar";

export default {
  name: 'PermissionConfig',
  components: {
    AdminTopNavbar, 
  },
  data() {
    return {
      users: [],
      loading: false,
      dialogVisible: false,
      isEdit: false,
      dialogTitle: '添加用户',
      form: {
        id: null,
        email: '',
        nickname: '',
        password: '',
        is_admin: false
      },
      rules: {
        email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
        nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
        is_admin: [{ required: true, message: '请选择角色', trigger: 'change' }]
      },
      roleOptions: [
        { label: '管理员', value: true },
        { label: '普通用户', value: false }
      ]
    };
  },
  created() {
    this.fetchUsers();
  },
  methods: {
    // 获取所有用户数据
    async fetchUsers() {
      this.loading = true;
      try {
        const response = await Axios.get('/user/admin/users');
        this.users = response.data;
      } catch (error) {
        this.$message.error('获取用户列表失败');
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
    
    // 获取角色名称
    getRoleName(is_admin) {
      return is_admin ? '管理员' : '普通用户';
    },
    
    // 添加用户
    handleAddUser() {
      this.isEdit = false;
      this.dialogTitle = '添加用户';
      this.form = {
        email: '',
        nickname: '',
        password: '',
        is_admin: false
      };
      this.dialogVisible = true;
    },
    
    // 编辑用户
    handleEdit(row) {
      this.isEdit = true;
      this.dialogTitle = '编辑用户';
      this.form = {
        id: row.id,
        email: row.email,
        nickname: row.nickname,
        password: '',
        is_admin: row.is_admin
      };
      this.dialogVisible = true;
    },
    
    // 删除用户
    // 删除用户
    async handleDelete(row) {
      try {
        // 使用 ElMessageBox.confirm 替代 this.$confirm
        await ElMessageBox.confirm('确认删除该用户?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        
        // 用户点击确认按钮后执行
        await Axios.delete(`/user/admin/users/${row.id}`);
        this.$message.success('删除成功');
        this.fetchUsers();
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败');
          console.error(error);
        }
      }
    },
    
    // 提交表单
    submitForm() {
      this.$refs.form.validate(async (valid) => {
        if (valid) {
          try {
            if (this.isEdit) {
              // 更新用户
              await Axios.put(`/user/admin/users/${this.form.id}`, {
                nickname: this.form.nickname,
                is_admin: this.form.is_admin
              });
              this.$message.success('更新成功');
            } else {
              // 添加用户
              await Axios.post('/user/admin/users', this.form);
              this.$message.success('添加成功');
            }
            this.dialogVisible = false;
            this.fetchUsers();
          } catch (error) {
            this.$message.error(this.isEdit ? '更新失败' : '添加失败');
            console.error(error);
          }
        }
      });
    }
  }
};
</script>

<style scoped>
.permission-config {
  padding: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.edit-btn,
.delete-btn {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-btn {
  background-color: #e7f5ff;
  color: #1c7ed6;
}

.edit-btn:hover {
  background-color: #d0ebff;
}

.delete-btn {
  background-color: #fff5f5;
  color: #e03131;
}

.delete-btn:hover {
  background-color: #ffe3e3;
}
</style>