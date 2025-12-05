"""
インタビューロジック: LM Studioとの対話、プロンプト生成
"""

import requests
from typing import Dict, List, Optional
from config import (
    LM_STUDIO_URL, LM_STUDIO_MODEL, CHARACTERS, CATEGORIES
)


class Interviewer:
    """インタビューを管理するクラス"""

    def __init__(self):
        self.lm_studio_url = LM_STUDIO_URL

    def check_lm_studio_connection(self) -> bool:
        """LM Studioへの接続確認"""
        try:
            # 簡単なテストリクエスト
            response = requests.post(
                self.lm_studio_url,
                json={
                    "model": LM_STUDIO_MODEL,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                },
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"LM Studio connection error: {e}")
            return False

    def generate_system_prompt(self, character_id: str, profile: Dict,
                               category_counts: Dict[str, int],
                               empty_categories: List[str]) -> str:
        """システムプロンプトを生成"""
        character = CHARACTERS.get(character_id, CHARACTERS["aoi"])

        # カテゴリー情報を整形
        categories_info = "\n".join([
            f"- {cat}: {CATEGORIES[cat]['description']}"
            for cat in CATEGORIES.keys()
        ])

        # 収集済みデータの概要
        collected_summary = ", ".join([
            f"{cat}({count}件)"
            for cat, count in category_counts.items() if count > 0
        ])
        if not collected_summary:
            collected_summary = "まだありません"

        # 空白カテゴリー
        empty_cats = ", ".join(empty_categories) if empty_categories else "なし"

        system_prompt = f"""あなたは{character['name']}、{character['description']}です。

【会話スタイル】
- 1発言は15-25文字程度
- 質問は1つずつ、簡潔に
- 口語的でフレンドリーに（{character['tone']}）
- 長い説明や前置きは不要
- テンポ良く進める
- 自然な会話を心がける

【会話戦略】
- まず相手の名前を聞く（初回のみ）
- その後、自然な会話でプロファイリング
- 空白カテゴリーがあれば軽く振る（「そういえば〜」）
- ユーザーが話したいことを優先
- 無理に質問を続けない
- 相手の発言に共感しながら進める

【プロファイリングカテゴリー】
{categories_info}

【現在の状況】
- 収集済み情報: {collected_summary}
- 空白カテゴリー: {empty_cats}
- セッション回数: {len(profile.get('sessions', []))}

日本語で対話してください。短く、フレンドリーに！"""

        return system_prompt

    def get_response(self, messages: List[Dict], character_id: str,
                    profile: Dict, category_counts: Dict[str, int],
                    empty_categories: List[str],
                    max_tokens: int = 100) -> Optional[str]:
        """
        LM Studioからレスポンスを取得
        Args:
            messages: 会話履歴 [{"role": "user/assistant", "content": "..."}]
            character_id: キャラクターID
            profile: ユーザープロファイル
            category_counts: カテゴリー別データ数
            empty_categories: 空のカテゴリーリスト
            max_tokens: 最大トークン数
        Returns:
            AIの応答テキスト
        """
        try:
            # システムプロンプトを生成
            system_prompt = self.generate_system_prompt(
                character_id, profile, category_counts, empty_categories
            )

            # メッセージリストを構築
            full_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages

            # LM Studioにリクエスト
            response = requests.post(
                self.lm_studio_url,
                json={
                    "model": LM_STUDIO_MODEL,
                    "messages": full_messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.8,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                assistant_message = result["choices"][0]["message"]["content"]
                return assistant_message.strip()
            else:
                print(f"LM Studio error: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error getting response: {e}")
            return None

    def generate_greeting(self, character_id: str, user_name: str = None) -> str:
        """挨拶メッセージを生成"""
        character = CHARACTERS.get(character_id, CHARACTERS["aoi"])

        if user_name:
            return f"こんにちは{user_name}さん！今日もお話しましょう！"
        else:
            return f"こんにちは！{character['name']}です。よろしくね！"

    def generate_first_question(self, character_id: str) -> str:
        """最初の質問を生成"""
        return "お名前を教えてもらえますか？"

    def extract_user_name(self, message: str) -> Optional[str]:
        """ユーザーメッセージから名前を抽出（簡易版）"""
        # 簡易的な実装
        # 「〜です」「〜といいます」などのパターンから抽出
        patterns = ["です", "だよ", "といいます", "っていいます", "と申します"]

        for pattern in patterns:
            if pattern in message:
                # パターンの前の部分を取得
                parts = message.split(pattern)
                if parts[0]:
                    # 最後の単語を名前として取得
                    name_candidate = parts[0].strip().split()[-1]
                    # 短すぎる・長すぎる名前は除外
                    if 1 <= len(name_candidate) <= 10:
                        return name_candidate

        # パターンマッチしない場合、メッセージ全体が短ければそれを名前とする
        if len(message) <= 10 and not any(c in message for c in "。、！？"):
            return message.strip()

        return None

    def suggest_next_topic(self, empty_categories: List[str],
                          character_id: str) -> Optional[str]:
        """次の話題を提案"""
        if not empty_categories:
            return None

        # ランダムに1つ選ぶ
        import random
        category = random.choice(empty_categories)

        # カテゴリーに応じた質問例
        questions = {
            "基本プロフィール": "お仕事は何してます？",
            "ライフストーリー": "これまでどんな人生を？",
            "現在の生活": "普段どんな生活してる？",
            "健康・ライフスタイル": "運動とかしてる？",
            "趣味・興味・娯楽": "趣味は何ですか？",
            "学習・成長": "何か学んでることある？",
            "人間関係・コミュニティ": "友達とはよく会う？",
            "情報収集・メディア": "ニュースとか見る？",
            "経済・消費": "買い物好き？",
            "価値観・将来": "将来の夢とかある？"
        }

        return questions.get(category, "他に何か教えて！")
