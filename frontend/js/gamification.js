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
    // バッジ名が空、未定義、または無効な場合は表示しない
    if (!badgeName || typeof badgeName !== 'string' || badgeName.trim() === '') {
        console.warn('[Badge] Invalid badge name, skipping modal:', badgeName);
        return;
    }

    // バッジが定義されているかチェック
    if (!BADGE_ICONS[badgeName]) {
        console.warn('[Badge] Unknown badge, skipping:', badgeName);
        return;
    }

    const modal = document.getElementById('badgeModal');
    const badgeIcon = document.getElementById('newBadgeIcon');
    const badgeNameElem = document.getElementById('newBadgeName');

    // 要素が存在しない場合は中止
    if (!modal || !badgeIcon || !badgeNameElem) {
        console.error('[Badge] Badge modal elements not found');
        return;
    }

    badgeIcon.textContent = BADGE_ICONS[badgeName];
    badgeNameElem.textContent = badgeName;

    // モーダルを表示
    modal.classList.remove('hidden');
    modal.style.display = 'flex';

    // 閉じるボタンのイベントリスナーを削除してから再設定（重複防止）
    const closeBtn = document.getElementById('closeBadgeBtn');
    const newCloseBtn = closeBtn.cloneNode(true);
    closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);

    newCloseBtn.onclick = () => {
        modal.classList.add('hidden');
        modal.style.display = 'none';
        // バッジをバッジセクションに追加
        addBadgeToDisplay(badgeName);
    };

    // 自動で閉じる（3秒後）
    setTimeout(() => {
        if (!modal.classList.contains('hidden')) {
            newCloseBtn.click();
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

/**
 * バッジモーダル初期化（ページ読み込み時に確実に非表示）
 */
function initializeBadgeModal() {
    const modal = document.getElementById('badgeModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
    }
}

// ページ読み込み時に初期化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeBadgeModal);
} else {
    initializeBadgeModal();
}
