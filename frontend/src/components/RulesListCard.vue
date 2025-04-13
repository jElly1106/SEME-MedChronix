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
                  placement="top">
                  <template #reference>
                    <el-icon class="delete-icon" style="cursor: pointer;">
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
        <el-select v-model="type1SelectedRule" placeholder="选择规则" style="width: 120px;">
          <el-option
            v-for="item in availableRules"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <span class="symbol">&gt;</span>
        <el-input v-model="type1Value" type="number" placeholder="数值" style="width: 120px;" />
      </div>

      <!-- 类型2： 下拉框 -> '-' -> 下拉框 -> '>' -> 数值输入框 -->
      <div class="rule-form" v-else-if="ruleType === 'type2'">
        <el-select v-model="type2LeftSelect" placeholder="选择规则" style="width: 120px;">
          <el-option
            v-for="item in availableRules"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <span class="symbol">-</span>
        <el-select v-model="type2RightSelect" placeholder="选择规则" style="width: 120px;">
          <el-option
            v-for="item in availableRules"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <span class="symbol">&gt;</span>
        <el-input v-model="type2Value" type="number" placeholder="数值" style="width: 120px;" />
      </div>

      <!-- 类型3： if -> 下拉框 -> '-' -> 下拉框 -> '>' -> 数值输入框 -->
      <div class="rule-form" v-else-if="ruleType === 'type3'">
        <span class="symbol">if</span>
        <el-select v-model="type3IfSelect" placeholder="选择规则" style="width: 120px;">
          <el-option
            v-for="item in availableRules"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <el-select v-model="type3LeftSelect" placeholder="选择规则" style="width: 120px;">
          <el-option
            v-for="item in availableRules"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <span class="symbol">-</span>
        <el-select v-model="type3RightSelect" placeholder="选择规则" style="width: 120px;">
          <el-option
            v-for="item in availableRules"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <span class="symbol">&gt;</span>
        <el-input v-model="type3Value" type="number" placeholder="数值" style="width: 120px;" />
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
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElIcon } from 'element-plus'

export default {
  name: 'RulesListCard',
  components: {
    Plus,
    Delete,
    ElIcon
  },
  data() {
    return {
      // 控制弹窗显示与隐藏
      showAddRuleModal: false,
      // 当前选中的规则类型
      ruleType: 'type1',
      // 初始已有的动态规则列表
      dynamicRules: [
        { id: 1, text: "非离子钙高 - 目标事件 > -0.41" },
        { id: 2, text: "目标事件 - CK高 > 0.04" },
        { id: 3, text: "目标事件 - 非离子钙高 > 1.00" },
        { id: 4, text: "目标事件 - 血尿素氮高 > 0.33" },
        { id: 5, text: "血细胞比容低 - 非离子钙高 > 0.13" },
        { id: 6, text: "非离子钙高 - AST低 > -0.14" },
        { id: 7, text: "血糖高 - ALT低 > -0.49" },
        { id: 8, text: "非离子钙高 - 脑利钠肽高 > -0.50" },
        { id: 9, text: "非离子钙高 - 血小板计数高 > -0.58" },
        { id: 10, text: "CK低 - 非离子钙高 > 0.58" }
      ],
      // 可选的规则（示例）
      availableRules: [
        '动脉血压收缩压高', 
        '动脉血压舒张压低', 
        '呼吸频率高',
        '血氧饱和度低',
        '心率高',
        '呼吸频率低',
        '动脉血压平均值低',
        '血红蛋白低',
        '血糖高',
        '凝血酶原时间高',
        '国际标准化比率高',
        '白细胞计数高',
        '动脉氧分压高',
        '血细胞比容',
        '动脉二氧化碳分压高',
        '动脉二氧化碳分压低',
        '部分凝血活酶时间高',
        '氯离子高',
        '肌酐高',
        '钠高',
        '动脉血压收缩压低',
        '动脉血压舒张压高',
        '动脉血压平均值高',
        '碳酸氢盐低',
        '白细胞计数低',
        '动脉氧分压低',
        '血尿素氮高',
        '碳酸氢盐高',
        '阴离子间隙低',
        '血小板计数低',
        '动脉碱剩余高',
        '氯离子低',
        '华氏体温高',
        '钾低',
        '血小板计数',
        '心率低',
        '阴离子间隙高',
        '钾高',
        '钠低',
        '肌酐低',
        '血尿素氮低',
        '部分凝血活酶时间低',
        '华氏体温低',
        '凝血酶原时间低',
        '血糖低',
        '血红蛋白高',
        '血细胞比容高',
        '国际标准化比率低',
        '中度到重度'
      ],
      // 类型1数据
      type1SelectedRule: '',
      type1Value: null,
      // 类型2数据
      type2LeftSelect: '',
      type2RightSelect: '',
      type2Value: null,
      // 类型3数据
      type3IfSelect: '',
      type3LeftSelect: '',
      type3RightSelect: '',
      type3Value: null
    };
  },
  methods: {
    // 点击“确定”按钮时的逻辑，根据选择生成一条规则文本并添加到 dynamicRules 中
    onConfirmAddRule() {
      let ruleText = '';
      switch (this.ruleType) {
        case 'type1':
          ruleText = `${this.type1SelectedRule} > ${this.type1Value}`;
          break;
        case 'type2':
          ruleText = `${this.type2LeftSelect} - ${this.type2RightSelect} > ${this.type2Value}`;
          break;
        case 'type3':
          ruleText = `if ${this.type3IfSelect} ${this.type3LeftSelect} - ${this.type3RightSelect} > ${this.type3Value}`;
          break;
      }
      // 添加到动态规则列表中，每个规则分配一个唯一 id
      this.dynamicRules.push({
        id: Date.now(),
        text: ruleText
      });
      // 重置表单
      this.resetForm();
      // 关闭弹窗
      this.showAddRuleModal = false;
    },
    resetForm() {
      this.ruleType = 'type1';
      this.type1SelectedRule = '';
      this.type1Value = null;
      this.type2LeftSelect = '';
      this.type2RightSelect = '';
      this.type2Value = null;
      this.type3IfSelect = '';
      this.type3LeftSelect = '';
      this.type3RightSelect = '';
      this.type3Value = null;
    },
    // 删除规则的方法
    handleDelete(ruleId) {
      this.dynamicRules = this.dynamicRules.filter(rule => rule.id !== ruleId);
    }
  }
};
</script>

<style scoped>
.rules-list-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: 220px;
  padding: 16px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #343C6A;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 添加规则按钮样式 */
.add-rule-btn {
  background-color: #2D5BFF;
  border: none;
  color: #fff;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 20px;
  line-height: 1;
}

/* 表格区域 */
.card-content {
  min-height: 100px;
  overflow-y: auto;
  max-height: 180px;
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
  background-color: #2D5BFF;
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
  border-color: #2D5BFF !important;
  color: #2D5BFF !important;
}

.confirm-btn {
  background-color: #2D5BFF !important;
  border-color: #2D5BFF !important;
  color: #fff !important;
}
</style>
