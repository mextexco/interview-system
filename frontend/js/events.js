/**
 * ランダムイベントシステム
 */

// イベントタイプ定義
const EVENT_TYPES = {
    QUIZ: 'quiz',              // 二択クイズ
    ASSOCIATION: 'association', // 連想ゲーム
    MEMORY: 'memory',           // 思い出話
    DEEP_QUESTION: 'deep_question' // 特別な質問
};

// イベントデータ
const EVENTS = {
    quiz: [
        {
            question: "朝型派？夜型派？",
            options: ["朝型", "夜型"],
            category: "現在の生活"
        },
        {
            question: "インドア派？アウトドア派？",
            options: ["インドア", "アウトドア"],
            category: "趣味・興味・娯楽"
        },
        {
            question: "計画的？即興的？",
            options: ["計画的", "即興的"],
            category: "価値観・将来"
        },
        {
            question: "一人が好き？みんなが好き？",
            options: ["一人", "みんな"],
            category: "人間関係・コミュニティ"
        }
    ],
    association: [
        {
            keyword: "夏",
            prompt: "「夏」と聞いて最初に思い浮かぶことは？",
            category: "趣味・興味・娯楽"
        },
        {
            keyword: "家族",
            prompt: "「家族」と聞いて思い浮かぶエピソードは？",
            category: "人間関係・コミュニティ"
        },
        {
            keyword: "挑戦",
            prompt: "「挑戦」と聞いて思い出すことは？",
            category: "ライフストーリー"
        },
        {
            keyword: "リラックス",
            prompt: "「リラックス」するとき、何をしますか？",
            category: "健康・ライフスタイル"
        }
    ],
    memory: [
        {
            theme: "子どもの頃の夢",
            question: "子どもの頃、将来何になりたかった？",
            category: "ライフストーリー"
        },
        {
            theme: "一番の思い出",
            question: "これまでで一番印象に残っている出来事は？",
            category: "ライフストーリー"
        },
        {
            theme: "初めての経験",
            question: "最近、初めて体験したことはある？",
            category: "学習・成長"
        },
        {
            theme: "大切な人",
            question: "あなたにとって大切な人は誰ですか？",
            category: "人間関係・コミュニティ"
        }
    ],
    deep_question: [
        {
            question: "人生で一番大切にしていることは？",
            category: "価値観・将来"
        },
        {
            question: "もし明日世界が終わるなら、今日何をする？",
            category: "価値観・将来"
        },
        {
            question: "今の自分を一言で表すと？",
            category: "基本プロフィール"
        },
        {
            question: "10年後の自分はどうなっていたい？",
            category: "価値観・将来"
        }
    ]
};

// イベント発生確率（10%）
const EVENT_TRIGGER_CHANCE = 0.1;

// 最小会話数（この回数以降からイベント発生）
const MIN_MESSAGES_FOR_EVENT = 3;

// 現在のイベント
let currentEvent = null;

/**
 * ランダムイベントをトリガー判定
 */
function shouldTriggerEvent(messageCount) {
    if (messageCount < MIN_MESSAGES_FOR_EVENT) {
        return false;
    }
    return Math.random() < EVENT_TRIGGER_CHANCE;
}

/**
 * ランダムイベントを選択
 */
function selectRandomEvent() {
    // ランダムにイベントタイプを選択
    const types = Object.keys(EVENT_TYPES);
    const randomType = types[Math.floor(Math.random() * types.length)];

    // そのタイプからランダムにイベントを選択
    const eventList = EVENTS[randomType];
    const randomEvent = eventList[Math.floor(Math.random() * eventList.length)];

    return {
        type: randomType,
        data: randomEvent
    };
}

/**
 * イベントモーダルを表示
 */
function showEventModal(event) {
    currentEvent = event;
    const modal = document.getElementById('eventModal');
    const title = document.getElementById('eventTitle');
    const content = document.getElementById('eventContent');
    const choicesDiv = document.getElementById('eventChoices');
    const inputDiv = document.getElementById('eventInput');

    // タイトル設定
    const titles = {
        quiz: "🎯 クイックアンサー",
        association: "💭 連想ゲーム",
        memory: "📖 思い出話",
        deep_question: "✨ 特別な質問"
    };
    title.textContent = titles[event.type];

    // コンテンツ設定
    if (event.type === 'quiz') {
        content.textContent = event.data.question;
        choicesDiv.innerHTML = '';
        event.data.options.forEach(option => {
            const btn = document.createElement('button');
            btn.className = 'event-choice-btn';
            btn.textContent = option;
            btn.onclick = () => handleEventChoice(option);
            choicesDiv.appendChild(btn);
        });
        choicesDiv.style.display = 'flex';
        inputDiv.style.display = 'none';
    } else if (event.type === 'association') {
        content.textContent = event.data.prompt;
        inputDiv.style.display = 'block';
        choicesDiv.style.display = 'none';
        document.getElementById('eventInputField').value = '';
        document.getElementById('eventInputField').placeholder = '自由に答えてください...';
    } else if (event.type === 'memory') {
        content.textContent = event.data.question;
        inputDiv.style.display = 'block';
        choicesDiv.style.display = 'none';
        document.getElementById('eventInputField').value = '';
        document.getElementById('eventInputField').placeholder = '思い出を教えてください...';
    } else if (event.type === 'deep_question') {
        content.textContent = event.data.question;
        inputDiv.style.display = 'block';
        choicesDiv.style.display = 'none';
        document.getElementById('eventInputField').value = '';
        document.getElementById('eventInputField').placeholder = 'じっくり考えて答えてください...';
    }

    modal.classList.remove('hidden');
}

/**
 * 選択肢が選ばれた時の処理
 */
function handleEventChoice(choice) {
    if (!currentEvent) return;

    // メッセージとして送信
    const messageInput = document.getElementById('messageInput');
    const originalValue = messageInput.value;

    messageInput.value = choice;
    sendMessage();

    // モーダルを閉じる
    closeEventModal();
}

/**
 * イベント入力を送信
 */
function submitEventInput() {
    const input = document.getElementById('eventInputField');
    const value = input.value.trim();

    if (!value) {
        alert('回答を入力してください');
        return;
    }

    // メッセージとして送信
    const messageInput = document.getElementById('messageInput');
    messageInput.value = value;
    sendMessage();

    // モーダルを閉じる
    closeEventModal();
}

/**
 * イベントモーダルを閉じる
 */
function closeEventModal() {
    const modal = document.getElementById('eventModal');
    modal.classList.add('hidden');
    currentEvent = null;
}

/**
 * イベントモーダルのセットアップ
 */
function setupEventModal() {
    const modal = document.getElementById('eventModal');
    if (modal) {
        modal.classList.add('hidden');
    }

    const submitBtn = document.getElementById('eventSubmitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitEventInput);
    }

    const skipBtn = document.getElementById('eventSkipBtn');
    if (skipBtn) {
        skipBtn.addEventListener('click', closeEventModal);
    }

    // Enterキーで送信
    const inputField = document.getElementById('eventInputField');
    if (inputField) {
        inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                submitEventInput();
            }
        });
    }
}

// ページ読み込み時に初期化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupEventModal);
} else {
    setupEventModal();
}
