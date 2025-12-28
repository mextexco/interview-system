"""
プロファイル管理: ユーザープロファイルとセッションデータの保存・読み込み
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from config import PROFILES_DIR, SESSIONS_DIR, CATEGORIES, HUMAN_STAGES
from data_validator import DataValidator


class ProfileManager:
    """ユーザープロファイルとセッションを管理するクラス"""

    def __init__(self):
        # データディレクトリの作成
        os.makedirs(PROFILES_DIR, exist_ok=True)
        os.makedirs(SESSIONS_DIR, exist_ok=True)

    def create_user(self, name: str, gender: str, character: str) -> Dict:
        """新規ユーザープロファイルを作成"""
        user_id = str(uuid.uuid4())
        profile = {
            "user_id": user_id,
            "name": name,
            "gender": gender,
            "character": character,
            "created_at": datetime.now().isoformat(),
            "human_stage": 1,
            "badges": [],
            "total_data_count": 0,
            "sessions": []
        }

        # プロファイル保存
        self._save_profile(user_id, profile)
        return profile

    def get_user(self, user_id: str) -> Optional[Dict]:
        """ユーザープロファイルを取得"""
        profile_path = os.path.join(PROFILES_DIR, f"{user_id}.json")
        if not os.path.exists(profile_path):
            return None

        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def update_user(self, user_id: str, updates: Dict) -> Dict:
        """ユーザープロファイルを更新"""
        profile = self.get_user(user_id)
        if not profile:
            raise ValueError(f"User {user_id} not found")

        profile.update(updates)
        profile["updated_at"] = datetime.now().isoformat()
        self._save_profile(user_id, profile)
        return profile

    def create_session(self, user_id: str) -> Dict:
        """新規セッションを作成"""
        session_id = str(uuid.uuid4())
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "date": datetime.now().isoformat(),
            "conversation": [],
            "extracted_data": {cat: [] for cat in CATEGORIES.keys()},
            "events_triggered": [],
            "reactions": {
                "small": 0,
                "medium": 0,
                "large": 0
            }
        }

        # セッション保存
        self._save_session(session_id, session)

        # ユーザープロファイルにセッションIDを追加
        profile = self.get_user(user_id)
        if profile:
            profile["sessions"].append(session_id)
            self._save_profile(user_id, profile)

        return session

    def get_session(self, session_id: str) -> Optional[Dict]:
        """セッションを取得"""
        session_path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
        if not os.path.exists(session_path):
            return None

        with open(session_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def update_session(self, session_id: str, updates: Dict) -> Dict:
        """セッションを更新"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.update(updates)
        session["updated_at"] = datetime.now().isoformat()
        self._save_session(session_id, session)
        return session

    def add_message(self, session_id: str, role: str, content: str,
                   expression: str = "normal") -> Dict:
        """会話メッセージを追加"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        if role == "assistant":
            message["expression"] = expression

        session["conversation"].append(message)
        self._save_session(session_id, session)
        return session

    def add_extracted_data(self, session_id: str, category: str,
                          key: str, value: any) -> Dict:
        """
        抽出したプロファイリングデータを追加
        Add extracted profiling data with validation
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if category not in session["extracted_data"]:
            session["extracted_data"][category] = []

        # データバリデーションを実行 / Validate data
        validator = DataValidator()
        existing_data = session["extracted_data"][category]

        validation_result = validator.validate_data_point(
            category, key, value, existing_data
        )

        # 矛盾がある場合はスキップ / Skip if contradictions found
        if not validation_result["valid"]:
            contradictions = validation_result.get("contradictions", [])
            print(f"[Validation] Data rejected: {contradictions}")
            for contradiction in contradictions:
                print(f"  - {contradiction}")

            # 矛盾データは保存しない / Don't save contradictory data
            return session

        # 警告がある場合はログ出力 / Log warnings if any
        warnings = validation_result.get("warnings", [])
        if warnings:
            print(f"[Validation] Warnings for {category}/{key}:")
            for warning in warnings:
                print(f"  - {warning}")

        # 値を正規化 / Normalize value
        normalized_value = validator.normalize_value(category, key, value)

        # 正規化が行われたかチェック / Check if normalization occurred
        normalization_occurred = normalized_value != value
        if normalization_occurred:
            print(f"[Normalization] {category}/{key}: '{value}' → {normalized_value}")

        # データエントリ作成 / Create data entry
        data_entry = {
            "key": key,
            "value": normalized_value,
            "timestamp": datetime.now().isoformat(),
            "data_version": "2.0"  # バージョン追跡
        }

        # 正規化が行われた場合は元の値も保存 / Save original value if normalized
        if normalization_occurred:
            data_entry["original_value"] = value

        # バリデーション情報を追加（オプション） / Add validation info (optional)
        if warnings:
            data_entry["validation_warnings"] = warnings

        session["extracted_data"][category].append(data_entry)
        self._save_session(session_id, session)

        # ユーザーの総データ数と人間形成ステージを更新
        self._update_user_stage(session["user_id"])

        return session

    def get_category_data_count(self, user_id: str) -> Dict[str, int]:
        """各カテゴリーのデータ数を取得"""
        profile = self.get_user(user_id)
        if not profile:
            return {}

        category_counts = {cat: 0 for cat in CATEGORIES.keys()}

        for session_id in profile["sessions"]:
            session = self.get_session(session_id)
            if session:
                for category, data_list in session["extracted_data"].items():
                    category_counts[category] += len(data_list)

        return category_counts

    def get_total_data_count(self, user_id: str) -> int:
        """総データ数を取得"""
        category_counts = self.get_category_data_count(user_id)
        return sum(category_counts.values())

    def get_empty_categories(self, user_id: str) -> List[str]:
        """データが空のカテゴリーを取得"""
        category_counts = self.get_category_data_count(user_id)
        return [cat for cat, count in category_counts.items() if count == 0]

    def calculate_human_stage(self, data_count: int) -> int:
        """データ数から人間形成ステージを計算"""
        for i in range(len(HUMAN_STAGES) - 1, -1, -1):
            if data_count >= HUMAN_STAGES[i]["min_data"]:
                return HUMAN_STAGES[i]["stage"]
        return 1

    def add_badge(self, user_id: str, badge_name: str) -> Dict:
        """バッジを追加"""
        profile = self.get_user(user_id)
        if not profile:
            raise ValueError(f"User {user_id} not found")

        if badge_name not in profile["badges"]:
            profile["badges"].append(badge_name)
            self._save_profile(user_id, profile)

        return profile

    def _save_profile(self, user_id: str, profile: Dict):
        """プロファイルをファイルに保存"""
        profile_path = os.path.join(PROFILES_DIR, f"{user_id}.json")
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

    def _save_session(self, session_id: str, session: Dict):
        """セッションをファイルに保存"""
        session_path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(session, f, ensure_ascii=False, indent=2)

    def _update_user_stage(self, user_id: str):
        """ユーザーの人間形成ステージを更新"""
        total_count = self.get_total_data_count(user_id)
        new_stage = self.calculate_human_stage(total_count)

        profile = self.get_user(user_id)
        if profile:
            profile["human_stage"] = new_stage
            profile["total_data_count"] = total_count
            self._save_profile(user_id, profile)
