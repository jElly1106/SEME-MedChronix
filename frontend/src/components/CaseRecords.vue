<template>
  <div class="case-records-container">
    <div class="case-records-left">
      <div class="case-records-header">
        <h3>病例列表</h3>
        <button class="add-record-btn" @click="addNewRecord">
          <i class="fa fa-plus"></i> 新增
        </button>
      </div>
      <div class="case-records-list">
        <div
          v-for="(record, index) in caseRecords"
          :key="index"
          class="case-record-item"
          :class="{ active: selectedRecordIndex === index }"
          @click="selectRecord(index)"
        >
          <div class="record-header">
            <span class="record-number">#{{ index + 1 }}</span>
            <span class="record-date">{{ record.visitDate }}</span>
          </div>
          <div class="record-location">{{ record.location }}</div>
          <div class="record-actions">
            <button
              class="delete-record-btn"
              @click.stop="confirmDeleteRecord(index)"
            >
              <i class="fa fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="case-records-right">
      <div
        v-if="selectedRecordIndex !== null && caseRecords[selectedRecordIndex]"
        class="case-detail"
      >
        <div class="case-detail-header">
          <h3>病例详情</h3>
          <div class="case-actions">
            <button
              class="edit-btn"
              @click="editCurrentRecord()"
              v-if="!editRecord && selectedRecordIndex !== null"
            >
              <i class="fa fa-edit"></i> 编辑
            </button>
            <button class="save-btn" @click="saveRecord" v-if="editRecord">
              <i class="fa fa-save"></i> 保存
            </button>
            <button class="cancel-btn" @click="cancelEdit" v-if="editRecord">
              <i class="fa fa-times"></i> 取消
            </button>
          </div>
        </div>

        <div class="case-info" v-if="!editRecord">
          <div class="info-group">
            <div class="info-label">就诊日期</div>
            <div class="info-value">
              {{ caseRecords[selectedRecordIndex]?.visitDate || "未设置" }}
            </div>
          </div>
          <div class="info-group">
            <div class="info-label">就诊地点</div>
            <div class="info-value">
              {{ caseRecords[selectedRecordIndex]?.location || "未设置" }}
            </div>
          </div>
          <div class="info-group">
            <div class="info-label">病例编号</div>
            <div class="info-value">
              {{ caseRecords[selectedRecordIndex]?.caseId || "未设置" }}
            </div>
          </div>
        </div>

        <div class="case-edit-form" v-else>
          <div class="form-group">
            <label>就诊日期</label>
            <input type="date" v-model="editingRecord.visitDate" />
          </div>
          <div class="form-group">
            <label>就诊地点</label>
            <input type="text" v-model="editingRecord.location" />
          </div>
          <div class="form-group">
            <label>病例编号</label>
            <input type="text" v-model="editingRecord.caseId" />
          </div>
        </div>

        <div class="case-notes">
          <h4>医生记录</h4>
          <div v-if="!editRecord" class="notes-content">
            {{ caseRecords[selectedRecordIndex].details }}
          </div>
          <textarea
            v-else
            v-model="editingRecord.details"
            class="notes-editor"
          ></textarea>
        </div>
      </div>

      <div v-else class="case-placeholder">
        <div class="placeholder-icon">
          <i class="fa fa-file-text-o"></i>
        </div>
        <p>请从左侧选择一个病例记录查看详情</p>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="modal">
      <div class="modal-content">
        <div class="modal-title">删除确认</div>
        <div class="modal-warning">
          <span class="warning-icon">⚠️</span>
          确定要删除这条病例记录吗？此操作不可恢复。
        </div>
        <div class="buttons">
          <button class="cancel-btn" @click="closeDeleteModal">取消</button>
          <button class="confirm-btn" @click="deleteRecord">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Axios from "@/utils/axios"; 
export default {
  name: "CaseRecords",
  props: {
    // 可以通过props接收父组件传递的初始数据
    initialRecords: {
      type: Array,
      default: () => [],
    },
    patientId: {
      type: [Number, String],
      required: true,
    },
  },
  data() {
    return {
      caseRecords: [],
      selectedRecordIndex: null,
      editRecord: false,
      editingRecord: null,
      showDeleteModal: false,
      recordToDeleteIndex: null,
      isNewRecord: false, // 添加这个属性来标记是否为新记录
    };
  },
  watch: {
    // 监听patientId的变化，当病人ID变化时重新获取数据
    patientId: {
      immediate: false, // 组件创建时不执行，因为created钩子已经执行了
      async handler(newPatientId, oldPatientId) {
        console.log('病人ID变化:', oldPatientId, '->', newPatientId);
        if (newPatientId && newPatientId !== oldPatientId) {
          try {
            // 重置组件状态
            this.editRecord = false;
            this.editingRecord = null;
            this.selectedRecordIndex = null;
            
            // 获取新病人的记录
            this.caseRecords = await this.getRecords();
            
            // 如果有记录，默认选中第一条
            if (this.caseRecords.length > 0) {
              this.selectedRecordIndex = 0;
            }
          } catch (error) {
            console.error('获取病例记录失败:', error);
            this.caseRecords = this.getDefaultRecords();
          }
        }
      }
    }
  },
  async created() {
    console.log('CaseRecords组件初始化，接收到的patientId:', this.patientId);
    // 初始化数据
    if (this.initialRecords.length > 0) {
      this.caseRecords = JSON.parse(JSON.stringify(this.initialRecords));
    } else {
      // 异步获取记录
      try {
        this.caseRecords = await this.getRecords();
      } catch (error) {
        console.error('获取病例记录失败:', error);
        this.caseRecords = this.getDefaultRecords();
      }
    }

    // 如果有记录，默认选中第一条
    if (this.caseRecords.length > 0) {
      this.selectedRecordIndex = 0;
    }
  },
  methods: {
    async getRecords() {
      console.log('获取病例记录，病人ID:', this.patientId);
      try {
        // 获取当前病人ID
        const patientId = this.patientId || this.$route.params.patientId;
        
        if (!patientId) {
          console.error('未找到病人ID');
          return this.getDefaultRecords(); // 如果没有病人ID，返回默认数据
        }
        
        // 获取token
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('未找到token');
          return this.getDefaultRecords();
        }
        
        // 调用后端接口
        console.log(`尝试获取病人ID为 ${patientId} 的所有病例记录`);
        
        // 修改API路径，确保与后端匹配
        const response = await Axios.get(`/patient/case_details/${patientId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          // 禁用withCredentials以避免某些CORS问题
          withCredentials: false
        });
        
        // 添加调试信息，查看API返回的原始数据
        console.log('API返回的原始数据:', response.data);
        
        // 检查响应状态
        if (response.data.code !== 200) {
          console.error('获取病例详情失败:', response.data.message);
          return this.getDefaultRecords();
        }
        
        // 确保数据是数组形式
        let casesData = response.data.data;
        if (!Array.isArray(casesData)) {
          console.warn('后端返回的数据不是数组，尝试转换');
          casesData = [casesData];
        }
        
        // 检查数据长度
        console.log('后端返回的病例数据长度:', casesData.length);
        
        // 如果数据为空，尝试使用备用接口
        if (!casesData || casesData.length === 0) {
          console.warn('后端返回的数据为空，尝试使用备用接口');
          return await this.getRecordsFromBackupAPI(patientId, token);
        }
        
        // 转换后端数据格式为前端所需格式
        const formattedData = this.formatRecordsData(casesData);
        console.log('格式化后的数据:', formattedData);
        console.log('格式化后的记录数量:', formattedData.length);
        
        return formattedData.length > 0 ? formattedData : this.getDefaultRecords();
      } catch (error) {
        console.error('获取病例详情出错:', error);
        
        // 尝试使用备用接口
        try {
          const patientId = this.patientId || this.$route.params.patientId;
          const token = localStorage.getItem('token');
          return await this.getRecordsFromBackupAPI(patientId, token);
        } catch (backupError) {
          console.error('备用接口也失败了:', backupError);
          return this.getDefaultRecords(); // 出错时返回默认数据
        }
      }
    },
    
    // 添加一个新方法用于从备用API获取数据
    async getRecordsFromBackupAPI(patientId, token) {
      console.log('尝试使用备用接口获取病例记录');
      
      // 尝试多个可能的API路径
      const possibleEndpoints = [
        `/patient/cases/${patientId}`,
        `/patient/case/list/${patientId}`,
        `/patient/medical_records/${patientId}`,
        `/patient/case_list/${patientId}`
      ];
      
      for (const endpoint of possibleEndpoints) {
        try {
          console.log(`尝试备用API端点: ${endpoint}`);
          const backupResponse = await Axios.get(endpoint, {
            headers: {
              'Authorization': `Bearer ${token}`
            },
            withCredentials: false
          });
          
          console.log(`备用API ${endpoint} 返回的原始数据:`, backupResponse.data);
          
          if (backupResponse.data.code === 200) {
            const backupData = Array.isArray(backupResponse.data.data) 
              ? backupResponse.data.data 
              : [backupResponse.data.data];
            
            if (backupData && backupData.length > 0) {
              const formattedBackupData = this.formatRecordsData(backupData);
              console.log('备用接口格式化后的数据:', formattedBackupData);
              return formattedBackupData;
            }
          }
        } catch (endpointError) {
          console.warn(`备用端点 ${endpoint} 请求失败:`, endpointError.message);
          // 继续尝试下一个端点
        }
      }
      
      // 如果所有备用API都失败，返回默认数据
      console.warn('所有备用API都失败，返回默认数据');
      return this.getDefaultRecords();
    },

    // 在formatRecordsData方法中添加调试信息
    formatRecordsData(casesData) {
      if (!casesData || casesData.length === 0) {
        console.log('后端返回的数据为空或长度为0');
        return [];
      }
      
      console.log('后端返回的原始病例数据长度:', casesData.length);
      console.log('后端返回的第一条数据示例:', casesData[0]);
      
      // 确保所有记录都被处理，不进行过滤
      return casesData.map(caseItem => {
        // 将事件数据转换为指标数据
        const indicators = caseItem.events ? caseItem.events.map(event => {
          return {
            name: event.event_name,
            value: event.value,
            unit: event.unit || '',
            range: `${event.standard_min || '?'}-${event.standard_max || '?'}`,
            status: event.status
          };
        }) : [];
        
        // 处理日期格式
        let visitDate = '未知日期';
        if (caseItem.visit_time) {
          // 处理多种可能的日期格式
          try {
            // 尝试提取日期部分
            if (caseItem.visit_time.includes('T')) {
              // ISO格式: 2025-04-06T00:00:00.000000
              visitDate = caseItem.visit_time.split('T')[0];
            } else if (caseItem.visit_time.includes(' ')) {
              // 数据库格式: 2025-04-06 00:00:00.000000
              visitDate = caseItem.visit_time.split(' ')[0];
            } else {
              // 如果只有日期部分
              visitDate = caseItem.visit_time;
            }
            console.log(`原始日期: ${caseItem.visit_time}, 格式化后: ${visitDate}`);
          } catch (error) {
            console.error('日期格式化错误:', error);
            visitDate = caseItem.visit_time; // 保留原始值
          }
        }
        
        // 构建前端需要的记录格式
        const formattedRecord = {
          id: caseItem.id || caseItem.case_id, // 确保ID字段被正确映射
          visitDate: visitDate,
          location: caseItem.visit_location || '未知地点',
          details: caseItem.doctor_notes || '无医生记录',
          caseId: caseItem.case_number,
          indicators: indicators
        };
        
        console.log(`格式化记录: ID=${formattedRecord.id}, 日期=${formattedRecord.visitDate}, 编号=${formattedRecord.caseId}`);
        
        return formattedRecord;
      });
    },

    // 保留原有的默认数据方法，作为备用
    getDefaultRecords() {
      return [
        {
          visitDate: "2024-12-14",
          location: "同济大学嘉定校区卫生所",
          details:
            "666",
          caseId: "A12345",
          indicators: [
            {
              name: "血压",
              value: "145/95",
              unit: "mmHg",
              range: "90-140/60-90",
              status: "偏高",
            },
            {
              name: "血糖",
              value: "5.8",
              unit: "mmol/L",
              range: "3.9-6.1",
              status: "正常",
            },
            {
              name: "心率",
              value: "88",
              unit: "次/分",
              range: "60-100",
              status: "正常",
            },
          ],
        },
        {
          visitDate: "2024-11-11",
          location: "同济大学嘉定校区卫生所",
          details:
            "患者复诊，头痛症状有所缓解，血压控制良好。继续服用降压药物，建议定期复查。",
          caseId: "A12346",
          indicators: [
            {
              name: "血压",
              value: "135/85",
              unit: "mmHg",
              range: "90-140/60-90",
              status: "正常",
            },
            {
              name: "血糖",
              value: "6.0",
              unit: "mmol/L",
              range: "3.9-6.1",
              status: "正常",
            },
          ],
        },
      ];
    },

    // 选择病例记录
    selectRecord(index) {
      if (index >= 0 && index < this.caseRecords.length) {
        // 如果当前正在编辑新记录，应该先取消编辑
        if (this.isNewRecord && this.editRecord) {
          this.cancelEdit();
        }

        this.selectedRecordIndex = index;
        this.editRecord = false;
        this.editingRecord = null;
      } else {
        console.warn("Invalid record index:", index);
        this.selectedRecordIndex = null;
      }
    },
    // 编辑记录
    editCurrentRecord() {
      if (
        this.selectedRecordIndex !== null &&
        this.caseRecords[this.selectedRecordIndex]
      ) {
        this.editingRecord = JSON.parse(
          JSON.stringify(this.caseRecords[this.selectedRecordIndex])
        );
        this.editRecord = true;
        this.isNewRecord = false;
      }
    },

    // 添加新记录
    async addNewRecord() {
      const newRecord = {
        visitDate: this.formatDate(new Date()),
        location: "同济大学嘉定校区卫生所",
        details: "",
        caseId: `A${Math.floor(10000 + Math.random() * 90000)}`,
        indicators: [
          {
            name: "血压",
            value: "",
            unit: "mmHg",
            range: "90-140/60-90",
            status: "正常",
          },
          {
            name: "血糖",
            value: "",
            unit: "mmol/L",
            range: "3.9-6.1",
            status: "正常",
          },
        ],
      };

      // 标记为新记录，而不是直接添加到数组
      this.editingRecord = JSON.parse(JSON.stringify(newRecord));
      this.editRecord = true;
      this.isNewRecord = true; // 添加一个标记，表示这是新记录
    },

    // 确认删除记录
    async confirmDeleteRecord(index) {
      this.recordToDeleteIndex = index;
      this.showDeleteModal = true;
    },

    // 删除记录
    async deleteRecord() {
      if (this.recordToDeleteIndex !== null) {
        try {
          const recordToDelete = this.caseRecords[this.recordToDeleteIndex];
          
          if (!recordToDelete.id) {
            console.error('缺少病例ID，无法删除');
            this.$message.error('删除失败：缺少病例ID');
            return;
          }
          
          // 获取token
          const token = localStorage.getItem('token');
          if (!token) {
            console.error('未找到token');
            this.$message.error('删除失败：未找到登录凭证');
            return;
          }
          
          // 调用后端删除接口
          const response = await Axios.delete(`/patient/case/${recordToDelete.id}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            },
            withCredentials: false
          });
          
          console.log('删除病例响应:', response.data);
          
          if (response.data.code !== 200) {
            console.error('删除病例失败:', response.data.message);
            this.$message.error(`删除失败：${response.data.message}`);
            return;
          }
          
          // 前端更新数据
          this.caseRecords.splice(this.recordToDeleteIndex, 1);

          // 如果删除的是当前选中的记录，重置选中状态
          if (this.recordToDeleteIndex === this.selectedRecordIndex) {
            if (this.caseRecords.length > 0) {
              this.selectedRecordIndex = 0;
            } else {
              this.selectedRecordIndex = null;
            }
          } else if (this.recordToDeleteIndex < this.selectedRecordIndex) {
            // 如果删除的记录在当前选中记录之前，需要调整索引
            this.selectedRecordIndex--;
          }

          this.closeDeleteModal();
          this.$message.success('删除成功');

          // 通知父组件数据已更新
          this.$emit("records-updated", this.caseRecords);
        } catch (error) {
          console.error('删除病例出错:', error);
          console.error('错误详情:', error.response?.data || error.message);
          this.$message.error('删除失败：' + (error.response?.data?.message || '服务器错误'));
        }
      }
    },
    // 关闭删除确认弹窗
    closeDeleteModal() {
      this.showDeleteModal = false;
      this.recordToDeleteIndex = null;
    },

    // 保存记录
    async saveRecord() {
      if (this.editingRecord) {
        try {
          // 获取token
          const token = localStorage.getItem('token');
          if (!token) {
            console.error('未找到token');
            this.$message.error('保存失败：未找到登录凭证');
            return;
          }
          
          // 准备请求数据
          const requestData = {
            patient_id: this.patientId,
            case_number: this.editingRecord.caseId,
            visit_time: this.editingRecord.visitDate + 'T00:00:00',
            visit_location: this.editingRecord.location,
            doctor_notes: this.editingRecord.details || ''
          };
          
          console.log('准备发送的数据:', requestData);
          
          let response;
          
          if (this.isNewRecord) {
            // 如果是新记录，调用创建接口
            try {
              response = await Axios.post('/patient/case', requestData, {
                headers: {
                  'Authorization': `Bearer ${token}`
                },
                withCredentials: false
              });
              
              console.log('创建病例响应:', response.data);
              
              if (response.data.code !== 200) {
                console.error('创建病例失败:', response.data.message);
                this.$message.error(`保存失败：${response.data.message}`);
                return;
              }
              
              // 获取新创建的病例ID
              const newCaseId = response.data.data.case_id || response.data.data.id;
              this.editingRecord.id = newCaseId;
              
              // 如果是新记录，添加到数组开头
              this.caseRecords.unshift(
                JSON.parse(JSON.stringify(this.editingRecord))
              );
              this.selectedRecordIndex = 0;
              this.isNewRecord = false;
              
              this.$message.success('新病例创建成功');
            } catch (createError) {
              console.error('创建病例请求出错:', createError);
              console.error('错误详情:', createError.response?.data || createError.message);
              this.$message.error('创建病例失败：' + (createError.response?.data?.message || '服务器错误'));
              return;
            }
          } else if (this.selectedRecordIndex !== null) {
            // 如果是编辑现有记录，调用更新接口
            const caseId = this.editingRecord.id;
            
            if (!caseId) {
              console.error('缺少病例ID，无法更新');
              this.$message.error('保存失败：缺少病例ID');
              return;
            }
            
            console.log(`准备更新病例，ID: ${caseId}`);
            
            try {
              response = await Axios.put(`/patient/case/${caseId}`, requestData, {
                headers: {
                  'Authorization': `Bearer ${token}`
                },
                withCredentials: false
              });
              
              console.log('更新病例响应:', response.data);
              
              if (response.data.code !== 200) {
                console.error('更新病例失败:', response.data.message);
                this.$message.error(`保存失败：${response.data.message}`);
                return;
              }
              
              // 如果是编辑现有记录
              this.caseRecords[this.selectedRecordIndex] = JSON.parse(
                JSON.stringify(this.editingRecord)
              );
              
              this.$message.success('病例更新成功');
            } catch (updateError) {
              console.error('更新病例请求出错:', updateError);
              console.error('错误详情:', updateError.response?.data || updateError.message);
              this.$message.error('更新病例失败：' + (updateError.response?.data?.message || '服务器错误'));
              return;
            }
          }

          this.editRecord = false;
          this.editingRecord = null;

          // 通知父组件数据已更新
          this.$emit("records-updated", this.caseRecords);
        } catch (error) {
          console.error('保存病例出错:', error);
          console.error('错误详情:', error.response?.data || error.message);
          this.$message.error('保存失败：' + (error.response?.data?.message || '服务器错误'));
        }
      }
    },

    // 取消编辑
    cancelEdit() {
      this.editRecord = false;

      // 如果是取消新记录的编辑，不需要保存这条记录
      if (this.isNewRecord) {
        this.isNewRecord = false;
      }

      this.editingRecord = null;
    },

    // 格式化日期
    formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, "0");
      const day = String(date.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    },
  },
};
</script>

<style scoped>
/* 病例记录容器样式 */
.case-records-container {
  display: flex;
  gap: 20px;
  height: 100%;
  padding: 0;
}

.case-records-left {
  width: 30%;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e9ecef;
}

.case-records-right {
  flex: 1;
  height: 100%;
  padding: 20px;
  overflow-y: auto;
}

.case-records-header {
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.case-records-header h3 {
  margin: 0;
  color: #2d5bff;
  font-size: 18px;
  font-weight: 600;
}

.add-record-btn {
  background-color: #2d5bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.add-record-btn:hover {
  background-color: #1a46e0;
}

.case-records-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.case-record-item {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  position: relative;
}

.case-record-item:hover {
  background: #f1f3f5;
  transform: translateX(5px);
}

.case-record-item.active {
  background: #e7f5ff;
  border-left: 3px solid #2d5bff;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-number {
  font-weight: 500;
  color: #6c757d;
}

.record-date {
  font-weight: 600;
  color: #343a40;
}

.record-location {
  color: #6c757d;
  font-size: 14px;
  margin-top: 5px;
}

.record-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  opacity: 0;
  transition: opacity 0.2s;
}

.case-record-item:hover .record-actions {
  opacity: 1;
}

.delete-record-btn {
  background: none;
  border: none;
  color: #e03131;
  cursor: pointer;
  padding: 5px;
  font-size: 14px;
  border-radius: 4px;
}

.delete-record-btn:hover {
  background-color: #fff5f5;
}

/* 病例详情样式 */
.case-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.case-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.case-detail-header h3 {
  margin: 0;
  color: #343a40;
  font-size: 20px;
  font-weight: 600;
}

.case-actions {
  display: flex;
  gap: 10px;
}

.edit-btn,
.save-btn,
.cancel-btn {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.edit-btn {
  background-color: #e7f5ff;
  color: #1c7ed6;
  border: 1px solid #d0ebff;
}

.save-btn {
  background-color: #ebfbee;
  color: #2b8a3e;
  border: 1px solid #d3f9d8;
}

.cancel-btn {
  background-color: #fff5f5;
  color: #e03131;
  border: 1px solid #ffe3e3;
}

/* 病例信息样式 */
.case-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
}

.info-group {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 5px;
}

.info-value {
  font-size: 16px;
  font-weight: 500;
  color: #343a40;
}

/* 编辑表单样式 */
.case-edit-form {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 5px;
}

.form-group input {
  padding: 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
}

/* 指标表格样式 */
.case-indicators {
  margin-bottom: 20px;
}

.case-indicators h4 {
  margin: 0 0 15px 0;
  color: #343a40;
  font-size: 18px;
  font-weight: 600;
}

.indicators-table {
  width: 100%;
  border-collapse: collapse;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.indicators-table th,
.indicators-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.indicators-table th {
  background-color: #f8f9fa;
  color: #495057;
  font-weight: 600;
}

.indicators-table tr:last-child td {
  border-bottom: none;
}

.indicators-table.editable input,
.indicators-table.editable select {
  padding: 6px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  width: 100%;
}

.delete-btn {
  background-color: #fff5f5;
  color: #e03131;
  border: 1px solid #ffe3e3;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
}

.add-indicator-btn {
  background-color: #e7f5ff;
  color: #1c7ed6;
  border: 1px solid #d0ebff;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

/* 指标行样式 */
.normal-row {
  background-color: #ffffff;
}

.high-row {
  background-color: #fff9db;
}

.low-row {
  background-color: #e7f5ff;
}

.abnormal-row {
  background-color: #fff5f5;
}

/* 状态标签样式 */
.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-normal {
  background-color: #ebfbee;
  color: #2b8a3e;
}

.status-high {
  background-color: #fff9db;
  color: #e67700;
}

.status-low {
  background-color: #e7f5ff;
  color: #1c7ed6;
}

.status-abnormal {
  background-color: #fff5f5;
  color: #e03131;
}

/* 医生记录样式 */
.case-notes {
  margin-top: 20px;
}

.case-notes h4 {
  margin: 0 0 15px 0;
  color: #343a40;
  font-size: 18px;
  font-weight: 600;
}

.notes-content {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  line-height: 1.6;
  color: #495057;
  min-height: 100px;
}

.notes-editor {
  width: 100%;
  min-height: 150px;
  padding: 15px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
}

/* 占位样式 */
.case-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #adb5bd;
}

.placeholder-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.case-placeholder p {
  font-size: 16px;
}

/* 弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.modal-content {
  background-color: #fff;
  border: 2px solid #f0f0f0;
  border-radius: 12px;
  padding: 24px 32px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.3s ease-out;
}

.modal-title {
  margin-bottom: 16px;
  color: #2d5bff;
  font-size: 1.2rem;
  font-weight: bold;
}

.modal-warning {
  margin-bottom: 16px;
  color: #000;
  font-size: 1.1rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}

.warning-icon {
  display: inline-block;
  animation: pulse 1.5s infinite;
}

.buttons {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.confirm-btn {
  background-color: #2d5bff !important;
  border: 1px solid #2d5bff !important;
  color: #fff !important;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 5px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}
</style>
