#!/usr/bin/env python3
"""
全フェーズ統合テスト / All Phases Integration Test
Runs all phase tests and provides a comprehensive report
"""

import sys
import os
import subprocess

def run_test(test_file, phase_name):
    """
    Run a test file and capture results
    テストファイルを実行して結果をキャプチャ
    """
    print("\n" + "=" * 80)
    print(f"Running {phase_name}")
    print("=" * 80)

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=60
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ {phase_name} timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running {phase_name}: {e}")
        return False


def main():
    """Main test runner"""
    print("\n")
    print("🧪" * 40)
    print("全フェーズ統合テスト / All Phases Integration Test")
    print("🧪" * 40)
    print("\n")

    # テストファイルとフェーズ名
    tests = [
        ("test_phase1_validation.py", "Phase 1: Data Validation & Contradiction Detection"),
        ("test_phase2_normalization.py", "Phase 2: Key Normalization"),
        ("test_phase4_value_normalization.py", "Phase 4: Value Normalization"),
    ]

    # Note: Phase 3 は LM Studio との統合が必要なためスキップ
    print("Note: Phase 3 requires LM Studio integration and will be validated during actual use.\n")

    results = {}

    # 各テストを実行
    for test_file, phase_name in tests:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(test_path):
            results[phase_name] = run_test(test_path, phase_name)
        else:
            print(f"❌ Test file not found: {test_file}")
            results[phase_name] = False

    # 総合結果
    print("\n\n" + "=" * 80)
    print("📊 総合テスト結果 / Overall Test Results")
    print("=" * 80)

    for phase_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {phase_name}")

    # 統計
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)

    print("\n" + "=" * 80)
    print(f"Total: {passed_tests}/{total_tests} phases passed")
    print("=" * 80)

    if passed_tests == total_tests:
        print("\n🎉🎉🎉 ALL TESTS PASSED! 全テスト合格！🎉🎉🎉")
        print("\n✅ データ品質改善の実装が完了しました！")
        print("✅ Data quality improvement implementation complete!")
        print("\n次のステップ:")
        print("1. 新しい面接セッションで動作確認")
        print("2. 抽出率・品質の測定")
        print("3. 既存データの一括正規化（オプション）")
        print("\nNext steps:")
        print("1. Test with new interview sessions")
        print("2. Measure extraction rate and quality")
        print("3. Bulk normalize existing data (optional)")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} phase(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
