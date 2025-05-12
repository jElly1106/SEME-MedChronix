<template>
  <div
    class="patient-card"
    :class="{ selected: isSelected }"
    @click="selectPatient"
  >
    <div class="patient-avatar">
      <span>{{ patient.name.charAt(0).toUpperCase() }}</span>
    </div>
    <div class="patient-info">
      <div class="patient-name">{{ patient.name }}</div>
      <div class="patient-meta">
        <span class="patient-gender">{{ patient.gender }}</span>
        <span class="patient-age">{{ patient.age }}岁</span>
        <span
          class="patient-type"
          :class="getStrokeTypeClass(patient.strokeType)"
        >
          {{ patient.strokeType }}
        </span>
      </div>
    </div>
    <div class="patient-actions">
      <button class="edit-btn" @click.stop="$emit('edit', patient)">
        <i class="fa fa-edit"></i>
      </button>
      <button class="delete-btn" @click.stop="$emit('delete', patient)">
        <i class="fa fa-trash"></i>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    patient: {
      type: Object,
      required: true,
    },
    isSelected: {
      type: Boolean,
      default: false
    },
    onSelect: {
      type: Function,
      required: true,
    },
  },
  methods: {
    selectPatient() {
      // 不再修改内部状态，只触发选择事件
      this.onSelect(this.patient);
    },
    getStrokeTypeClass(strokeType) {
      if (strokeType === "缺血性") return "ischemic";
      if (strokeType === "出血性") return "hemorrhagic";
      if (strokeType === "短暂性脑缺血发作") return "tia";
      return "other";
    },
  },
};
</script>

<style scoped>
.patient-card {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  border-left: 3px solid transparent;
  margin-bottom: 12px;
}

.patient-card:hover {
  transform: translateX(5px);
  background-color: #f1f3f5;
}

.patient-card.selected {
  background-color: #e7f5ff;
  border-left: 3px solid #2d5bff;
  box-shadow: 0 4px 12px rgba(45, 91, 255, 0.15);
}

.patient-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2d5bff, #7597ff);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.patient-avatar span {
  color: white;
  font-size: 18px;
  font-weight: bold;
}

.patient-info {
  flex: 1;
  overflow: hidden;
}

.patient-name {
  font-weight: 600;
  font-size: 16px;
  color: #343a40;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.patient-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.patient-gender,
.patient-age,
.patient-type {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.patient-gender {
  background-color: #e7f5ff;
  color: #1c7ed6;
}

.patient-age {
  background-color: #fff3bf;
  color: #e67700;
}

.patient-type {
  background-color: #ffe3e3;
  color: #e03131;
}

.patient-type.ischemic {
  background-color: #e7f5ff;
  color: #1c7ed6;
}

.patient-type.hemorrhagic {
  background-color: #ffe3e3;
  color: #e03131;
}

.patient-type.tia {
  background-color: #ebfbee;
  color: #2b8a3e;
}

.patient-type.other {
  background-color: #f1f3f5;
  color: #495057;
}

.patient-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.patient-card:hover .patient-actions {
  opacity: 1;
}

.patient-card.selected .patient-actions {
  opacity: 1;
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
