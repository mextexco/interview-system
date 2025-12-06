/**
 * キャラクター表示と表情差分管理
 */

const CHARACTER_EMOJIS = {
    'misaki': '👩',
    'kenta': '👨',
    'aoi': '🧑'
};

const EXPRESSION_EMOJIS = {
    'normal': '😊',
    'smile': '😄',
    'surprised': '😲',
    'thinking': '🤔',
    'empathy': '🥺',
    'encourage': '💪'
};

/**
 * キャラクターのセットアップ
 */
function setupCharacter(characterId) {
    const characterData = getCharacterData(characterId);

    // ヘッダーにキャラクター名を表示
    document.getElementById('characterName').textContent = characterData.name;

    // アバターエリアにキャラクター表示
    const avatarEmoji = document.getElementById('avatarEmoji');
    avatarEmoji.textContent = CHARACTER_EMOJIS[characterId] || '👤';

    const characterNameDisplay = document.getElementById('characterNameDisplay');
    characterNameDisplay.textContent = characterData.name;
}

/**
 * 表情を更新
 */
function updateCharacterExpression(expression) {
    const avatarEmoji = document.getElementById('avatarEmoji');
    const emojiMap = EXPRESSION_EMOJIS;

    if (emojiMap[expression]) {
        avatarEmoji.textContent = emojiMap[expression];

        // 3秒後に元に戻す
        setTimeout(() => {
            const characterId = currentProfile?.character || 'aoi';
            avatarEmoji.textContent = CHARACTER_EMOJIS[characterId] || '👤';
        }, 3000);
    }
}

/**
 * キャラクターデータを取得（仮実装）
 */
function getCharacterData(characterId) {
    const characters = {
        'misaki': {
            name: '美咲',
            description: '明るく聞き上手な女性'
        },
        'kenta': {
            name: '健太',
            description: '落ち着いて知的な男性'
        },
        'aoi': {
            name: 'あおい',
            description: '親しみやすく中性的'
        }
    };

    return characters[characterId] || characters['aoi'];
}
