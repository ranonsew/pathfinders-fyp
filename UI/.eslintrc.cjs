/* eslint-env node */
module.exports = {
  root: true,
  'extends': [
    'plugin:vue/vue3-essential',
    'eslint:recommended'
  ],
  rules: {
    "vue/multi-word-component-names": "off",
    "vue/no-unused-components": "off",
  },
  parserOptions: {
    ecmaVersion: 'latest'
  }
}
