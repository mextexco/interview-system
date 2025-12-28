#!/usr/bin/env python3
"""
Phase 1 テスト: データ矛盾検出とバリデーションのテスト
Phase 1 Test: Data contradiction detection and validation test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from profile_manager import ProfileManager
import uuid

def test_contradiction_detection():
    """矛盾検出のテスト / Test contradiction detection"""
    print("=" * 70)
    print("Test 1: Contradiction Detection / 矛盾検出テスト")
    print("=" * 70)

    manager = ProfileManager()

    # テスト用ユーザーとセッションを作成
    user = manager.create_user("テストユーザー", "male", "kenta")
    session = manager.create_session(user["user_id"])
    session_id = session["session_id"]

    # Test Case 1: 「1人暮らし」を追加
    print("\n1. Adding '1人暮らし' to 家族構成...")
    session = manager.add_extracted_data(
        session_id,
        "基本プロフィール",
        "家族構成",
        "1人暮らし"
    )
    print("   ✅ Data added successfully")

    # Test Case 2: 矛盾する「5人家族」を追加しようとする（拒否されるべき）
    print("\n2. Attempting to add contradictory '5人家族'...")
    session_before = manager.get_session(session_id)
    data_count_before = len(session_before["extracted_data"]["基本プロフィール"])

    session = manager.add_extracted_data(
        session_id,
        "基本プロフィール",
        "家族構成",
        "5人家族"
    )

    session_after = manager.get_session(session_id)
    data_count_after = len(session_after["extracted_data"]["基本プロフィール"])

    if data_count_after == data_count_before:
        print("   ✅ Contradictory data was correctly rejected!")
    else:
        print("   ❌ ERROR: Contradictory data was not rejected!")

    # Test Case 3: 非矛盾データ「太郎」を追加（許可されるべき）
    print("\n3. Adding non-contradictory data '太郎' to 名前...")
    session = manager.add_extracted_data(
        session_id,
        "基本プロフィール",
        "名前",
        "太郎"
    )
    print("   ✅ Data added successfully")

    print("\n" + "=" * 70)
    print("Final data in 基本プロフィール:")
    final_data = manager.get_session(session_id)["extracted_data"]["基本プロフィール"]
    for item in final_data:
        print(f"  - {item['key']}: {item['value']}")


def test_geographic_validation():
    """地理的検証のテスト / Test geographic validation"""
    print("\n\n" + "=" * 70)
    print("Test 2: Geographic Validation / 地理的検証テスト")
    print("=" * 70)

    manager = ProfileManager()

    # テスト用ユーザーとセッションを作成
    user = manager.create_user("地理テストユーザー", "female", "misaki")
    session = manager.create_session(user["user_id"])
    session_id = session["session_id"]

    # Test Case 1: 正しい地理データ「東京都渋谷区」
    print("\n1. Adding valid geographic data '東京都渋谷区'...")
    session = manager.add_extracted_data(
        session_id,
        "基本プロフィール",
        "住所",
        "東京都渋谷区"
    )
    print("   ✅ Valid geographic data added successfully")

    # Test Case 2: 間違った地理データ「東京都横浜」（横浜は神奈川県）
    print("\n2. Attempting to add invalid geographic data '東京都横浜'...")
    session_before = manager.get_session(session_id)
    data_count_before = len(session_before["extracted_data"]["基本プロフィール"])

    session = manager.add_extracted_data(
        session_id,
        "基本プロフィール",
        "住所",
        "東京都横浜"
    )

    session_after = manager.get_session(session_id)
    data_count_after = len(session_after["extracted_data"]["基本プロフィール"])

    if data_count_after == data_count_before:
        print("   ✅ Invalid geographic data was correctly rejected!")
    else:
        print("   ❌ ERROR: Invalid geographic data was not rejected!")

    # Test Case 3: 未検証の地理データ「東京都中野区」（警告あり・保存される）
    print("\n3. Adding unverified but valid geographic data '神奈川県横浜市'...")
    session = manager.add_extracted_data(
        session_id,
        "基本プロフィール",
        "出身地",
        "神奈川県横浜市"
    )
    print("   ✅ Valid geographic data added successfully")

    print("\n" + "=" * 70)
    print("Final data in 基本プロフィール:")
    final_data = manager.get_session(session_id)["extracted_data"]["基本プロフィール"]
    for item in final_data:
        warnings = item.get("validation_warnings", [])
        warning_text = f" [WARNINGS: {warnings}]" if warnings else ""
        print(f"  - {item['key']}: {item['value']}{warning_text}")


def test_mixed_scenario():
    """複合シナリオのテスト / Test mixed scenario"""
    print("\n\n" + "=" * 70)
    print("Test 3: Mixed Scenario / 複合シナリオテスト")
    print("=" * 70)

    manager = ProfileManager()

    # テスト用ユーザーとセッションを作成
    user = manager.create_user("複合テストユーザー", "male", "aoi")
    session = manager.create_session(user["user_id"])
    session_id = session["session_id"]

    test_data = [
        ("基本プロフィール", "名前", "山田太郎", True),
        ("基本プロフィール", "年齢", "30歳", True),
        ("基本プロフィール", "職業", "エンジニア", True),
        ("基本プロフィール", "住所", "東京都渋谷区", True),
        ("基本プロフィール", "家族構成", "独身", True),
        ("基本プロフィール", "家族構成", "妻と子供2人", False),  # Should be rejected (contradiction)
        ("基本プロフィール", "住所", "東京都横浜", False),  # Should be rejected (geographic error)
        ("趣味・興味・娯楽", "趣味", "読書", True),
        ("趣味・興味・娯楽", "趣味", "プログラミング", True),
    ]

    print("\nAdding test data...")
    results = []

    for category, key, value, should_succeed in test_data:
        session_before = manager.get_session(session_id)
        count_before = len(session_before["extracted_data"][category])

        session = manager.add_extracted_data(session_id, category, key, value)

        session_after = manager.get_session(session_id)
        count_after = len(session_after["extracted_data"][category])

        actually_added = count_after > count_before
        success = actually_added == should_succeed

        status = "✅" if success else "❌"
        action = "added" if actually_added else "rejected"
        expected = "should add" if should_succeed else "should reject"

        print(f"{status} {category}/{key}={value}: {action} ({expected})")
        results.append(success)

    print("\n" + "=" * 70)
    print(f"Test Results: {results.count(True)}/{len(results)} tests passed")

    if all(results):
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed")

    print("\n" + "=" * 70)
    print("Final extracted data:")
    final_session = manager.get_session(session_id)
    for category, data_list in final_session["extracted_data"].items():
        if data_list:
            print(f"\n{category}:")
            for item in data_list:
                print(f"  - {item['key']}: {item['value']}")


if __name__ == "__main__":
    print("\n")
    print("🧪 Phase 1 Validation Tests")
    print("=" * 70)

    test_contradiction_detection()
    test_geographic_validation()
    test_mixed_scenario()

    print("\n\n" + "=" * 70)
    print("✅ Phase 1 validation testing complete!")
    print("=" * 70)
    print()
