"""
設定ファイル: LM Studio URL、キャラクター定義、カテゴリー定義
"""

import os

# LM Studio設定
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_MODEL = "local-model"  # LM Studioでは任意の名前でOK

# データ保存先
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")

# キャラクター定義
CHARACTERS = {
    "misaki": {
        "name": "美咲",
        "gender": "女性",
        "age": "20代後半",
        "description": "明るく聞き上手な女性",
        "tone": "フレンドリーで優しい",
        "for_user_gender": "男性",
        "expressions": ["normal", "smile", "surprised", "thinking", "empathy", "encourage"]
    },
    "kenta": {
        "name": "健太",
        "gender": "男性",
        "age": "30代前半",
        "description": "落ち着いて知的な男性",
        "tone": "穏やかで丁寧",
        "for_user_gender": "女性",
        "expressions": ["normal", "smile", "surprised", "thinking", "empathy", "encourage"]
    },
    "aoi": {
        "name": "あおい",
        "gender": "中性的",
        "age": "20代",
        "description": "親しみやすく中性的なキャラクター",
        "tone": "カジュアルで親しみやすい",
        "for_user_gender": "その他",
        "expressions": ["normal", "smile", "surprised", "thinking", "empathy", "encourage"]
    }
}

# プロファイリングカテゴリー定義
CATEGORIES = {
    "基本プロフィール": {
        "fields": ["名前", "性別", "年齢層", "職業", "家族構成"],
        "description": "基本的な情報"
    },
    "ライフストーリー": {
        "fields": ["学歴", "職歴", "人生の転機", "重要な出来事"],
        "description": "これまでの人生の歩み"
    },
    "現在の生活": {
        "fields": ["1日の過ごし方", "住環境", "生活リズム"],
        "description": "今の日常生活"
    },
    "健康・ライフスタイル": {
        "fields": ["運動習慣", "食事", "睡眠", "健康管理"],
        "description": "健康や生活習慣"
    },
    "趣味・興味・娯楽": {
        "fields": ["趣味", "好きなこと", "エンターテイメント", "休日の過ごし方"],
        "description": "好きなことや楽しみ"
    },
    "学習・成長": {
        "fields": ["学びたいこと", "スキル", "自己啓発", "勉強"],
        "description": "成長や学習への取り組み"
    },
    "人間関係・コミュニティ": {
        "fields": ["友人", "家族関係", "コミュニティ", "人付き合い"],
        "description": "人との繋がり"
    },
    "情報収集・メディア": {
        "fields": ["ニュース", "SNS", "情報源", "メディア利用"],
        "description": "情報との向き合い方"
    },
    "経済・消費": {
        "fields": ["買い物", "お金の使い方", "価値基準", "経済観"],
        "description": "お金や消費に関する考え"
    },
    "価値観・将来": {
        "fields": ["大切にしていること", "将来の夢", "目標", "人生観"],
        "description": "価値観や将来のビジョン"
    }
}

# バッジ定義
BADGES = {
    "オープンハート": {
        "description": "感情的な話を3回以上共有した",
        "condition": "emotional_count >= 3",
        "icon": "💖"
    },
    "ストーリーテラー": {
        "description": "人生の転機について語った",
        "condition": "has_life_event",
        "icon": "📖"
    },
    "多趣味": {
        "description": "5つ以上の趣味を持っている",
        "condition": "hobby_count >= 5",
        "icon": "🎨"
    },
    "哲学者": {
        "description": "価値観について深く語った",
        "condition": "philosophy_depth >= 3",
        "icon": "🤔"
    },
    "継続は力なり": {
        "description": "3日連続でセッションを行った",
        "condition": "consecutive_days >= 3",
        "icon": "🔥"
    },
    "夜更かし": {
        "description": "深夜0時以降に会話した",
        "condition": "late_night_session",
        "icon": "🌙"
    },
    "長い付き合い": {
        "description": "10回以上のセッションを完了",
        "condition": "session_count >= 10",
        "icon": "🏆"
    },
    "サプライズ": {
        "description": "予想外の一面を見せた",
        "condition": "has_surprise",
        "icon": "✨"
    },
    "思索者": {
        "description": "深い思考を共有した",
        "condition": "deep_thought_count >= 3",
        "icon": "💭"
    },
    "記憶の守護者": {
        "description": "幼少期の記憶を共有した",
        "condition": "has_childhood_memory",
        "icon": "🎈"
    }
}

# ランダムイベント定義
RANDOM_EVENTS = {
    "クイックトーク": {
        "prompt": "好きな食べ物ベスト3を教えて！",
        "category": "趣味・興味・娯楽",
        "trigger_rate": 0.15
    },
    "もしもトーク": {
        "prompt": "もし宝くじで1億円当たったら何する？",
        "category": "価値観・将来",
        "trigger_rate": 0.10
    },
    "思い出タイム": {
        "prompt": "子供の頃の一番楽しかった思い出は？",
        "category": "ライフストーリー",
        "trigger_rate": 0.15
    }
}

# 人間形成ステージ
HUMAN_STAGES = [
    {"stage": 1, "min_data": 0, "image": "stage1.svg", "description": "輪郭のみ"},
    {"stage": 2, "min_data": 10, "image": "stage2.svg", "description": "顔・体の輪郭"},
    {"stage": 3, "min_data": 25, "image": "stage3.svg", "description": "服装・基本"},
    {"stage": 4, "min_data": 50, "image": "stage4.svg", "description": "表情・アクセサリー"},
    {"stage": 5, "min_data": 100, "image": "stage5.svg", "description": "目に光・オーラ"}
]

# リアクション設定
REACTION_TIERS = {
    "small": {
        "threshold": 20,  # 文字数
        "sound": "pop.mp3",
        "effect": "expression_change"
    },
    "medium": {
        "threshold": 50,
        "sound": "chime.mp3",
        "effect": "particles"
    },
    "large": {
        "threshold": 100,
        "sound": "success.mp3",
        "effect": "flash"
    }
}
