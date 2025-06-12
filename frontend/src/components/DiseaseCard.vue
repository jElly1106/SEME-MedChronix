<template>
  <div class="disease-card">
    <h4>{{ name }}</h4>
    <p>{{ description }}</p>
  </div>
</template>

<script>
export default {
  name: "DiseaseCard",
  props: {
    name: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
  },
};
</script>

<style scoped>
.disease-card {
  background-color: #C6D2FD;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  font-size: 16px;
  font-family: 'Arial', sans-serif;
}

.disease-card h4 {
  font-size: 18px;
  font-weight: 600;
  color: #2D5BFF;
  margin-bottom: 10px;
}

.disease-card p {
  font-size: 14px;
  color: #333;
}
</style>
