module.exports = {
    root: true,
    env: {
        browser: true,
        es2022: true,
        node: true
    },
    extends: [
        'plugin:vue/vue3-recommended',
        'eslint:recommended',
        '@vue/typescript/recommended',
        'plugin:prettier/recommended'
    ],
    parserOptions: {
        ecmaVersion: 2022,
        parser: '@typescript-eslint/parser',
        sourceType: 'module'
    },
    plugins: ['@typescript-eslint', 'vue', 'prettier'],
    rules: {
        'no-console': process.env && process.env.NODE_ENV === 'production' ? 'warn' : 'off',
        'no-debugger': process.env && process.env.NODE_ENV === 'production' ? 'warn' : 'off',
        '@typescript-eslint/no-explicit-any': 'warn',
        'vue/multi-word-component-names': 'off',
        'prettier/prettier': 'error'
    }
}
