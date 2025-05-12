<template>
  <div class="rules-list-card">
    <div class="card-header">
      规则列表
      <!-- 右侧添加规则按钮，使用 Element Plus 的加号图标 -->
      <button class="add-rule-btn" @click="showAddRuleModal = true">
        <el-icon>
          <Plus />
        </el-icon>
      </button>
    </div>

    <div class="card-content">
      <!-- 规则列表表格 -->
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th class="col-index">序号</th>
              <th class="col-rule">内容</th>
              <th class="col-action"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(rule, index) in dynamicRules" :key="rule.id">
              <td>{{ index + 1 }}</td>
              <td>{{ rule.text }}</td>
              <td>
                <!-- 使用 Element Plus 的 Popconfirm 组件来确认删除操作 -->
                <el-popconfirm
                  title="是否确认删除该规则？"
                  @confirm="handleDelete(rule.id)"
                  placement="top"
                >
                  <template #reference>
                    <el-icon class="delete-icon" style="cursor: pointer">
                      <Delete />
                    </el-icon>
                  </template>
                </el-popconfirm>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 弹窗：添加规则 -->
    <el-dialog v-model="showAddRuleModal" width="600px">
      <!-- 自定义标题插槽，用卡片标题的样式 -->
      <template #title>
        <div class="card-header">添加规则</div>
      </template>

      <!-- 规则类型选择 -->
      <div class="rule-type-selector">
        <span>请选择规则类型：</span>
        <el-select v-model="ruleType" placeholder="请选择规则类型" style="width: 200px;">
          <el-option label="类型1" value="type1"></el-option>
          <el-option label="类型2" value="type2"></el-option>
          <el-option label="类型3" value="type3"></el-option>
        </el-select>
      </div>

      <!-- 根据不同规则类型渲染不同表单结构 -->
      <!-- 类型1： 下拉框 -> '>' -> 数值输入框（无 + -） -->
    <div class="rule-form" v-if="ruleType === 'type1'">
      <!-- 规则名称 & 规则权重 -->
      <el-input
        v-model="type1Name"
        placeholder="名称"
        style="width: 120px; margin-right: 10px;"
      />
      <el-input
        v-model="type1Weight"
        type="number"
        placeholder="权重"
        style="width: 120px; margin-right: 10px;"
      />

      <!-- 原有逻辑：选择规则 -> '>' -> 数值输入框 -->
      <el-select v-model="type1SelectedRule" placeholder="选择事件" style="width: 120px;">
        <el-option
          v-for="item in availableRules"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <span class="symbol">&gt;</span>
      <el-input
        v-model="type1Value"
        type="number"
        placeholder="数值"
        style="width: 120px;"
      />
    </div>

    <!-- 类型2： 下拉框 -> '-' -> 下拉框 -> '>' -> 数值输入框 -->
    <div class="rule-form" v-else-if="ruleType === 'type2'">
      <!-- 规则名称 & 规则权重 -->
      <el-input
        v-model="type2Name"
        placeholder="名称"
        style="width: 120px; margin-right: 10px;"
      />
      <el-input
        v-model="type2Weight"
        type="number"
        placeholder="权重"
        style="width: 120px; margin-right: 10px;"
      />

      <!-- 原有逻辑：选择规则 -> '-' -> 选择规则 -> '>' -> 数值输入框 -->
      <el-select v-model="type2LeftSelect" placeholder="选择事件" style="width: 120px;">
        <el-option
          v-for="item in availableRules"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <span class="symbol">-</span>
      <el-select v-model="type2RightSelect" placeholder="选择事件" style="width: 120px;">
        <el-option
          v-for="item in availableRules"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <span class="symbol">&gt;</span>
      <el-input
        v-model="type2Value"
        type="number"
        placeholder="数值"
        style="width: 120px;"
      />
    </div>

    <!-- 类型3： if -> 下拉框 -> '-' -> 下拉框 -> '>' -> 数值输入框 -->
    <div class="rule-form" v-else-if="ruleType === 'type3'">
      <!-- 规则名称 & 规则权重 -->
      <el-input
        v-model="type3Name"
        placeholder="名称"
        style="width: 120px; margin-right: 10px;"
      />
      <el-input
        v-model="type3Weight"
        type="number"
        placeholder="权重"
        style="width: 120px; margin-right: 10px;"
      />

      <!-- 原有逻辑：if -> 选择规则 -> '-' -> 选择规则 -> '>' -> 数值输入框 -->
      <span class="symbol">if</span>
      <el-select v-model="type3IfSelect" placeholder="选择前置条件" style="width: 120px;">
        <el-option
          v-for="item in preconditions"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <el-select v-model="type3LeftSelect" placeholder="选择事件" style="width: 120px;">
        <el-option
          v-for="item in availableRules"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <span class="symbol">-</span>
      <el-select v-model="type3RightSelect" placeholder="选择事件" style="width: 120px;">
        <el-option
          v-for="item in availableRules"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <span class="symbol">&gt;</span>
      <el-input
        v-model="type3Value"
        type="number"
        placeholder="数值"
        style="width: 120px;"
      />
    </div>


      <template #footer>
        <div class="dialog-footer">
          <el-button class="cancel-btn" @click="showAddRuleModal = false">取消</el-button>
          <el-button class="confirm-btn" @click="onConfirmAddRule">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { Plus, Delete } from "@element-plus/icons-vue";
import { ElIcon, ElMessage, ElNotification } from "element-plus";
import Axios from "@/utils/axios";

export default {
  name: "RulesListCard",
  components: {
    Plus,
    Delete,
    ElIcon,
  },
  data() {
    return {
      // 控制弹窗显示与隐藏
      showAddRuleModal: false,
      // 当前选中的规则类型
      ruleType: "type1",
      // 初始已有的动态规则列表
      dynamicRules: [],
      // 可选的规则（示例）
      availableRules: [],
      preconditions: [],
      // 类型1数据
      type1Name: "",
      type1Weight: 1,
      type1SelectedRule: "",
      type1Value: null,
      
      // 类型2数据
      type2Name: "",
      type2Weight: 1,
      type2LeftSelect: "",
      type2RightSelect: "",
      type2Value: null,
      
      // 类型3数据
      type3Name: "",
      type3Weight: 1,
      type3IfSelect: "",
      type3LeftSelect: "",
      type3RightSelect: "",
      type3Value: null,
      
      // 事件映射
      eventsMap: {},
      preconditionsMap: {},
      // ... 现有代码 ...
    };
  },
  mounted() {
    // 组件挂载后获取规则列表
    this.fetchRules();
    // 获取事件ID和名称的映射
    this.fetchEventsMap();
    this.fetchPreconditions();
  },
  methods: {
    async fetchRules() {
      try {
        this.loading = true;
        // 获取token
        const token = localStorage.getItem('token');
        
        // 调用后端接口获取规则列表
        const response = await Axios.get('/rule/get_rules', {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          withCredentials: false
        });
        
        // 检查响应数据
        if (response.data && Array.isArray(response.data)) {
          // 将后端返回的数据格式转换为组件需要的格式
          this.dynamicRules = response.data.map(item => ({
            id: item.id,
            text: item.content
          }));
          
          console.log('成功获取规则列表:', this.dynamicRules);
        } else {
          console.error('规则数据格式不正确:', response.data);
          this.error = '获取规则数据格式不正确';
        }
      } catch (error) {
        console.error('获取规则列表失败:', error);
        this.error = '获取规则列表失败';
        
        // 如果API请求失败，可以使用默认的硬编码数据（可选）
        this.dynamicRules = [
          { id: 1, text: "非离子钙高 - 目标事件 > -0.41" },
          { id: 2, text: "目标事件 - CK高 > 0.04" },
          // 可以保留几个作为备用
        ];
      } finally {
        this.loading = false;
      }
    },
    async onConfirmAddRule() {
      try {
        let ruleText = "";
        let requestData = {
          disease_id: 1,
          category: 1,  // 默认类别
        };

        // 根据不同规则类型构建请求数据
        switch (this.ruleType) {
          case "type1":{
            // 验证必填字段
            if (!this.type1SelectedRule) {
              ElMessage.error('请选择事件');
              return;
            }
            if (this.type1Value === null || this.type1Value === '') {
              ElMessage.error('请输入数值');
              return;
            }
            
            ruleText = `${this.type1SelectedRule} > ${this.type1Value}`;
            requestData.name = this.type1Name || ruleText;
            requestData.weight = this.type1Weight || 1;
            requestData.event_id1 = this.getEventIdByName(this.type1SelectedRule);
            requestData.time_delta = parseFloat(this.type1Value);
            break;
          }
          case "type2":{
            // 验证必填字段
            if (!this.type2LeftSelect) {
              ElMessage.error('请选择左侧事件');
              return;
            }
            if (!this.type2RightSelect) {
              ElMessage.error('请选择右侧事件');
              return;
            }
            if (this.type2Value === null || this.type2Value === '') {
              ElMessage.error('请输入数值');
              return;
            }
            
            ruleText = `${this.type2LeftSelect} - ${this.type2RightSelect} > ${this.type2Value}`;
            requestData.name = this.type2Name || ruleText;
            requestData.weight = parseFloat(this.type2Weight) || 1;
            
            // 获取事件ID并确保它们是有效的数字
            const event_id1 = this.getEventIdByName(this.type2LeftSelect);
            const event_id2 = this.getEventIdByName(this.type2RightSelect);
            
            // 记录事件ID用于调试
            console.log(`事件1 "${this.type2LeftSelect}" ID: ${event_id1}`);
            console.log(`事件2 "${this.type2RightSelect}" ID: ${event_id2}`);
            
            requestData.event_id1 = event_id1;
            requestData.event_id2 = event_id2;
            requestData.time_delta = parseFloat(this.type2Value);
            requestData.category = 2;  // 确保类型2使用正确的类别
            break;
          }
          case "type3":{
            // 验证必填字段
            if (!this.type3IfSelect || !this.type3LeftSelect || !this.type3RightSelect) {
              ElMessage.error('请选择所有事件');
              return;
            }
            if (this.type3Value === null || this.type3Value === '') {
              ElMessage.error('请输入数值');
              return;
            }
            
            ruleText = `if ${this.type3IfSelect} ${this.type3LeftSelect} - ${this.type3RightSelect} > ${this.type3Value}`;
            requestData.name = this.type3Name || ruleText;
            requestData.weight = parseFloat(this.type3Weight) || 1;
            
            // 获取事件ID和前置条件ID
            const event_id1 = this.getEventIdByName(this.type3LeftSelect);
            const event_id2 = this.getEventIdByName(this.type3RightSelect);
            const precondition_id = this.getPreconditionIdByName(this.type3IfSelect);
            
            // 记录事件ID用于调试
            console.log(`前置条件 "${this.type3IfSelect}" ID: ${precondition_id}`);
            console.log(`事件1 "${this.type3LeftSelect}" ID: ${event_id1}`);
            console.log(`事件2 "${this.type3RightSelect}" ID: ${event_id2}`);
            
            requestData.event_id1 = event_id1;
            requestData.event_id2 = event_id2;
            requestData.precondition = precondition_id;
            requestData.time_delta = parseFloat(this.type3Value);
            
            // 设置类型3特有的参数
            requestData.category = 3;  // 确保类型3使用正确的类别
            break;
          }
        }

        // 验证必填字段
        if (!requestData.name) {
          ElMessage.error('请输入规则名称');
          return;
        }
        
        if (!requestData.weight) {
          ElMessage.error('请输入规则权重');
          return;
        }

        console.log('准备发送的规则数据:', requestData);

        // 获取token
        const token = localStorage.getItem('token');
        
        // 发送POST请求到后端添加规则
        const response = await Axios.post('/rule/add_rule', requestData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          withCredentials: false
        });

        // 检查响应状态
        if (response.status === 201) {
          console.log('规则添加成功:', response.data);
          
          // 显示成功消息 - 修改这里
          ElMessage({
            message: '规则添加成功',
            type: 'success'
          });
          
          // 重置表单
          this.resetForm();
          // 关闭弹窗
          this.showAddRuleModal = false;
          
          // 刷新规则列表
          this.fetchRules();
        } else {
          console.error('添加规则失败:', response.data);
          ElMessage.error('添加规则失败');
        }
      } catch (error) {
        console.error('添加规则请求失败:', error);
        ElMessage.error('添加规则失败: ' + (error.response?.data?.error || '未知错误'));
      }
    },
    
    resetForm() {
      this.ruleType = "type1";
      
      // 重置类型1数据
      this.type1Name = "";
      this.type1Weight = 1;
      this.type1SelectedRule = "";
      this.type1Value = null;
      
      // 重置类型2数据
      this.type2Name = "";
      this.type2Weight = 1;
      this.type2LeftSelect = "";
      this.type2RightSelect = "";
      this.type2Value = null;
      
      // 重置类型3数据
      this.type3Name = "";
      this.type3Weight = 1;
      this.type3IfSelect = "";
      this.type3LeftSelect = "";
      this.type3RightSelect = "";
      this.type3Value = null;
    },
    
    // 获取所有事件的ID和名称映射
    async fetchEventsMap() {
      try {
        // 获取token
        const token = localStorage.getItem('token');
        
        // 调用后端接口获取所有事件
        const response = await Axios.get('/event/get_all_events', {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          withCredentials: false
        });
        
        // 检查响应数据
        if (response.data && Array.isArray(response.data)) {
          // 创建事件名称到ID的映射
          this.eventsMap = {};
          response.data.forEach(event => {
            this.eventsMap[event.name] = event.id;
          });
          
          // 更新可选规则列表
          this.availableRules = response.data.map(event => event.name);
          
          console.log('成功获取事件映射:', this.eventsMap);
          console.log('成功获取可选规则列表:', this.availableRules);
        } else {
          console.error('事件数据格式不正确:', response.data);
        }
      } catch (error) {
        console.error('获取事件映射失败:', error);
      }
    },
    
    // 获取所有前置条件
        // 获取所有前置条件
    async fetchPreconditions() {
      try {
        // 获取token
        const token = localStorage.getItem('token');
        
        // 调用后端接口获取所有前置条件
        const response = await Axios.get('/precondition/get_all_preconditions', {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          withCredentials: false
        });
        
        // 检查响应数据
        console.log('前置条件原始响应数据:', response.data);
        
        if (response.data && Array.isArray(response.data)) {
          this.preconditionsMap = {};
          
          // 更新前置条件列表 - 增加更灵活的数据处理
          this.preconditions = response.data.map(precondition => {
            // 尝试多种可能的属性名
            const name = precondition.description;
            
            if (name) {
              this.preconditionsMap[name] = precondition.id || 0;
              return name;
            }
            return null;
          }).filter(name => name !== null); // 过滤掉空值
          
          console.log('成功获取前置条件列表:', this.preconditions);
          console.log('前置条件映射:', this.preconditionsMap);
          
          // 如果列表为空，使用事件列表作为备用
          if (this.preconditions.length === 0) {
            console.warn('前置条件列表为空，使用事件列表作为备用');
            this.preconditions = [...this.availableRules];
          }
        } else {
          console.error('前置条件数据格式不正确:', response.data);
          // 使用事件列表作为备用
          this.preconditions = [...this.availableRules];
        }
      } catch (error) {
        console.error('获取前置条件列表失败:', error);
        // 如果获取失败，使用事件列表作为备用
        this.preconditions = [...this.availableRules];
      }
    },
    
    // 根据事件名称获取事件ID
    getEventIdByName(eventName) {
      // 如果事件映射中存在该事件名称，则返回对应的ID
      if (this.eventsMap[eventName] !== undefined) {
        return this.eventsMap[eventName];
      }
      
      // 如果映射中不存在，则记录错误并使用备用方法
      console.error(`未找到事件名称 "${eventName}" 对应的ID`);
      
      // 备用方法：使用哈希值作为ID（仅在映射不存在时使用）
      return Math.abs(this.hashCode(eventName)) % 100 + 1;
    },
    // 根据前置条件名称获取前置条件ID
    getPreconditionIdByName(preconditionName) {
      // 如果前置条件映射中存在该名称，则返回对应的ID
      if (this.preconditionsMap[preconditionName] !== undefined) {
        return this.preconditionsMap[preconditionName];
      }
      
      // 如果映射中不存在，则记录错误并使用备用方法
      console.error(`未找到前置条件名称 "${preconditionName}" 对应的ID`);
      
      // 备用方法：使用哈希值作为ID（仅在映射不存在时使用）
      return Math.abs(this.hashCode(preconditionName)) % 100 + 1;
    },
    
    // 哈希函数保持不变
    hashCode(str) {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
      }
      return hash;
    },
    // 删除规则的方法
        // 删除规则的方法
        // 删除规则的方法
    async handleDelete(ruleId) {
      try {
        // 获取 token
        const token = localStorage.getItem('token');
        
        console.log(`尝试删除规则 ID: ${ruleId}`);
        
        // 使用完整的 URL 路径
        const url = `/rule/delete_rule/${ruleId}`;
        console.log('发送删除请求到:', url);
        // 发送 DELETE 请求到后端
        const response = await Axios.delete(url,{
          
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          withCredentials: false
        });
        
        // 检查响应状态
        if (response.status === 200) {
          console.log('规则删除成功:', response.data);
          // 从 dynamicRules 中移除已删除的规则
          this.dynamicRules = this.dynamicRules.filter(rule => rule.id !== ruleId);
          // 使用 Element Plus 的消息提示
          ElNotification({
            title: '成功',
            message: '规则删除成功',
            type: 'success'
          });
        } else {
          console.error('删除规则失败:', response.data);
          ElNotification.error({
            title: '错误',
            message: '删除规则失败'
          });
        }
      } catch (error) {
        console.error('删除规则请求失败:', error);
        // 显示详细错误信息，帮助调试
        console.error('错误详情:', error.response ? error.response.data : '无响应数据');
        console.error('错误状态:', error.response ? error.response.status : '无状态码');
        console.error('请求URL:', `/rule/delete_rule/${ruleId}`);
        
        // 使用 Element Plus 的消息提示
        ElNotification.error({
          title: '错误',
          message: '删除规则失败，请检查网络连接或联系管理员'
        });
      }
    },
  },
};
</script>

<style scoped>
.rules-list-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 404px;
  padding: 16px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #343c6a;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 添加规则按钮样式 */
.add-rule-btn {
  background-color: #2d5bff;
  border: none;
  color: #fff;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

/* 表格区域 */
.card-content {
  min-height: 80px;
  overflow-y: auto;
  max-height: 360px;
}

/* 表格容器，添加圆角+隐藏溢出 */
.table-container {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
}

/* 基础表格样式 */
table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

thead {
  background-color: #2d5bff;
}

thead th {
  color: #fff;
  padding: 8px;
  font-size: 14px;
}

tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

tbody td {
  padding: 8px;
  font-size: 14px;
  color: #333;
}

/* 列宽可根据需要微调 */
.col-index {
  width: 50px;
}
.col-rule {
  width: auto;
}
.col-action {
  width: 20px;
  text-align: center;
}

/* 弹窗内样式 */
.rule-type-selector {
  margin-bottom: 16px;
}

.rule-form {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
}

.symbol {
  margin: 0 4px;
  font-weight: bold;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 按钮样式 */
.cancel-btn {
  background-color: #fff !important;
  border-color: #2d5bff !important;
  color: #2d5bff !important;
}

.confirm-btn {
  background-color: #2d5bff !important;
  border-color: #2d5bff !important;
  color: #fff !important;
}
</style>
