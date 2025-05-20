import eslint from "@eslint/js";
import eslintPluginNext from "@next/eslint-plugin-next";
import eslintConfigPrettier from "eslint-config-prettier";
import eslintPluginImport from "eslint-plugin-import";
import eslintPluginReact from "eslint-plugin-react";
import eslintPluginReactHooks from "eslint-plugin-react-hooks";
import eslintPluginUnusedImport from "eslint-plugin-unused-imports";
import eslintPluginTypescript from "typescript-eslint";

const eslintConfig = [
  {
    // ====================
    // Global settings
    // ====================
    files: ["*.js", "*.jsx", "*.ts", "*.tsx", "*.mjs", "*.cjs"],
    ignores: [
      "**/build/",
      "**/bin/",
      "**/dist/",
      "**/obj/",
      "**/out/",
      "**/.next/",
      "**/node_modules/",
    ],
  },
  {
    // ====================
    // for React.js/Next.js
    // ====================
    ...eslint.configs.recommended, // ESLint recommended
    ...eslintPluginReact.configs.flat.recommended,
    ...eslintPluginReact.configs.flat["jsx-runtime"],
    plugins: {
      "@next/next": eslintPluginNext,
      "react-hooks": eslintPluginReactHooks,
    },
    rules: {
      ...eslintPluginReactHooks.configs.recommended.rules,
      ...eslintPluginNext.configs.recommended.rules,
      ...eslintPluginNext.configs["core-web-vitals"].rules,
      "@next/next/no-img-element": "error",
      "react/prop-types": "off",
    },
  },
  {
    // ====================
    // for TypeScript
    // ====================
    files: ["*.ts", "*.tsx"],
    // ...tseslint.configs.recommended, // Typescript recommended
    ...eslintPluginTypescript.configs.strictTypeChecked, // Type check
    ...eslintPluginTypescript.configs.stylisticTypeChecked, // Style check
    languageOptions: {
      parser: eslintPluginTypescript.parser,
      parserOptions: { project: "./tsconfig.json" },
    },
    rules: {
      "@typescript-eslint/no-unused-vars": [
        // 未使用の変数を警告
        "warn",
        { argsIgnorePattern: "^_" },
      ],
      // "@typescript-eslint/explicit-function-return-type": "off", // 関数の戻り値の型を明示
      "@typescript-eslint/consistent-type-definitions": ["error", "type"], // 型定義の一貫性
      // "@typescript-eslint/no-unsafe-assignment": "off", // 安全でない代入を許可
      // "@typescript-eslint/no-misused-promises": "off", // Promiseの誤用を無効化
      "react/jsx-boolean-value": "error", // JSXでのboolean値を明示
      "react/jsx-curly-brace-presence": "error", // JSXで不要な{}を防止
    },
  },
  {
    // ====================
    // for Import order & Unused import
    // ====================
    plugins: {
      import: eslintPluginImport,
      "unused-imports": eslintPluginUnusedImport,
    },
    rules: {
      "import/order": [
        "error",
        {
          // import種別ごとにグループ化
          groups: [
            "builtin",
            "external",
            "internal",
            ["parent", "sibling", "index"],
            "type",
          ],
          // アルファベット順に並べ替え
          alphabetize: { order: "asc", caseInsensitive: true },
          // グループ間で1行空ける
          "newlines-between": "never",
          pathGroups: [
            { pattern: "react", group: "builtin", position: "before" },
            { pattern: "next/**", group: "builtin", position: "before" },
            {
              pattern: "@/app/**",
              group: "internal",
              position: "before",
            },
            {
              pattern: "@/components/**",
              group: "internal",
              position: "before",
            },
            {
              pattern: "@/styles/**",
              group: "internal",
              position: "before",
            },
          ],
        },
      ],
      "import/newline-after-import": "error", // import後は改行
      "import/no-duplicates": "error", // 重複importを防止
      "unused-imports/no-unused-imports": "error", // 未使用importを防止
    },
  },

  {
    // ====================
    // for Prettier
    // ====================
    ...eslintConfigPrettier,
  },
];

export default eslintConfig;
