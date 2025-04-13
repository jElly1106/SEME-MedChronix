// .eslintrc.js
module.exports = {
    parserOptions: {
      parser: '@babel/eslint-parser', // 使用 Babel 解析器
      requireConfigFile: false, // 不强制要求 Babel 配置文件
    },
    extends: [
      'plugin:vue/vue3-essential', // 使用 Vue 3 的基本规则集
      'eslint:recommended'
    ],
    rules: {
      // 在这里可以自定义 ESLint 规则
      'no-undef': 'off' // 关闭 `no-undef` 规则
    }
  };
  