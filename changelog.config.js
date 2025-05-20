module.exports = {
  // 絵文字の表示
  disableEmoji: false,
  // コミットメッセージの形式
  format: "{emoji} {scope}:{subject} ",
  // コミットメッセージの最大文字数
  maxMessageLength: 64,
  // コミットメッセージの最小文字数
  minMessageLength: 3,
  // コミット時の質問の一覧
  questions: [
    "type",
    "scope",
    "subject",
    // "body",
    // "breaking",
    // "issues",
    // "lerna",
  ],
  // コミット種別の一覧
  list: [
    "feat",
    "docs",
    "fix",
    "style",
    "ci",
    "release",
    "refactor",
    "test",
    "chore",
    "perf",
  ],
  // 変更範囲の種別
  scopes: ["開発環境", "フロントエンド", "バックエンド", "インフラ"],
  // コミット種別の詳細
  types: {
    feat: {
      description: "新機能",
      emoji: "✨",
      value: "feat",
    },
    docs: {
      description: "ドキュメント変更",
      emoji: "📝",
      value: "docs",
    },
    fix: {
      description: "バグ修正",
      emoji: "🐛",
      value: "fix",
    },
    style: {
      description: "UI変更",
      emoji: "💄",
      value: "style",
    },
    ci: {
      description: "CI/CD",
      emoji: "👷",
      value: "ci",
    },
    release: {
      description: "リリース",
      emoji: "🚀",
      value: "release",
    },
    refactor: {
      description: "リファクタリング",
      emoji: "♻️",
      value: "refactor",
    },
    test: {
      description: "テスト追加",
      emoji: "✅",
      value: "test",
    },
    chore: {
      description: "開発ツール変更",
      emoji: "📦",
      value: "chore",
    },
    perf: {
      description: "性能向上",
      emoji: "⚡️",
      value: "perf",
    },

    messages: {
      // 質問のメッセージ
      type: "コミット種別を選択。:",
      customScope: "変更の影響範囲を選択。:",
      subject: "変更について簡潔な命令形で説明。:\n",
      body: "変更について詳細に説明。:\n ",
      breaking: "後方互換性の破壊箇所を列挙。:\n",
      footer: "この変更で解決するイシューを記載 (例：#123)。:",
      confirmCommit: "この変更が影響するパッケージを列挙。:\n",
    },
  },
};
