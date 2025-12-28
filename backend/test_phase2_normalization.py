#!/usr/bin/env python3
"""
Phase 2 テスト: キー正規化のテスト
Phase 2 Test: Key normalization test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from key_normalizer import KeyNormalizer
from interviewer import Interviewer

def test_key_normalization():
    """キー正規化のテスト / Test key normalization"""
    print("=" * 70)
    print("Test 1: Key Normalization / キー正規化テスト")
    print("=" * 70)

    normalizer = KeyNormalizer()

    # 重複キーのテストケース
    test_cases = [
        # (category, raw_key, expected_normalized_key)
        ("ライフストーリー", "行動", "活動"),
        ("ライフストーリー", "活動", "活動"),
        ("基本プロフィール", "仕事", "職業"),
        ("基本プロフィール", "職業", "職業"),
        ("基本プロフィール", "業種", "職業"),
        ("現在の生活", "食事時間", "食事"),
        ("現在の生活", "食事習慣", "食事"),
        ("基本プロフィール", "住まい", "住所"),
        ("基本プロフィール", "居住地", "住所"),
    ]

    passed = 0
    failed = 0

    print("\nNormalization tests:")
    for category, raw_key, expected in test_cases:
        normalized = normalizer.normalize_key(category, raw_key)
        if normalized == expected:
            print(f"  ✅ {category}/{raw_key} → {normalized}")
            passed += 1
        else:
            print(f"  ❌ {category}/{raw_key} → {normalized} (expected: {expected})")
            failed += 1

    print(f"\nResults: {passed}/{passed+failed} tests passed")

    if failed == 0:
        print("🎉 All key normalization tests passed!")
        return True
    else:
        print(f"⚠️  {failed} tests failed")
        return False


def test_batch_normalization():
    """バッチ正規化のテスト / Test batch normalization"""
    print("\n\n" + "=" * 70)
    print("Test 2: Batch Normalization / バッチ正規化テスト")
    print("=" * 70)

    normalizer = KeyNormalizer()

    # 重複キーを含むデータポイント
    data_points = [
        {"category": "ライフストーリー", "key": "行動", "value": "朝のコーヒー"},
        {"category": "ライフストーリー", "key": "活動", "value": "ジョギング"},
        {"category": "ライフストーリー", "key": "取り組み", "value": "英語学習"},
        {"category": "基本プロフィール", "key": "仕事", "value": "エンジニア"},
        {"category": "基本プロフィール", "key": "職業", "value": "教師"},
        {"category": "基本プロフィール", "key": "業種", "value": "IT"},
    ]

    print("\nBefore normalization:")
    key_counts_before = {}
    for item in data_points:
        key = f"{item['category']}/{item['key']}"
        key_counts_before[key] = key_counts_before.get(key, 0) + 1
        print(f"  - {key} = {item['value']}")

    normalized_data = normalizer.normalize_batch(data_points)

    print("\nAfter normalization:")
    key_counts_after = {}
    for item in normalized_data:
        key = f"{item['category']}/{item['key']}"
        key_counts_after[key] = key_counts_after.get(key, 0) + 1
        print(f"  - {key} = {item['value']}")

    # 重複が解消されているか確認
    print("\nKey deduplication check:")

    # ライフストーリー/活動: 3つのキー（行動、活動、取り組み）が統一されるべき
    life_activity_count = key_counts_after.get("ライフストーリー/活動", 0)
    if life_activity_count == 3:
        print(f"  ✅ ライフストーリー/活動: {life_activity_count} entries (行動+活動+取り組み)")
    else:
        print(f"  ❌ ライフストーリー/活動: {life_activity_count} entries (expected: 3)")

    # 基本プロフィール/職業: 3つのキー（仕事、職業、業種）が統一されるべき
    profile_job_count = key_counts_after.get("基本プロフィール/職業", 0)
    if profile_job_count == 3:
        print(f"  ✅ 基本プロフィール/職業: {profile_job_count} entries (仕事+職業+業種)")
        return True
    else:
        print(f"  ❌ 基本プロフィール/職業: {profile_job_count} entries (expected: 3)")
        return False


def test_normalization_stats():
    """正規化統計のテスト / Test normalization statistics"""
    print("\n\n" + "=" * 70)
    print("Test 3: Normalization Statistics / 正規化統計テスト")
    print("=" * 70)

    normalizer = KeyNormalizer()

    # 正規化が必要なデータ
    data_points = [
        {"category": "ライフストーリー", "key": "行動", "value": "朝の散歩"},
        {"category": "ライフストーリー", "key": "活動", "value": "読書"},
        {"category": "基本プロフィール", "key": "仕事", "value": "開発者"},
        {"category": "基本プロフィール", "key": "職業", "value": "デザイナー"},
        {"category": "現在の生活", "key": "食事時間", "value": "7時"},
    ]

    normalized_data = normalizer.normalize_batch(data_points)
    stats = normalizer.get_normalization_stats()

    print(f"\nTotal normalizations: {stats['total_normalizations']}")
    print("\nNormalization details:")

    for category, data in stats['by_category'].items():
        print(f"\n  {category}: {data['count']} normalizations")
        for raw, normalized in data['mappings'].items():
            print(f"    {raw} → {normalized}")

    # 統計の確認
    expected_total = 3  # 行動→活動、仕事→職業、食事時間→食事
    if stats['total_normalizations'] == expected_total:
        print(f"\n✅ Normalization count correct: {stats['total_normalizations']}")
        return True
    else:
        print(f"\n❌ Normalization count incorrect: {stats['total_normalizations']} (expected: {expected_total})")
        return False


def test_duplicate_key_consolidation():
    """重複キーの統合テスト / Test duplicate key consolidation"""
    print("\n\n" + "=" * 70)
    print("Test 4: Duplicate Key Consolidation / 重複キー統合テスト")
    print("=" * 70)

    normalizer = KeyNormalizer()

    # 分析レポートで見つかった重複キーをテスト
    print("\nTesting keys from analysis report:")
    print("  - 「行動」 appeared 3 times")
    print("  - 「活動」 appeared 3 times")
    print("  - 「職業」 appeared 2 times")

    # これらが同じキーに正規化されるか確認
    行動_normalized = normalizer.normalize_key("ライフストーリー", "行動")
    活動_normalized = normalizer.normalize_key("ライフストーリー", "活動")

    職業1_normalized = normalizer.normalize_key("基本プロフィール", "職業")
    職業2_normalized = normalizer.normalize_key("現在の生活", "職業")

    print("\nNormalization results:")
    all_passed = True

    if 行動_normalized == 活動_normalized:
        print(f"  ✅ '行動' and '活動' both normalized to '{行動_normalized}'")
    else:
        print(f"  ❌ '行動' → {行動_normalized}, '活動' → {活動_normalized} (should be same)")
        all_passed = False

    if 職業1_normalized == 職業2_normalized:
        print(f"  ✅ '職業' in different categories: '{職業1_normalized}' and '{職業2_normalized}'")
    else:
        print(f"  ❌ '職業' normalization differs: '{職業1_normalized}' vs '{職業2_normalized}'")
        all_passed = False

    return all_passed


if __name__ == "__main__":
    print("\n")
    print("🧪 Phase 2 Key Normalization Tests")
    print("=" * 70)

    results = []
    results.append(("Key Normalization", test_key_normalization()))
    results.append(("Batch Normalization", test_batch_normalization()))
    results.append(("Normalization Statistics", test_normalization_stats()))
    results.append(("Duplicate Key Consolidation", test_duplicate_key_consolidation()))

    print("\n\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nOverall: {total_passed}/{total_tests} test suites passed")

    if total_passed == total_tests:
        print("\n🎉 Phase 2 complete! All key normalization tests passed!")
        exit(0)
    else:
        print(f"\n⚠️  {total_tests - total_passed} test suite(s) failed")
        exit(1)
