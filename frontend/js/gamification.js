/**
 * ゲーミフィケーション: バッジ、リアクション演出
 */

const BADGE_ICONS = {
    "オープンハート": "💖",
    "ストーリーテラー": "📖",
    "多趣味": "🎨",
    "哲学者": "🤔",
    "継続は力なり": "🔥",
    "夜更かし": "🌙",
    "長い付き合い": "🏆",
    "サプライズ": "✨",
    "思索者": "💭",
    "記憶の守護者": "🎈"
};

/**
 * バッジ獲得モーダルを表示
 */
function showBadgeModal(badgeName) {
    const modal = document.getElementById('badgeModal');
    const badgeIcon = document.getElementById('newBadgeIcon');
    const badgeNameElem = document.getElementById('newBadgeName');

    badgeIcon.textContent = BADGE_ICONS[badgeName] || '🏆';
    badgeNameElem.textContent = badgeName;

    modal.classList.remove('hidden');

    // 閉じるボタン
    const closeBtn = document.getElementById('closeBadgeBtn');
    closeBtn.onclick = () => {
        modal.classList.add('hidden');
        // バッジをバッジセクションに追加
        addBadgeToDisplay(badgeName);
    };

    // 自動で閉じる（3秒後）
    setTimeout(() => {
        if (!modal.classList.contains('hidden')) {
            closeBtn.click();
        }
    }, 3000);
}

/**
 * バッジをバッジセクションに追加
 */
function addBadgeToDisplay(badgeName) {
    const container = document.getElementById('badgesContainer');

    // "まだバッジがありません"を削除
    const noBadges = container.querySelector('.no-badges');
    if (noBadges) {
        noBadges.remove();
    }

    // バッジアイテムを作成
    const badgeItem = document.createElement('div');
    badgeItem.className = 'badge-item';

    const icon = document.createElement('span');
    icon.className = 'badge-icon';
    icon.textContent = BADGE_ICONS[badgeName] || '🏆';

    const name = document.createElement('p');
    name.className = 'badge-name';
    name.textContent = badgeName;

    badgeItem.appendChild(icon);
    badgeItem.appendChild(name);
    container.appendChild(badgeItem);

    // バッジ数を更新
    updateBadgeCount();
}

/**
 * バッジ数を更新
 */
function updateBadgeCount() {
    const container = document.getElementById('badgesContainer');
    const badges = container.querySelectorAll('.badge-item');
    const badgeCount = document.getElementById('badgeCount');
    badgeCount.textContent = `(${badges.length})`;
}

/**
 * リアクション演出をトリガー
 */
function triggerReaction(reactionTier) {
    const chatContainer = document.getElementById('chatContainer');

    if (reactionTier === 'small') {
        // 小さなパーティクル
        createParticle(chatContainer, '✨', 1);
    } else if (reactionTier === 'medium') {
        // 中規模パーティクル
        createParticle(chatContainer, '⭐', 3);
    } else if (reactionTier === 'large') {
        // 大規模パーティクル
        createParticle(chatContainer, '🌟', 5);
        // フラッシュ効果
        flashEffect();
    }
}

/**
 * パーティクルを作成
 */
function createParticle(container, emoji, count) {
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.className = 'reaction-particle';
        particle.textContent = emoji;
        particle.style.left = `${Math.random() * 80 + 10}%`;
        particle.style.top = `${Math.random() * 50 + 25}%`;

        container.appendChild(particle);

        // 1秒後に削除
        setTimeout(() => {
            particle.remove();
        }, 1000);
    }
}

/**
 * フラッシュ効果
 */
function flashEffect() {
    const body = document.body;
    const flash = document.createElement('div');
    flash.style.position = 'fixed';
    flash.style.top = '0';
    flash.style.left = '0';
    flash.style.width = '100%';
    flash.style.height = '100%';
    flash.style.background = 'rgba(255, 255, 255, 0.7)';
    flash.style.pointerEvents = 'none';
    flash.style.zIndex = '9999';
    flash.style.animation = 'flash 0.3s ease';

    body.appendChild(flash);

    setTimeout(() => {
        flash.remove();
    }, 300);
}
