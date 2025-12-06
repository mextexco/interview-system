/**
 * 音声機能: Web Speech API (音声認識・音声合成)
 */

// 音声認識の設定
let recognition = null;
let isRecording = false;

// 音声合成の設定
const synth = window.speechSynthesis;
let currentVoice = null;

/**
 * 音声認識を初期化
 */
function initSpeechRecognition() {
    // ブラウザ対応チェック
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn('このブラウザは音声認識に対応していません');
        return false;
    }

    recognition = new SpeechRecognition();
    recognition.lang = 'ja-JP';
    recognition.continuous = false;
    recognition.interimResults = false;

    // 認識結果のハンドリング
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('[Voice] Recognition result:', transcript);

        // 認識したテキストを入力欄に設定
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.value = transcript;
            // 自動送信
            sendMessage();
        }
    };

    recognition.onerror = (event) => {
        console.error('[Voice] Recognition error:', event.error);
        stopRecording();

        if (event.error === 'no-speech') {
            showVoiceError('音声が検出されませんでした');
        } else if (event.error === 'not-allowed') {
            showVoiceError('マイクへのアクセスが許可されていません');
        }
    };

    recognition.onend = () => {
        stopRecording();
    };

    return true;
}

/**
 * 音声認識を開始
 */
function startRecording() {
    if (!recognition) {
        if (!initSpeechRecognition()) {
            alert('音声認識が利用できません。ブラウザを確認してください。');
            return;
        }
    }

    if (isRecording) {
        stopRecording();
        return;
    }

    try {
        recognition.start();
        isRecording = true;
        updateMicButton(true);
        console.log('[Voice] Recording started');
    } catch (error) {
        console.error('[Voice] Failed to start recording:', error);
    }
}

/**
 * 音声認識を停止
 */
function stopRecording() {
    if (recognition && isRecording) {
        recognition.stop();
        isRecording = false;
        updateMicButton(false);
        console.log('[Voice] Recording stopped');
    }
}

/**
 * マイクボタンの表示を更新
 */
function updateMicButton(recording) {
    const micButton = document.getElementById('micButton');
    if (!micButton) return;

    if (recording) {
        micButton.classList.add('recording');
        micButton.textContent = '🎤';
        micButton.title = '録音中...（クリックで停止）';
    } else {
        micButton.classList.remove('recording');
        micButton.textContent = '🎙️';
        micButton.title = '音声入力を開始';
    }
}

/**
 * 音声エラーメッセージを表示
 */
function showVoiceError(message) {
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        const originalPlaceholder = messageInput.placeholder;
        messageInput.placeholder = message;
        setTimeout(() => {
            messageInput.placeholder = originalPlaceholder;
        }, 3000);
    }
}

/**
 * テキストを音声で読み上げ
 */
function speakText(text, characterId = 'aoi') {
    if (!synth) {
        console.warn('このブラウザは音声合成に対応していません');
        return;
    }

    // 既存の音声を停止
    synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ja-JP';

    // キャラクターごとの音声設定
    const voiceSettings = getVoiceSettings(characterId);
    utterance.pitch = voiceSettings.pitch;
    utterance.rate = voiceSettings.rate;
    utterance.volume = voiceSettings.volume;

    // 利用可能な日本語音声を取得
    const voices = synth.getVoices();
    const japaneseVoice = voices.find(voice => voice.lang.startsWith('ja'));
    if (japaneseVoice) {
        utterance.voice = japaneseVoice;
    }

    // 読み上げ開始・終了イベント
    utterance.onstart = () => {
        console.log('[Voice] Speech started');
        updateSpeakerIcon(true);
    };

    utterance.onend = () => {
        console.log('[Voice] Speech ended');
        updateSpeakerIcon(false);
    };

    utterance.onerror = (event) => {
        console.error('[Voice] Speech error:', event.error);
        updateSpeakerIcon(false);
    };

    synth.speak(utterance);
}

/**
 * キャラクターごとの音声設定を取得
 */
function getVoiceSettings(characterId) {
    const settings = {
        'misaki': {
            pitch: 1.2,  // 高め（女性）
            rate: 1.0,   // 標準速度
            volume: 1.0
        },
        'kenta': {
            pitch: 0.8,  // 低め（男性）
            rate: 0.95,  // やや遅め
            volume: 1.0
        },
        'aoi': {
            pitch: 1.0,  // 標準（中性）
            rate: 1.0,
            volume: 1.0
        }
    };

    return settings[characterId] || settings['aoi'];
}

/**
 * スピーカーアイコンの表示を更新
 */
function updateSpeakerIcon(speaking) {
    const speakerIcon = document.getElementById('speakerIcon');
    if (!speakerIcon) return;

    if (speaking) {
        speakerIcon.textContent = '🔊';
        speakerIcon.classList.add('speaking');
    } else {
        speakerIcon.textContent = '🔇';
        speakerIcon.classList.remove('speaking');
    }
}

/**
 * 音声合成を停止
 */
function stopSpeaking() {
    if (synth) {
        synth.cancel();
        updateSpeakerIcon(false);
    }
}

/**
 * 音声機能の初期化（ページ読み込み時）
 */
function initVoiceFeatures() {
    // 音声認識の初期化
    initSpeechRecognition();

    // 音声合成の準備（音声リストを読み込む）
    if (synth) {
        // Chromeでは最初に getVoices() を呼ぶ必要がある
        synth.getVoices();

        // 音声リストが非同期で読み込まれる場合に対応
        if (synth.onvoiceschanged !== undefined) {
            synth.onvoiceschanged = () => {
                console.log('[Voice] Available voices loaded:', synth.getVoices().length);
            };
        }
    }

    console.log('[Voice] Voice features initialized');
}

// ページ読み込み時に音声機能を初期化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initVoiceFeatures);
} else {
    initVoiceFeatures();
}
