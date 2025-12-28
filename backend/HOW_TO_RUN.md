# 実行方法ガイド / How to Run Guide

面接システムの品質改善機能を実行する方法を説明します。

---

## 📋 前提条件 / Prerequisites

### 1. LM Studioの起動

```bash
# LM Studioアプリケーションを起動
# モデルをロードしてサーバーを起動 (http://localhost:1234)
```

**確認方法**:
```bash
curl http://localhost:1234/v1/models
```

モデル一覧が表示されればOK ✅

### 2. Python依存パッケージのインストール

```bash
cd /Users/ichiharas17/interview-system/backend
pip install -r requirements.txt  # もし requirements.txt があれば
```

---

## 🧪 テストの実行

### オプション1: 各フェーズのテストを個別実行

```bash
cd /Users/ichiharas17/interview-system/backend

# Phase 1: データ矛盾検出テスト
python3 test_phase1_validation.py

# Phase 2: キー正規化テスト
python3 test_phase2_normalization.py

# Phase 4: 値正規化テスト
python3 test_phase4_value_normalization.py
```

### オプション2: 全フェーズ統合テスト

```bash
# すべてのテストを一度に実行
python3 test_all_phases.py
```

**期待される出力**:
```
🎉🎉🎉 ALL TESTS PASSED! 全テスト合格！🎉🎉🎉
✅ データ品質改善の実装が完了しました！
```

### オプション3: ライブセッションテスト（LM Studioと実際に対話）

```bash
# LM Studioとの実際の対話をテスト
python3 test_live_session.py
```

このテストでは以下を確認：
- ✅ データ抽出 (100%)
- ✅ キー正規化 (「仕事」→「職業」など)
- ✅ 値正規化 (「500万円」→ 5,000,000 JPY)
- ✅ 矛盾検出 (カテゴリーをまたいだ検出)
- ✅ 地理的検証 (都道府県・市区町村)

---

## 💬 実際の面接セッションを実行

### 方法1: インタラクティブセッション（ターミナルで対話）

```bash
cd /Users/ichiharas17/interview-system/backend

# インタラクティブ面接を開始
python3 interactive_session.py
```

**実行例**:
```
🎤 インタラクティブ面接セッション
==================================================
Ctrl+C で終了

LM Studio接続確認中...
✅ LM Studio接続成功

あなたの名前を入力してください: 太郎

性別を選択してください:
1. 男性 (male)
2. 女性 (female)
3. その他 (other)
番号を入力 [1-3]: 1

面接官を選択してください:
1. 健太 (kenta) - 落ち着いて知的な男性
2. 美咲 (misaki) - 明るく聞き上手な女性
3. あおい (aoi) - 親しみやすく中性的
番号を入力 [1-3]: 1

🤖 面接官: こんにちは太郎さん！今日もお話しましょう！
🤖 面接官: お名前を教えてもらえますか？

👤 あなた: 太郎です

[データ抽出中...]
🤖 面接官: よろしくお願いします！お仕事は何をされていますか？

👤 あなた: ITエンジニアです。年収は500万くらいです

[データ抽出中...]
[✅ 2件のデータを抽出]
🤖 面接官: ITエンジニアですか！素晴らしいですね...

...
```

**終了方法**:
- `quit` / `exit` / `終了` と入力
- または `Ctrl+C`

**データの確認**:
セッション終了時に保存場所が表示されます：
```
data/sessions/{session_id}.json
```

### 方法2: Flaskバックエンド + フロントエンド

#### 1. バックエンド起動

```bash
cd /Users/ichiharas17/interview-system/backend
python app.py
```

**確認**:
```bash
curl http://localhost:5000/api/health
```

#### 2. フロントエンド起動（別ターミナル）

```bash
cd /Users/ichiharas17/interview-system/frontend
npm run dev
```

#### 3. ブラウザでアクセス

http://localhost:3000 にアクセスして面接を開始

---

## 📊 結果の確認

### 1. セッションファイルを直接確認

```bash
cd /Users/ichiharas17/interview-system/data/sessions

# 最新のセッションを表示
ls -lt | head -5

# セッションの内容を確認
cat {session_id}.json | python3 -m json.tool
```

### 2. 正規化されたデータの例

```json
{
  "category": "基本プロフィール",
  "key": "年齢",
  "value": {
    "age_range": [30, 34],
    "original": "30代前半"
  },
  "original_value": "30代前半",
  "data_version": "2.0",
  "timestamp": "2025-12-28T..."
}
```

```json
{
  "category": "経済・消費",
  "key": "年収",
  "value": {
    "amount": 5000000,
    "currency": "JPY",
    "original": "500万円"
  },
  "original_value": "500万円",
  "data_version": "2.0"
}
```

---

## 🔍 デバッグ・ログの確認

### ログの種類

実行時に以下のログが出力されます：

```
[Extraction] LM Studio response: ...
[Extraction] Found 3 data points
[Normalization] 基本プロフィール/年収: '500万円' → {...}
[Validation] Data rejected: [矛盾理由]
```

### 詳細ログを見る

`interviewer.py` と `profile_manager.py` にデバッグログが組み込まれているため、
実行時にコンソールで確認できます。

---

## ⚙️ カスタマイズ

### 1. 標準キーマッピングの追加

`config.py` の `STANDARD_KEYS` を編集：

```python
STANDARD_KEYS = {
    "基本プロフィール": {
        "新しいキー": ["キー1", "キー2", "キー3"],
        ...
    }
}
```

### 2. 矛盾検出ルールの追加

`data_validator.py` の `CONTRADICTION_RULES` を編集：

```python
CONTRADICTION_RULES = {
    "基本プロフィール": {
        "新しいフィールド": {
            "group1": ["指標1", "指標2"],
            "group2": ["指標3", "指標4"],
            "check_type": "mutual_exclusive"
        }
    }
}
```

### 3. 地理情報の追加

`data_validator.py` の `GEOGRAPHY_MAP` を編集：

```python
GEOGRAPHY_MAP = {
    "新しい県": ["市1", "市2", "市3"],
    ...
}
```

---

## 🐛 トラブルシューティング

### LM Studioに接続できない

**エラー**: `❌ LM Studio connection error`

**解決方法**:
1. LM Studioアプリが起動しているか確認
2. モデルがロードされているか確認
3. サーバーが http://localhost:1234 で起動しているか確認
   ```bash
   curl http://localhost:1234/v1/models
   ```

### データが抽出されない

**症状**: `[Extraction] Found 0 data points`

**確認ポイント**:
1. ユーザーの発言に具体的な情報が含まれているか
2. LM Studioのモデルが適切に応答しているか
3. `interviewer.py` のログで抽出プロンプトと応答を確認

### 矛盾検出が動作しない

**確認ポイント**:
1. `CONTRADICTION_RULES` に該当するルールがあるか確認
2. ログで `[Validation] Data rejected` が出力されているか確認
3. 異なるカテゴリーの矛盾は `_check_cross_category_contradiction` で処理

---

## 📚 関連ドキュメント

- **実装詳細**: `IMPLEMENTATION_SUMMARY.md`
- **テスト結果**: 各テストファイルを実行して確認
- **GitHubリポジトリ**: https://github.com/mextexco/interview-system

---

## 🎯 クイックスタート

最も簡単な開始方法：

```bash
# 1. LM Studioを起動してモデルをロード

# 2. バックエンドディレクトリに移動
cd /Users/ichiharas17/interview-system/backend

# 3. テストを実行して動作確認
python3 test_all_phases.py

# 4. インタラクティブ面接を開始
python3 interactive_session.py
```

これで品質改善機能が動作する面接が開始されます！ 🚀
