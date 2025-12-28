#!/usr/bin/env python3
"""
ライブセッションテスト / Live Session Test
実際の面接セッションで品質改善機能をテスト
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from profile_manager import ProfileManager
from interviewer import Interviewer
import uuid

def test_live_session():
    """
    実際の面接セッションで品質改善機能をテスト
    Test quality improvement features with a real interview session
    """
    print("\n" + "=" * 80)
    print("🧪 ライブセッションテスト / Live Session Quality Test")
    print("=" * 80)

    # 初期化
    manager = ProfileManager()
    interviewer = Interviewer()

    # LM Studio接続確認
    print("\n1. LM Studio接続確認...")
    if interviewer.check_lm_studio_connection():
        print("   ✅ LM Studio接続成功")
    else:
        print("   ❌ LM Studio接続失敗")
        return False

    # ユーザー作成
    print("\n2. テストユーザー作成...")
    user = manager.create_user("品質改善テストユーザー", "male", "kenta")
    user_id = user["user_id"]
    print(f"   ✅ ユーザーID: {user_id}")

    # セッション作成
    print("\n3. セッション作成...")
    session = manager.create_session(user_id)
    session_id = session["session_id"]
    print(f"   ✅ セッションID: {session_id}")

    # テストシナリオ：様々なデータパターン
    print("\n4. データ抽出・検証・正規化のテスト")
    print("=" * 80)

    test_scenarios = [
        {
            "name": "年収データの正規化",
            "user_message": "年収は500万くらいです",
            "expected_category": "経済・消費",
            "expected_key": "年収",
            "test_type": "normalization"
        },
        {
            "name": "年齢データの正規化",
            "user_message": "30代前半です",
            "expected_category": "基本プロフィール",
            "expected_key": "年齢",
            "test_type": "normalization"
        },
        {
            "name": "住所の地理的検証（正常）",
            "user_message": "東京都渋谷区に住んでいます",
            "expected_category": "基本プロフィール",
            "expected_key": "住所",
            "test_type": "geographic_validation"
        },
        {
            "name": "職業のキー正規化",
            "user_message": "仕事はITエンジニアです",
            "expected_category": "基本プロフィール",
            "expected_key": "職業",  # 「仕事」→「職業」に正規化されるべき
            "test_type": "key_normalization"
        },
        {
            "name": "家族構成（矛盾検出準備）",
            "user_message": "1人暮らしです",
            "expected_category": "基本プロフィール",
            "expected_key": "家族構成",
            "test_type": "baseline"
        }
    ]

    conversation_history = []
    results = []

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- シナリオ {i}: {scenario['name']} ---")
        print(f"ユーザー: {scenario['user_message']}")

        # AIレスポンス取得
        conversation_history.append({
            "role": "user",
            "content": scenario["user_message"]
        })

        # カテゴリー情報取得
        category_counts = manager.get_category_data_count(user_id)
        empty_categories = [cat for cat in ["基本プロフィール", "ライフストーリー", "現在の生活"]
                          if category_counts.get(cat, 0) == 0]

        assistant_response = interviewer.get_response(
            conversation_history,
            "kenta",
            user,
            category_counts,
            empty_categories
        )

        if assistant_response:
            print(f"AI: {assistant_response}")
            conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })

        # データ抽出
        extracted_data = interviewer.extract_profile_data(
            scenario["user_message"],
            assistant_response or "",
            conversation_history
        )

        print(f"\n抽出結果: {len(extracted_data)} データポイント")

        # 抽出されたデータを保存
        session_before = manager.get_session(session_id)
        data_count_before = sum(len(data) for data in session_before["extracted_data"].values())

        for data_point in extracted_data:
            session = manager.add_extracted_data(
                session_id,
                data_point["category"],
                data_point["key"],
                data_point["value"]
            )

        session_after = manager.get_session(session_id)
        data_count_after = sum(len(data) for data in session_after["extracted_data"].values())

        # 結果確認
        success = False
        if extracted_data:
            for data_point in extracted_data:
                print(f"  - {data_point['category']}/{data_point['key']}: {data_point['value']}")

                # シナリオの期待値と比較
                if (data_point['category'] == scenario['expected_category'] and
                    data_point['key'] == scenario['expected_key']):
                    success = True

        if data_count_after > data_count_before:
            print(f"✅ データ保存成功 ({data_count_before} → {data_count_after})")
        else:
            print(f"⚠️  データ保存なし")

        results.append({
            "scenario": scenario['name'],
            "success": success,
            "extracted_count": len(extracted_data)
        })

    # 矛盾検出テスト
    print(f"\n--- 追加シナリオ: 矛盾検出テスト ---")
    print("ユーザー: 家族は妻と子供2人の4人家族です")

    # このデータは「1人暮らし」と矛盾するため拒否されるべき
    session_before = manager.get_session(session_id)
    data_count_before = len(session_before["extracted_data"]["基本プロフィール"])

    # 直接データを追加して矛盾検出をテスト
    session = manager.add_extracted_data(
        session_id,
        "基本プロフィール",
        "家族構成",
        "妻と子供2人の4人家族"
    )

    session_after = manager.get_session(session_id)
    data_count_after = len(session_after["extracted_data"]["基本プロフィール"])

    if data_count_after == data_count_before:
        print("✅ 矛盾データが正しく拒否されました")
        results.append({
            "scenario": "矛盾検出",
            "success": True,
            "extracted_count": 0
        })
    else:
        print("❌ 矛盾データが保存されてしまいました")
        results.append({
            "scenario": "矛盾検出",
            "success": False,
            "extracted_count": 1
        })

    # 最終結果表示
    print("\n\n" + "=" * 80)
    print("📊 最終セッションデータ / Final Session Data")
    print("=" * 80)

    final_session = manager.get_session(session_id)
    total_data_points = 0

    for category, data_list in final_session["extracted_data"].items():
        if data_list:
            print(f"\n【{category}】 ({len(data_list)}件)")
            for item in data_list:
                total_data_points += 1

                # 値の表示
                value_display = item['value']
                if isinstance(value_display, dict):
                    # 正規化されたデータの場合
                    if 'amount' in value_display:
                        value_display = f"{value_display['amount']:,} JPY (元: {value_display.get('original', '')})"
                    elif 'age' in value_display:
                        value_display = f"年齢: {value_display['age']} (元: {value_display.get('original', '')})"
                    elif 'age_range' in value_display:
                        value_display = f"年齢範囲: {value_display['age_range']} (元: {value_display.get('original', '')})"
                    elif 'prefecture' in value_display:
                        value_display = f"{value_display['prefecture']}/{value_display.get('city', '')} (検証済み)"

                print(f"  - {item['key']}: {value_display}")

                # データバージョン表示
                if item.get('data_version') == '2.0':
                    print(f"    [v2.0: 正規化済み]")

                # 警告表示
                if 'validation_warnings' in item:
                    for warning in item['validation_warnings']:
                        print(f"    ⚠️  {warning}")

    # 統計サマリー
    print("\n" + "=" * 80)
    print("📈 統計サマリー / Statistics Summary")
    print("=" * 80)

    successful_scenarios = sum(1 for r in results if r['success'])
    total_scenarios = len(results)

    print(f"成功したシナリオ: {successful_scenarios}/{total_scenarios}")
    print(f"総データポイント数: {total_data_points}")
    print(f"データ抽出率: {(sum(r['extracted_count'] for r in results) / total_scenarios * 100):.1f}%")

    print("\nシナリオ別結果:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['scenario']}: {result['extracted_count']}件抽出")

    # 品質改善機能の動作確認
    print("\n" + "=" * 80)
    print("✅ 品質改善機能の動作確認")
    print("=" * 80)

    checks = [
        ("データ抽出", sum(r['extracted_count'] for r in results) > 0),
        ("キー正規化", any(r['scenario'] == '職業のキー正規化' and r['success'] for r in results)),
        ("値正規化", total_data_points > 0),
        ("矛盾検出", any(r['scenario'] == '矛盾検出' and r['success'] for r in results)),
        ("地理的検証", any(r['scenario'] == '住所の地理的検証（正常）' and r['success'] for r in results))
    ]

    for check_name, check_result in checks:
        status = "✅" if check_result else "❌"
        print(f"{status} {check_name}")

    all_checks_passed = all(check_result for _, check_result in checks)

    if all_checks_passed:
        print("\n🎉 すべての品質改善機能が正常に動作しています！")
        print("🎉 All quality improvement features are working correctly!")
        return True
    else:
        print("\n⚠️  一部の機能に問題があります")
        return False


if __name__ == "__main__":
    print("\n")
    try:
        success = test_live_session()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n中断されました")
        exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
