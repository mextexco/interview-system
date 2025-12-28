#!/usr/bin/env python3
"""
インタラクティブ面接セッション / Interactive Interview Session
ターミナルから面接を実行できます
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from profile_manager import ProfileManager
from interviewer import Interviewer

def interactive_session():
    """
    インタラクティブな面接セッション
    Interactive interview session
    """
    print("\n" + "=" * 80)
    print("🎤 インタラクティブ面接セッション / Interactive Interview Session")
    print("=" * 80)
    print("\nCtrl+C で終了 / Press Ctrl+C to exit\n")

    # 初期化
    manager = ProfileManager()
    interviewer = Interviewer()

    # LM Studio接続確認
    print("LM Studio接続確認中...")
    if not interviewer.check_lm_studio_connection():
        print("❌ LM Studioに接続できません。")
        print("   LM Studioを起動して、モデルをロードしてください。")
        return

    print("✅ LM Studio接続成功\n")

    # ユーザー名入力
    user_name = input("あなたの名前を入力してください: ").strip()
    if not user_name:
        user_name = "ゲストユーザー"

    # 性別選択
    print("\n性別を選択してください:")
    print("1. 男性 (male)")
    print("2. 女性 (female)")
    print("3. その他 (other)")
    gender_choice = input("番号を入力 [1-3]: ").strip()

    gender_map = {"1": "male", "2": "female", "3": "other"}
    gender = gender_map.get(gender_choice, "other")

    # キャラクター選択
    print("\n面接官を選択してください:")
    print("1. 健太 (kenta) - 落ち着いて知的な男性")
    print("2. 美咲 (misaki) - 明るく聞き上手な女性")
    print("3. あおい (aoi) - 親しみやすく中性的")
    char_choice = input("番号を入力 [1-3]: ").strip()

    char_map = {"1": "kenta", "2": "misaki", "3": "aoi"}
    character_id = char_map.get(char_choice, "kenta")

    # ユーザー・セッション作成
    print(f"\nユーザー '{user_name}' を作成中...")
    user = manager.create_user(user_name, gender, character_id)
    user_id = user["user_id"]

    print(f"セッション作成中...")
    session = manager.create_session(user_id)
    session_id = session["session_id"]

    print(f"\n✅ セッションID: {session_id}")
    print(f"✅ ユーザーID: {user_id}\n")

    # 挨拶
    greeting = interviewer.generate_greeting(character_id, user_name)
    print(f"🤖 面接官: {greeting}")

    first_question = interviewer.generate_first_question(character_id)
    print(f"🤖 面接官: {first_question}\n")

    # 会話履歴
    conversation_history = []
    turn_count = 0

    try:
        while True:
            # ユーザー入力
            user_input = input("👤 あなた: ").strip()

            if not user_input:
                continue

            # 終了コマンド
            if user_input.lower() in ['quit', 'exit', '終了', 'q']:
                print("\n面接を終了します...")
                break

            turn_count += 1

            # 会話履歴に追加
            conversation_history.append({
                "role": "user",
                "content": user_input
            })

            # データ抽出（バックグラウンド）
            print("\n[データ抽出中...]")

            # AIレスポンス取得
            category_counts = manager.get_category_data_count(user_id)
            empty_categories = [
                cat for cat in ["基本プロフィール", "ライフストーリー", "現在の生活",
                               "健康・ライフスタイル", "趣味・興味・娯楽"]
                if category_counts.get(cat, 0) == 0
            ]

            assistant_response = interviewer.get_response(
                conversation_history,
                character_id,
                user,
                category_counts,
                empty_categories
            )

            if not assistant_response:
                print("⚠️  AIレスポンスを取得できませんでした。")
                continue

            # 会話履歴に追加
            conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })

            # AIレスポンス表示
            print(f"\n🤖 面接官: {assistant_response}\n")

            # データ抽出
            extracted_data = interviewer.extract_profile_data(
                user_input,
                assistant_response,
                conversation_history
            )

            # データ保存
            if extracted_data:
                print(f"[✅ {len(extracted_data)}件のデータを抽出]")
                for data_point in extracted_data:
                    session = manager.add_extracted_data(
                        session_id,
                        data_point["category"],
                        data_point["key"],
                        data_point["value"]
                    )

            # 5ターンごとに進捗表示
            if turn_count % 5 == 0:
                print("\n" + "=" * 80)
                print("📊 現在の収集データ:")
                current_session = manager.get_session(session_id)
                total_points = 0
                for category, data_list in current_session["extracted_data"].items():
                    if data_list:
                        total_points += len(data_list)
                        print(f"  {category}: {len(data_list)}件")
                print(f"  合計: {total_points}件")
                print("=" * 80 + "\n")

    except KeyboardInterrupt:
        print("\n\n面接を終了します...")

    # 最終結果表示
    print("\n\n" + "=" * 80)
    print("📊 面接結果 / Interview Results")
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
                        value_display = f"{value_display['amount']:,} JPY"
                    elif 'age' in value_display:
                        value_display = f"年齢: {value_display['age']}"
                    elif 'age_range' in value_display:
                        value_display = f"年齢範囲: {value_display['age_range'][0]}-{value_display['age_range'][1]}"
                    elif 'prefecture' in value_display:
                        value_display = f"{value_display['prefecture']}/{value_display.get('city', '')}"

                print(f"  - {item['key']}: {value_display}")

                # データバージョン表示
                if item.get('data_version') == '2.0':
                    print(f"    [正規化済み v2.0]")

    print(f"\n総データポイント数: {total_data_points}")
    print(f"会話ターン数: {turn_count}")

    if turn_count > 0:
        extraction_rate = (total_data_points / turn_count) * 100
        print(f"データ抽出率: {extraction_rate:.1f}%")

    print("\n" + "=" * 80)
    print(f"セッションデータは以下に保存されています:")
    print(f"  data/sessions/{session_id}.json")
    print("=" * 80)


if __name__ == "__main__":
    try:
        interactive_session()
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
