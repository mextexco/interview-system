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

    // 既存の内容を削除
    stagePlaceholder.innerHTML = '';

    // SVG人型を作成
    const svg = createHumanSVG(stage);
    stagePlaceholder.appendChild(svg);

    // ステージ情報を更新
    const description = STAGE_DESCRIPTIONS[stage] || "不明";
    stageInfo.textContent = `Stage ${stage}: ${description} (${dataCount}件)`;

    // アニメーション効果
    svg.style.animation = 'humanGrow 0.8s ease';
}

/**
 * SVG人型を作成（ステージごとに詳細度が増す）
 */
function createHumanSVG(stage) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '200');
    svg.setAttribute('height', '300');
    svg.setAttribute('viewBox', '0 0 200 300');
    svg.classList.add('human-svg');

    const opacity = Math.min(stage * 0.2, 1);
    const baseColor = `rgba(100, 120, 200, ${opacity})`;

    // Stage 1: 基本輪郭のみ
    if (stage >= 1) {
        // 頭
        const head = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        head.setAttribute('cx', '100');
        head.setAttribute('cy', '60');
        head.setAttribute('r', '30');
        head.setAttribute('fill', 'none');
        head.setAttribute('stroke', baseColor);
        head.setAttribute('stroke-width', '3');
        svg.appendChild(head);

        // 体
        const body = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        body.setAttribute('x1', '100');
        body.setAttribute('y1', '90');
        body.setAttribute('x2', '100');
        body.setAttribute('y2', '180');
        body.setAttribute('stroke', baseColor);
        body.setAttribute('stroke-width', '3');
        svg.appendChild(body);
    }

    // Stage 2: 手足追加
    if (stage >= 2) {
        // 左腕
        const leftArm = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        leftArm.setAttribute('x1', '100');
        leftArm.setAttribute('y1', '110');
        leftArm.setAttribute('x2', '60');
        leftArm.setAttribute('y2', '150');
        leftArm.setAttribute('stroke', baseColor);
        leftArm.setAttribute('stroke-width', '3');
        svg.appendChild(leftArm);

        // 右腕
        const rightArm = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        rightArm.setAttribute('x1', '100');
        rightArm.setAttribute('y1', '110');
        rightArm.setAttribute('x2', '140');
        rightArm.setAttribute('y2', '150');
        rightArm.setAttribute('stroke', baseColor);
        rightArm.setAttribute('stroke-width', '3');
        svg.appendChild(rightArm);

        // 左足
        const leftLeg = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        leftLeg.setAttribute('x1', '100');
        leftLeg.setAttribute('y1', '180');
        leftLeg.setAttribute('x2', '70');
        leftLeg.setAttribute('y2', '260');
        leftLeg.setAttribute('stroke', baseColor);
        leftLeg.setAttribute('stroke-width', '3');
        svg.appendChild(leftLeg);

        // 右足
        const rightLeg = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        rightLeg.setAttribute('x1', '100');
        rightLeg.setAttribute('y1', '180');
        rightLeg.setAttribute('x2', '130');
        rightLeg.setAttribute('y2', '260');
        rightLeg.setAttribute('stroke', baseColor);
        rightLeg.setAttribute('stroke-width', '3');
        svg.appendChild(rightLeg);
    }

    // Stage 3: 服装（体を塗りつぶし）
    if (stage >= 3) {
        const bodyRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        bodyRect.setAttribute('x', '80');
        bodyRect.setAttribute('y', '90');
        bodyRect.setAttribute('width', '40');
        bodyRect.setAttribute('height', '90');
        bodyRect.setAttribute('fill', `rgba(150, 170, 220, ${opacity})`);
        bodyRect.setAttribute('rx', '5');
        svg.insertBefore(bodyRect, svg.firstChild);
    }

    // Stage 4: 顔（目・口）
    if (stage >= 4) {
        // 左目
        const leftEye = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        leftEye.setAttribute('cx', '90');
        leftEye.setAttribute('cy', '55');
        leftEye.setAttribute('r', '4');
        leftEye.setAttribute('fill', baseColor);
        svg.appendChild(leftEye);

        // 右目
        const rightEye = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        rightEye.setAttribute('cx', '110');
        rightEye.setAttribute('cy', '55');
        rightEye.setAttribute('r', '4');
        rightEye.setAttribute('fill', baseColor);
        svg.appendChild(rightEye);

        // 口
        const mouth = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        mouth.setAttribute('d', 'M 90 70 Q 100 75 110 70');
        mouth.setAttribute('fill', 'none');
        mouth.setAttribute('stroke', baseColor);
        mouth.setAttribute('stroke-width', '2');
        svg.appendChild(mouth);
    }

    // Stage 5: オーラ（光）
    if (stage >= 5) {
        const aura = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        aura.setAttribute('cx', '100');
        aura.setAttribute('cy', '150');
        aura.setAttribute('r', '120');
        aura.setAttribute('fill', 'none');
        aura.setAttribute('stroke', 'rgba(255, 215, 0, 0.6)');
        aura.setAttribute('stroke-width', '8');
        aura.classList.add('aura-glow');
        svg.insertBefore(aura, svg.firstChild);
    }

    return svg;
}
