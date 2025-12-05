"""
ゲーミフィケーション: バッジシステム、ランダムイベント、リアクション判定
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import BADGES, RANDOM_EVENTS, REACTION_TIERS


class GamificationManager:
    """ゲーミフィケーション要素を管理するクラス"""

    def __init__(self):
        pass

    def check_badges(self, profile: Dict, session_data: Dict) -> List[str]:
        """
        新規獲得バッジをチェック
        Returns: 新しく獲得したバッジのリスト
        """
        newly_earned = []
        current_badges = profile.get("badges", [])

        # 各バッジの条件をチェック
        for badge_name, badge_info in BADGES.items():
            if badge_name in current_badges:
                continue  # すでに獲得済み

            if self._check_badge_condition(badge_name, profile, session_data):
                newly_earned.append(badge_name)

        return newly_earned

    def _check_badge_condition(self, badge_name: str, profile: Dict,
                               session_data: Dict) -> bool:
        """個別のバッジ条件をチェック"""
        # 簡易的な条件チェック（実際はより詳細な分析が必要）
        if badge_name == "オープンハート":
            return session_data.get("emotional_count", 0) >= 3

        elif badge_name == "ストーリーテラー":
            return session_data.get("has_life_event", False)

        elif badge_name == "多趣味":
            hobby_count = self._count_hobbies(profile)
            return hobby_count >= 5

        elif badge_name == "哲学者":
            return session_data.get("philosophy_depth", 0) >= 3

        elif badge_name == "継続は力なり":
            return self._check_consecutive_days(profile) >= 3

        elif badge_name == "夜更かし":
            return self._is_late_night_session()

        elif badge_name == "長い付き合い":
            return len(profile.get("sessions", [])) >= 10

        elif badge_name == "サプライズ":
            return session_data.get("has_surprise", False)

        elif badge_name == "思索者":
            return session_data.get("deep_thought_count", 0) >= 3

        elif badge_name == "記憶の守護者":
            return session_data.get("has_childhood_memory", False)

        return False

    def _count_hobbies(self, profile: Dict) -> int:
        """趣味の数をカウント（簡易版）"""
        # 実際のセッションデータから趣味カテゴリーの項目数を数える必要がある
        # ここでは仮実装
        return 0

    def _check_consecutive_days(self, profile: Dict) -> int:
        """連続日数をチェック"""
        sessions = profile.get("sessions", [])
        if len(sessions) < 3:
            return 0

        # セッション日付を取得して連続性をチェック
        # 簡易版実装
        return 0

    def _is_late_night_session(self) -> bool:
        """深夜セッション（0時以降）かチェック"""
        now = datetime.now()
        return now.hour >= 0 and now.hour < 6

    def should_trigger_event(self) -> Optional[Dict]:
        """ランダムイベントを発動すべきかチェック"""
        for event_name, event_info in RANDOM_EVENTS.items():
            trigger_rate = event_info.get("trigger_rate", 0.1)
            if random.random() < trigger_rate:
                return {
                    "name": event_name,
                    "prompt": event_info["prompt"],
                    "category": event_info["category"]
                }
        return None

    def determine_reaction(self, message: str, context: Dict = None) -> str:
        """
        ユーザーメッセージからリアクションレベルを判定
        Returns: "small", "medium", "large"
        """
        message_length = len(message)

        # 特定のキーワードチェック
        emotional_keywords = ["嬉しい", "悲しい", "楽しい", "辛い", "感動", "幸せ"]
        specific_keywords = ["実は", "昔は", "今は", "将来は", "夢は"]

        has_emotional = any(keyword in message for keyword in emotional_keywords)
        has_specific = any(keyword in message for keyword in specific_keywords)
        has_numbers = any(char.isdigit() for char in message)

        # Large: 100文字以上 + 感情的 + 具体的
        if message_length >= REACTION_TIERS["large"]["threshold"]:
            if has_emotional or has_specific:
                return "large"

        # Medium: 50文字以上 + (感情的 or 具体的 or 数字)
        if message_length >= REACTION_TIERS["medium"]["threshold"]:
            if has_emotional or has_specific or has_numbers:
                return "medium"

        # Small: 20文字以上
        if message_length >= REACTION_TIERS["small"]["threshold"]:
            return "small"

        return "none"

    def analyze_message_for_data(self, message: str) -> Dict:
        """
        メッセージを分析してプロファイリングデータとメタ情報を抽出
        Returns: {
            "emotional_count": int,
            "has_life_event": bool,
            "philosophy_depth": int,
            ...
        }
        """
        analysis = {
            "emotional_count": 0,
            "has_life_event": False,
            "philosophy_depth": 0,
            "deep_thought_count": 0,
            "has_surprise": False,
            "has_childhood_memory": False
        }

        # 感情的な言葉のカウント
        emotional_keywords = ["嬉しい", "悲しい", "楽しい", "辛い", "感動", "幸せ",
                             "苦しい", "寂しい", "懐かしい", "ワクワク"]
        analysis["emotional_count"] = sum(
            1 for keyword in emotional_keywords if keyword in message
        )

        # 人生の転機を示す言葉
        life_event_keywords = ["転職", "結婚", "出産", "卒業", "引越し", "転機",
                              "変わった", "決断", "別れ"]
        analysis["has_life_event"] = any(
            keyword in message for keyword in life_event_keywords
        )

        # 価値観を示す言葉
        philosophy_keywords = ["大切", "信じる", "思う", "考え", "価値観",
                              "理想", "目標", "夢"]
        analysis["philosophy_depth"] = sum(
            1 for keyword in philosophy_keywords if keyword in message
        )

        # 深い思考
        if len(message) > 100 and analysis["philosophy_depth"] > 0:
            analysis["deep_thought_count"] = 1

        # サプライズ要素
        surprise_keywords = ["実は", "意外と", "驚き", "びっくり"]
        analysis["has_surprise"] = any(
            keyword in message for keyword in surprise_keywords
        )

        # 幼少期の記憶
        childhood_keywords = ["子供の頃", "小さい頃", "幼稚園", "小学校",
                            "昔は", "子どもの時"]
        analysis["has_childhood_memory"] = any(
            keyword in message for keyword in childhood_keywords
        )

        return analysis

    def get_expression_for_reaction(self, reaction_tier: str,
                                    message_analysis: Dict = None) -> str:
        """
        リアクションレベルとメッセージ分析から適切な表情を選択
        Returns: 表情名 (normal, smile, surprised, thinking, empathy, encourage)
        """
        if reaction_tier == "large":
            if message_analysis and message_analysis.get("emotional_count", 0) > 0:
                return "empathy"
            return "surprised"

        elif reaction_tier == "medium":
            if message_analysis and message_analysis.get("has_surprise"):
                return "surprised"
            if message_analysis and message_analysis.get("philosophy_depth", 0) > 0:
                return "thinking"
            return "smile"

        elif reaction_tier == "small":
            return "normal"

        return "normal"
