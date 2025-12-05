/**
 * 人間形成ビジュアル: 5段階の成長表示
 */

const STAGE_DESCRIPTIONS = {
    1: "輪郭のみ",
    2: "顔・体の輪郭",
    3: "服装・基本",
    4: "表情・アクセサリー",
    5: "目に光・オーラ"
};

const STAGE_THRESHOLDS = {
    1: 0,
    2: 10,
    3: 25,
    4: 50,
    5: 100
};

/**
 * 人間形成ビジュアルを更新
 */
function updateHumanFormation(stage, dataCount) {
    const stagePlaceholder = document.getElementById('stagePlaceholder');
    const stageInfo = document.getElementById('stageInfo');

    // 既存のサークルを削除
    stagePlaceholder.innerHTML = '';

    // 新しいサークルを作成
    const circle = document.createElement('div');
    circle.className = `stage-circle stage-${stage}`;
    stagePlaceholder.appendChild(circle);

    // ステージ情報を更新
    const description = STAGE_DESCRIPTIONS[stage] || "不明";
    stageInfo.textContent = `Stage ${stage}: ${description} (${dataCount}件)`;

    // アニメーション効果
    circle.style.animation = 'none';
    setTimeout(() => {
        circle.style.animation = 'badgePop 0.5s ease';
    }, 10);
}
