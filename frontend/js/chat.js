/**
 * チャット機能: メッセージ送受信、表示
 */

// グローバル変数
let currentUserId = null;
let currentSessionId = null;
let currentProfile = null;
let messageCount = 0;
const API_BASE_URL = 'http://localhost:5001/api';

/**
 * LM Studio接続チェック
 */
async function checkLMStudioConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        const statusText = document.getElementById('lmStatusText');
        if (data.lm_studio === 'connected') {
            statusText.textContent = '●';
            statusText.classList.add('connected');
            statusText.classList.remove('disconnected');
        } else {
            statusText.textContent = '○';
            statusText.classList.add('disconnected');
            statusText.classList.remove('connected');
        }
    } catch (error) {
        console.error('Health check error:', error);
        const statusText = document.getElementById('lmStatusText');
        statusText.textContent = '✗';
        statusText.classList.add('disconnected');
    }
}

/**
 * スタートモーダルを表示
 */
function showStartModal() {
    const modal = document.getElementById('startModal');
    modal.classList.remove('hidden');

    // 性別ボタンにイベントリスナー
    const genderButtons = document.querySelectorAll('.gender-btn');
    genderButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const gender = btn.dataset.gender;
            startInterview(gender);
        });
    });
}

/**
 * インタビュー開始
 */
async function startInterview(gender) {
    try {
        // ユーザー作成
        const createResponse = await fetch(`${API_BASE_URL}/user/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gender: gender })
        });

        const createData = await createResponse.json();
        if (!createData.success) {
            alert('ユーザー作成に失敗しました');
            return;
        }

        currentUserId = createData.user_id;
        currentProfile = createData.profile;

        // セッション作成
        const sessionResponse = await fetch(`${API_BASE_URL}/session/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUserId })
        });

        const sessionData = await sessionResponse.json();
        if (!sessionData.success) {
            alert('セッション作成に失敗しました');
            return;
        }

        currentSessionId = sessionData.session.session_id;

        // メッセージカウントをリセット
        messageCount = 0;

        // キャラクター設定
        setupCharacter(currentProfile.character);

        // 初期メッセージを表示
        const conversation = sessionData.session.conversation;
        conversation.forEach(msg => {
            displayMessage(msg.role, msg.content, msg.expression);
        });

        // モーダルを閉じる
        document.getElementById('startModal').classList.add('hidden');

        // 入力を有効化
        document.getElementById('messageInput').disabled = false;
        document.getElementById('sendButton').disabled = false;

        // 送信ボタンイベント
        setupSendButton();

        // 音声ボタンイベント
        setupVoiceButton();

        // ビジュアライゼーション初期化
        updateHumanFormation(currentProfile.human_stage, 0);
        updateStatusDisplay(currentProfile);

    } catch (error) {
        console.error('Start interview error:', error);
        alert('エラーが発生しました');
    }
}

/**
 * 送信ボタンのセットアップ
 */
function setupSendButton() {
    const sendButton = document.getElementById('sendButton');
    const messageInput = document.getElementById('messageInput');

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

/**
 * 音声ボタンのセットアップ
 */
function setupVoiceButton() {
    const micButton = document.getElementById('micButton');
    if (micButton) {
        micButton.addEventListener('click', () => {
            startRecording();
        });
    }
}

/**
 * メッセージ送信
 */
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (!message) return;

    // ユーザーメッセージを表示
    displayMessage('user', message);

    // 入力をクリア
    messageInput.value = '';

    // ボタンを無効化（レスポンス待ち）
    const sendButton = document.getElementById('sendButton');
    sendButton.disabled = true;
    messageInput.disabled = true;

    try {
        // チャットAPIにリクエスト
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message
            })
        });

        const data = await response.json();

        if (!data.success) {
            alert('メッセージ送信に失敗しました');
            return;
        }

        // アシスタントメッセージを表示
        displayMessage('assistant', data.response, data.expression);

        // 音声で読み上げ
        if (typeof speakText === 'function') {
            speakText(data.response, currentProfile.character);
        }

        // リアクション演出
        if (data.reaction && data.reaction !== 'none') {
            triggerReaction(data.reaction);
        }

        // バッジ獲得
        if (data.badges && data.badges.length > 0) {
            for (const badgeName of data.badges) {
                showBadgeModal(badgeName);
            }
        }

        // ステージ変化
        if (data.stage_changed) {
            updateHumanFormation(data.new_stage, data.profile.total_data_count);
        }

        // プロファイル更新
        currentProfile = data.profile;
        updateStatusDisplay(currentProfile);

        // メッセージカウントを増やす
        messageCount++;

        // ランダムイベント判定
        if (typeof shouldTriggerEvent === 'function' && shouldTriggerEvent(messageCount)) {
            // 少し遅らせて表示（アシスタントの返答の後）
            setTimeout(() => {
                const event = selectRandomEvent();
                showEventModal(event);
            }, 1000);
        }

    } catch (error) {
        console.error('Send message error:', error);
        alert('エラーが発生しました');
    } finally {
        // ボタンを再有効化
        sendButton.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}

/**
 * メッセージを表示
 */
function displayMessage(role, content, expression = 'normal') {
    const chatContainer = document.getElementById('chatContainer');

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.textContent = content;

    messageDiv.appendChild(bubbleDiv);
    chatContainer.appendChild(messageDiv);

    // スクロール
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // アシスタントメッセージの場合、表情を更新
    if (role === 'assistant' && expression) {
        updateCharacterExpression(expression);
    }
}

/**
 * ステータス折りたたみのセットアップ
 */
function setupStatusToggle() {
    const toggle = document.getElementById('statusToggle');
    const content = document.getElementById('statusContent');
    const icon = toggle.querySelector('.toggle-icon');

    toggle.addEventListener('click', () => {
        content.classList.toggle('collapsed');
        icon.classList.toggle('rotated');
    });
}
