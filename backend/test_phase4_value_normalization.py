#!/usr/bin/env python3
"""
Phase 4 テスト: 値正規化のテスト
Phase 4 Test: Value normalization test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from data_validator import DataValidator


def test_income_normalization():
    """年収・収入の正規化テスト / Test income normalization"""
    print("=" * 70)
    print("Test 1: Income Normalization / 年収正規化テスト")
    print("=" * 70)

    validator = DataValidator()

    test_cases = [
        # (input, expected_amount, expected_original)
        ("300万", 3000000, "300万"),
        ("300万円", 3000000, "300万円"),
        ("500万くらい", 5000000, "500万くらい"),
        ("1000万", 10000000, "1000万"),
        ("2億", 200000000, "2億"),
        ("450万円程度", 4500000, "450万円程度"),
    ]

    passed = 0
    failed = 0

    print("\nIncome normalization tests:")
    for input_val, expected_amount, expected_original in test_cases:
        result = validator._normalize_income(input_val)

        # 辞書型の結果を期待
        if isinstance(result, dict):
            actual_amount = result.get("amount")
            actual_original = result.get("original")

            if actual_amount == expected_amount and actual_original == expected_original:
                print(f"  ✅ '{input_val}' → {actual_amount:,} JPY")
                passed += 1
            else:
                print(f"  ❌ '{input_val}' → {actual_amount} (expected: {expected_amount})")
                failed += 1
        else:
            print(f"  ❌ '{input_val}' → {result} (expected structured data)")
            failed += 1

    print(f"\nResults: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_age_normalization():
    """年齢の正規化テスト / Test age normalization"""
    print("\n\n" + "=" * 70)
    print("Test 2: Age Normalization / 年齢正規化テスト")
    print("=" * 70)

    validator = DataValidator()

    test_cases = [
        # (input, expected_result)
        ("30歳", {"age": 30, "original": "30歳"}),
        ("25歳", {"age": 25, "original": "25歳"}),
        ("50代", {"age_range": [50, 59], "original": "50代"}),
        ("30代前半", {"age_range": [30, 34], "original": "30代前半"}),
        ("40代後半", {"age_range": [45, 49], "original": "40代後半"}),
        ("20-30", {"age_range": [20, 30], "original": "20-30"}),
    ]

    passed = 0
    failed = 0

    print("\nAge normalization tests:")
    for input_val, expected in test_cases:
        result = validator._normalize_age(input_val)

        if isinstance(result, dict) and result == expected:
            if "age" in result:
                print(f"  ✅ '{input_val}' → age: {result['age']}")
            elif "age_range" in result:
                print(f"  ✅ '{input_val}' → age_range: {result['age_range']}")
            passed += 1
        else:
            print(f"  ❌ '{input_val}' → {result}")
            print(f"      Expected: {expected}")
            failed += 1

    print(f"\nResults: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_address_normalization():
    """住所の正規化テスト / Test address normalization"""
    print("\n\n" + "=" * 70)
    print("Test 3: Address Normalization / 住所正規化テスト")
    print("=" * 70)

    validator = DataValidator()

    test_cases = [
        # (input, should_validate, should_have_prefecture, should_have_city)
        ("東京都渋谷区", True, True, True),
        ("神奈川県横浜市", True, True, True),
        ("東京都横浜", False, True, False),  # 地理的エラー（都道府県は検出されるが市区町村が合わない）
        ("大阪府大阪市", True, True, True),
    ]

    passed = 0
    failed = 0

    print("\nAddress normalization tests:")
    for input_val, should_validate, should_have_pref, should_have_city in test_cases:
        result = validator._normalize_address(input_val)

        if isinstance(result, dict):
            validated = result.get("validated", False)
            has_pref = "prefecture" in result
            has_city = "city" in result

            if (validated == should_validate and
                has_pref == should_have_pref and
                has_city == should_have_city):

                if validated:
                    print(f"  ✅ '{input_val}' → {result.get('prefecture', '')}/{result.get('city', '')}")
                else:
                    print(f"  ✅ '{input_val}' → Invalid (as expected)")
                passed += 1
            else:
                print(f"  ❌ '{input_val}' → Unexpected result")
                print(f"      validated={validated}, has_pref={has_pref}, has_city={has_city}")
                print(f"      Expected: validated={should_validate}, has_pref={should_have_pref}, has_city={should_have_city}")
                failed += 1
        else:
            print(f"  ❌ '{input_val}' → {result} (expected structured data)")
            failed += 1

    print(f"\nResults: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_normalize_value_integration():
    """normalize_value統合テスト / Test normalize_value integration"""
    print("\n\n" + "=" * 70)
    print("Test 4: normalize_value Integration / 統合テスト")
    print("=" * 70)

    validator = DataValidator()

    test_cases = [
        # (category, key, value, expected_type)
        ("経済・消費", "年収", "500万", dict),
        ("基本プロフィール", "年齢", "35歳", dict),
        ("基本プロフィール", "住所", "東京都渋谷区", dict),
        ("趣味・興味・娯楽", "趣味", "読書", str),  # 正規化不要
        ("現在の生活", "食事", "朝7時", str),  # 正規化不要
    ]

    passed = 0
    failed = 0

    print("\nnormalize_value integration tests:")
    for category, key, value, expected_type in test_cases:
        result = validator.normalize_value(category, key, value)
        result_type = type(result)

        if result_type == expected_type:
            if isinstance(result, dict):
                # 構造化データの場合は詳細表示
                if "amount" in result:
                    print(f"  ✅ {category}/{key}: '{value}' → {result['amount']:,} JPY")
                elif "age" in result:
                    print(f"  ✅ {category}/{key}: '{value}' → age: {result['age']}")
                elif "prefecture" in result:
                    print(f"  ✅ {category}/{key}: '{value}' → {result.get('prefecture', '')}/{result.get('city', '')}")
                else:
                    print(f"  ✅ {category}/{key}: '{value}' → {result}")
            else:
                # 文字列のままの場合
                print(f"  ✅ {category}/{key}: '{value}' (no normalization needed)")
            passed += 1
        else:
            print(f"  ❌ {category}/{key}: '{value}' → {result_type} (expected: {expected_type})")
            failed += 1

    print(f"\nResults: {passed}/{passed+failed} tests passed")
    return failed == 0


def test_approximate_income():
    """概算年収の検出テスト / Test approximate income detection"""
    print("\n\n" + "=" * 70)
    print("Test 5: Approximate Income Detection / 概算年収検出テスト")
    print("=" * 70)

    validator = DataValidator()

    test_cases = [
        # (input, should_be_approximate)
        ("500万くらい", True),
        ("500万ぐらい", True),
        ("500万程度", True),
        ("500万前後", True),
        ("約500万", True),
        ("500万", False),
        ("500万円", False),
    ]

    passed = 0
    failed = 0

    print("\nApproximate income tests:")
    for input_val, should_be_approx in test_cases:
        result = validator._normalize_income(input_val)

        if isinstance(result, dict):
            is_approximate = result.get("approximate", False)

            if is_approximate == should_be_approx:
                approx_text = " (approximate)" if is_approximate else ""
                print(f"  ✅ '{input_val}' → {result.get('amount', 0):,} JPY{approx_text}")
                passed += 1
            else:
                print(f"  ❌ '{input_val}' → approximate={is_approximate} (expected: {should_be_approx})")
                failed += 1
        else:
            print(f"  ❌ '{input_val}' → {result} (expected structured data)")
            failed += 1

    print(f"\nResults: {passed}/{passed+failed} tests passed")
    return failed == 0


if __name__ == "__main__":
    print("\n")
    print("🧪 Phase 4 Value Normalization Tests")
    print("=" * 70)

    results = []
    results.append(("Income Normalization", test_income_normalization()))
    results.append(("Age Normalization", test_age_normalization()))
    results.append(("Address Normalization", test_address_normalization()))
    results.append(("normalize_value Integration", test_normalize_value_integration()))
    results.append(("Approximate Income Detection", test_approximate_income()))

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
        print("\n🎉 Phase 4 complete! All value normalization tests passed!")
        exit(0)
    else:
        print(f"\n⚠️  {total_tests - total_passed} test suite(s) failed")
        exit(1)
