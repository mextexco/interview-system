"""
Key Normalizer / キー正規化
類似したキー名を標準キー名に正規化するモジュール

Normalizes similar key names to standard key names.
"""

from typing import Dict, List
from config import STANDARD_KEYS, get_standard_key


class KeyNormalizer:
    """
    Key normalization for data extraction
    データ抽出のためのキー正規化
    """

    def __init__(self):
        """Initialize the normalizer"""
        self.standard_keys = STANDARD_KEYS
        self.normalization_log = []  # ログ記録用

    def normalize_key(self, category: str, raw_key: str) -> str:
        """
        Normalize a raw key to its standard form
        生のキー名を標準形に正規化

        Args:
            category: カテゴリー名
            raw_key: 正規化前のキー名

        Returns:
            正規化されたキー名
        """
        normalized = get_standard_key(category, raw_key)

        # ログに記録（デバッグ用）
        if normalized != raw_key:
            self.normalization_log.append({
                "category": category,
                "raw": raw_key,
                "normalized": normalized
            })

        return normalized

    def normalize_batch(self, data_points: List[Dict]) -> List[Dict]:
        """
        Normalize keys in a batch of data points
        データポイントのバッチでキーを正規化

        Args:
            data_points: データポイントのリスト
                         [{category, key, value}, ...]

        Returns:
            正規化されたデータポイントのリスト
        """
        normalized_data = []

        for item in data_points:
            if not isinstance(item, dict):
                continue

            if "category" not in item or "key" not in item:
                # 必須フィールドがない場合はスキップ
                continue

            normalized_item = item.copy()
            normalized_item['key'] = self.normalize_key(
                item['category'],
                item['key']
            )

            normalized_data.append(normalized_item)

        return normalized_data

    def get_normalization_stats(self) -> Dict:
        """
        Get normalization statistics
        正規化統計を取得

        Returns:
            正規化の統計情報
        """
        if not self.normalization_log:
            return {
                "total_normalizations": 0,
                "by_category": {}
            }

        by_category = {}
        for log_entry in self.normalization_log:
            category = log_entry["category"]
            if category not in by_category:
                by_category[category] = {
                    "count": 0,
                    "mappings": {}
                }

            by_category[category]["count"] += 1

            raw = log_entry["raw"]
            normalized = log_entry["normalized"]

            if raw not in by_category[category]["mappings"]:
                by_category[category]["mappings"][raw] = normalized

        return {
            "total_normalizations": len(self.normalization_log),
            "by_category": by_category
        }

    def clear_log(self):
        """Clear the normalization log / ログをクリア"""
        self.normalization_log = []


# 使用例 / Usage example
if __name__ == "__main__":
    # テスト / Test
    normalizer = KeyNormalizer()

    # Test 1: 単一キーの正規化
    print("Test 1: Single key normalization")
    print("=" * 50)

    test_cases = [
        ("ライフストーリー", "行動"),
        ("ライフストーリー", "活動"),
        ("基本プロフィール", "仕事"),
        ("基本プロフィール", "職業"),
        ("現在の生活", "食事時間"),
        ("現在の生活", "食事習慣"),
    ]

    for category, key in test_cases:
        normalized = normalizer.normalize_key(category, key)
        status = "→" if normalized != key else "="
        print(f"{category}/{key} {status} {normalized}")

    # Test 2: バッチ正規化
    print("\n\nTest 2: Batch normalization")
    print("=" * 50)

    data_points = [
        {"category": "ライフストーリー", "key": "行動", "value": "朝のコーヒー"},
        {"category": "ライフストーリー", "key": "活動", "value": "ジョギング"},
        {"category": "基本プロフィール", "key": "仕事", "value": "エンジニア"},
        {"category": "基本プロフィール", "key": "職業", "value": "教師"},
        {"category": "現在の生活", "key": "食事時間", "value": "朝7時"},
        {"category": "現在の生活", "key": "食事習慣", "value": "1日3食"},
    ]

    normalized_data = normalizer.normalize_batch(data_points)

    print("Before normalization:")
    for item in data_points:
        print(f"  {item['category']}/{item['key']} = {item['value']}")

    print("\nAfter normalization:")
    for item in normalized_data:
        print(f"  {item['category']}/{item['key']} = {item['value']}")

    # Test 3: 正規化統計
    print("\n\nTest 3: Normalization statistics")
    print("=" * 50)

    stats = normalizer.get_normalization_stats()
    print(f"Total normalizations: {stats['total_normalizations']}")
    print("\nBy category:")

    for category, data in stats['by_category'].items():
        print(f"\n  {category}: {data['count']} normalizations")
        for raw, normalized in data['mappings'].items():
            print(f"    {raw} → {normalized}")

    # Test 4: キー重複の検出
    print("\n\nTest 4: Duplicate key detection")
    print("=" * 50)

    # 「行動」と「活動」は同じキーに正規化されるべき
    key1 = normalizer.normalize_key("ライフストーリー", "行動")
    key2 = normalizer.normalize_key("ライフストーリー", "活動")

    if key1 == key2:
        print(f"✅ Success: '行動' and '活動' both normalized to '{key1}'")
    else:
        print(f"❌ Failed: '行動' → {key1}, '活動' → {key2}")

    # 「職業」と「仕事」は同じキーに正規化されるべき
    key3 = normalizer.normalize_key("基本プロフィール", "職業")
    key4 = normalizer.normalize_key("基本プロフィール", "仕事")

    if key3 == key4:
        print(f"✅ Success: '職業' and '仕事' both normalized to '{key3}'")
    else:
        print(f"❌ Failed: '職業' → {key3}, '仕事' → {key4}")
