import os
import sys
import csv
import json
import socket
from datetime import datetime
from pathlib import Path
import webbrowser
import http.server
import socketserver

# ----------------------------------------------------------------------
# Game HTML, CSS & JavaScript
# ----------------------------------------------------------------------
HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Math Quest: HCF & LCM Explorer</title>
    <style>
        :root {
            --primary: #4f46e5;
            --primary-light: #818cf8;
            --accent: #f59e0b;
            --success: #10b981;
            --danger: #ef4444;
            --bg-grad: linear-gradient(135deg, #4338ca 0%, #7e22ce 100%);
            --card-bg: rgba(255, 255, 255, 0.96);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            user-select: none;
        }

        body {
            min-height: 100vh;
            background: var(--bg-grad);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }

        .game-card {
            background: var(--card-bg);
            border-radius: 28px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 660px;
            padding: 24px;
            position: relative;
            overflow: hidden;
            text-align: center;
        }

        /* Top HUD */
        .hud {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            font-weight: 700;
            gap: 6px;
            flex-wrap: wrap;
        }
        .hud-left {
            display: flex;
            gap: 8px;
        }
        .pill {
            background: #e0e7ff;
            color: #3730a3;
            padding: 7px 14px;
            border-radius: 50px;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .streak-pill {
            background: #fef3c7;
            color: #b45309;
        }
        .finish-btn {
            background: #0f172a;
            color: white;
            border: none;
            padding: 7px 16px;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }
        .finish-btn:hover {
            background: #334155;
            transform: translateY(-1px);
        }

        /* Controls Section */
        .controls-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 12px;
        }
        @media (max-width: 520px) {
            .controls-grid { grid-template-columns: 1fr; }
        }
        .control-group { text-align: left; }
        .control-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            font-weight: 800;
            color: #64748b;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
            display: block;
        }
        .segmented-control {
            display: flex;
            gap: 4px;
            background: #f1f5f9;
            padding: 4px;
            border-radius: 12px;
        }
        .control-btn {
            flex: 1;
            padding: 7px 4px;
            border: none;
            border-radius: 8px;
            background: transparent;
            font-weight: 700;
            color: #64748b;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.8rem;
            white-space: nowrap;
        }
        .control-btn.active {
            background: white;
            color: var(--primary);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        }

        /* Question Box */
        .question-box {
            background: #f8fafc;
            border: 2px dashed #cbd5e1;
            border-radius: 20px;
            padding: 18px;
            margin-bottom: 16px;
        }
        .badge {
            display: inline-block;
            background: #4f46e5;
            color: white;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            text-transform: uppercase;
            font-weight: 800;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        .question-title {
            font-size: 1.1rem;
            color: #334155;
            margin-bottom: 6px;
            font-weight: 600;
        }
        .numbers-display {
            font-size: clamp(2rem, 5.5vw, 2.7rem);
            font-weight: 900;
            color: #1e1b4b;
            letter-spacing: 1px;
            line-height: 1.2;
        }

        /* Multiple Choice */
        .choices-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 14px;
        }
        .choice-btn {
            background: white;
            border: 3px solid #e2e8f0;
            padding: 16px;
            border-radius: 16px;
            font-size: 1.55rem;
            font-weight: 800;
            color: #1e293b;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
            transition: transform 0.1s, border-color 0.2s, background 0.2s;
        }
        .choice-btn:hover {
            transform: translateY(-2px);
            border-color: var(--primary-light);
        }
        .choice-btn.correct {
            background: #dcfce7 !important;
            border-color: var(--success) !important;
            color: #15803d !important;
        }
        .choice-btn.wrong {
            background: #fee2e2 !important;
            border-color: var(--danger) !important;
            color: #b91c1c !important;
        }

        /* Direct Input */
        .input-container {
            display: flex;
            gap: 10px;
            justify-content: center;
            align-items: center;
            margin-bottom: 14px;
        }
        .answer-input {
            width: 160px;
            height: 60px;
            font-size: 1.9rem;
            font-weight: 900;
            text-align: center;
            border: 3px solid #cbd5e1;
            border-radius: 18px;
            outline: none;
            color: #1e293b;
            background: #fff;
            user-select: text;
        }
        .answer-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.15);
        }
        .answer-input.correct {
            border-color: var(--success);
            background: #dcfce7;
            color: #15803d;
        }
        .answer-input.wrong {
            border-color: var(--danger);
            background: #fee2e2;
            color: #b91c1c;
        }
        .submit-btn {
            height: 60px;
            padding: 0 24px;
            border: none;
            border-radius: 18px;
            background: var(--primary);
            color: white;
            font-size: 1.15rem;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .submit-btn:hover { background: #4338ca; }

        /* Hint & Feedback */
        .hint-btn {
            background: none;
            border: none;
            color: #6366f1;
            font-weight: 700;
            cursor: pointer;
            text-decoration: underline;
            font-size: 0.95rem;
            margin-bottom: 10px;
            display: inline-block;
        }
        .hint-box {
            display: none;
            text-align: left;
            background: #fffbeb;
            border: 1px solid #fef3c7;
            border-radius: 14px;
            padding: 12px 16px;
            margin-bottom: 14px;
            font-size: 0.9rem;
            color: #92400e;
            line-height: 1.5;
        }
        .hint-box p { margin-bottom: 5px; }
        .highlight-ans {
            background: #fde68a;
            padding: 1px 6px;
            border-radius: 4px;
            font-weight: 800;
        }

        .feedback {
            font-size: 1.1rem;
            font-weight: 700;
            min-height: 28px;
            margin-bottom: 8px;
            color: #475569;
        }

        .next-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 12px 28px;
            font-size: 1.05rem;
            font-weight: 800;
            border-radius: 14px;
            cursor: pointer;
            display: none;
            margin: 0 auto;
            box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35);
        }
        .next-btn:hover { background: #4338ca; }

        /* Report Modal */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(4px);
            z-index: 100;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }
        .modal-card {
            background: white;
            border-radius: 24px;
            max-width: 500px;
            width: 100%;
            padding: 28px;
            text-align: center;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
            animation: popIn 0.3s ease;
        }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin: 20px 0;
        }
        .stat-box {
            background: #f8fafc;
            padding: 12px;
            border-radius: 14px;
            border: 1px solid #e2e8f0;
        }
        .stat-val {
            font-size: 1.6rem;
            font-weight: 900;
            color: #1e1b4b;
        }
        .stat-lbl {
            font-size: 0.75rem;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
        }
        .modal-badge {
            display: inline-block;
            background: #fef3c7;
            color: #92400e;
            padding: 6px 18px;
            border-radius: 50px;
            font-weight: 800;
            font-size: 1.1rem;
            margin-bottom: 10px;
        }
        .status-msg {
            font-size: 0.9rem;
            color: #059669;
            font-weight: 700;
            margin: 12px 0;
            padding: 8px;
            background: #ecfdf5;
            border-radius: 10px;
        }
        .modal-actions {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
        .btn-modal {
            padding: 10px 20px;
            border-radius: 12px;
            font-weight: 700;
            cursor: pointer;
            border: none;
            font-size: 0.95rem;
        }
        .btn-modal-primary {
            background: var(--primary);
            color: white;
        }
        .btn-modal-secondary {
            background: #e2e8f0;
            color: #334155;
        }

        #confetti-canvas {
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 10;
        }

        @keyframes popIn {
            from { transform: scale(0.9); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="game-card">
        <canvas id="confetti-canvas"></canvas>

        <!-- Top HUD -->
        <div class="hud">
            <div class="hud-left">
                <div class="pill">⭐ Score: <span id="score">0</span></div>
                <div class="pill streak-pill">🔥 Streak: <span id="streak">0</span></div>
            </div>
            <button class="finish-btn" onclick="openSessionSummary()">💾 Finish & Save</button>
        </div>

        <!-- Controls -->
        <div class="controls-grid">
            <div class="control-group">
                <span class="control-label">Skill Concept</span>
                <div class="segmented-control" id="concept-selector">
                    <button class="control-btn active" onclick="setControl('concept', 'hcf')">🛡️ HCF</button>
                    <button class="control-btn" onclick="setControl('concept', 'lcm')">🚀 LCM</button>
                    <button class="control-btn" onclick="setControl('concept', 'mixed')">⚡ Mixed</button>
                </div>
            </div>

            <div class="control-group">
                <span class="control-label">Answer Mode</span>
                <div class="segmented-control" id="mode-selector">
                    <button class="control-btn active" onclick="setControl('mode', 'choice')">🔘 Choices</button>
                    <button class="control-btn" onclick="setControl('mode', 'input')">✍️ Type In</button>
                </div>
            </div>
        </div>

        <div class="control-group" style="margin-bottom: 14px;">
            <span class="control-label">Number of Items</span>
            <div class="segmented-control" id="count-selector">
                <button class="control-btn active" onclick="setControl('count', 'random')">🎲 2 or 3 Numbers</button>
                <button class="control-btn" onclick="setControl('count', '2')">2 Numbers</button>
                <button class="control-btn" onclick="setControl('count', '3')">3 Numbers</button>
            </div>
        </div>

        <!-- Question Section -->
        <div class="question-box">
            <span class="badge" id="type-badge">HCF</span>
            <div class="question-title" id="question-text">Find the Highest Common Factor of:</div>
            <div class="numbers-display" id="numbers-display">--</div>
        </div>

        <!-- Multiple Choice Mode -->
        <div class="choices-grid" id="choices-grid"></div>

        <!-- Type-In Mode -->
        <div class="input-container" id="input-container" style="display: none;">
            <input type="number" id="answer-input" class="answer-input" placeholder="?" autocomplete="off" />
            <button class="submit-btn" id="submit-btn" onclick="submitTypedAnswer()">Check ➜</button>
        </div>

        <!-- Hint Section -->
        <button class="hint-btn" id="hint-toggle-btn" onclick="toggleHint()">💡 Need a hint? Show working</button>
        <div class="hint-box" id="hint-box"></div>

        <div class="feedback" id="feedback">Choose or type the correct answer!</div>
        <button class="next-btn" id="next-btn" onclick="generateQuestion()">Next Question ➜</button>
    </div>

    <!-- Session Completion Modal -->
    <div class="modal-overlay" id="summary-modal">
        <div class="modal-card">
            <div class="modal-badge" id="summary-badge">🌟 Great Job!</div>
            <h2 style="color: #1e1b4b; margin-bottom: 4px;">Session Report</h2>
            <p style="color: #64748b; font-size: 0.9rem;">Here is how you performed this session:</p>

            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-val" id="modal-score">0</div>
                    <div class="stat-lbl">Final Score</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val" id="modal-acc">0%</div>
                    <div class="stat-lbl">Accuracy</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val" id="modal-answered">0/0</div>
                    <div class="stat-lbl">Questions Right</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val" id="modal-streak">0</div>
                    <div class="stat-lbl">Best Streak</div>
                </div>
            </div>

            <div class="status-msg" id="save-status">💾 Saving log to your Desktop...</div>

            <div class="modal-actions">
                <button class="btn-modal btn-modal-primary" onclick="closeModalAndContinue()">Keep Playing</button>
                <button class="btn-modal btn-modal-secondary" onclick="resetSession()">Start Fresh Session</button>
            </div>
        </div>
    </div>

    <script>
        // Web Audio Synthesizer
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playTone(freq, type = 'sine', duration = 0.15) {
            if (audioCtx.state === 'suspended') audioCtx.resume();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        }

        function playCorrectSound() {
            playTone(523.25, 'triangle', 0.1);
            setTimeout(() => playTone(659.25, 'triangle', 0.1), 100);
            setTimeout(() => playTone(783.99, 'triangle', 0.22), 200);
        }

        function playWrongSound() {
            playTone(240, 'sawtooth', 0.18);
            setTimeout(() => playTone(180, 'sawtooth', 0.25), 140);
        }

        // Math Core Algorithms
        function gcd2(a, b) {
            while (b) { let t = b; b = a % b; a = t; }
            return a;
        }
        function gcdArray(arr) { return arr.reduce((acc, val) => gcd2(acc, val)); }
        function lcm2(a, b) { return (a * b) / gcd2(a, b); }
        function lcmArray(arr) { return arr.reduce((acc, val) => lcm2(acc, val)); }

        function getFactors(n) {
            let f = [];
            for (let i = 1; i <= n; i++) if (n % i === 0) f.push(i);
            return f;
        }

        function getMultiples(n, maxVal, minCount = 4) {
            let m = [], i = 1;
            while (n * i <= maxVal || i <= minCount) {
                m.push(n * i);
                i++;
                if (i > 12) break;
            }
            return m;
        }

        // State & Logging
        let conceptMode = 'hcf';
        let answerMode = 'choice';
        let countMode = 'random';
        let score = 0;
        let streak = 0;
        let bestStreak = 0;
        let answered = false;

        let currentNumbers = [];
        let currentType = 'hcf';
        let currentCorrectAnswer = 0;

        // Session Logger
        let sessionLogs = [];
        const sessionStartTime = new Date();

        function setControl(category, value) {
            if (category === 'concept') {
                conceptMode = value;
                document.querySelectorAll('#concept-selector .control-btn').forEach(b => b.classList.remove('active'));
            } else if (category === 'mode') {
                answerMode = value;
                document.querySelectorAll('#mode-selector .control-btn').forEach(b => b.classList.remove('active'));
            } else {
                countMode = value;
                document.querySelectorAll('#count-selector .control-btn').forEach(b => b.classList.remove('active'));
            }
            event.target.classList.add('active');
            generateQuestion();
        }

        // Procedural Generators (Numbers up to 100)
        function generateHCF(itemCount) {
            const commonG = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20];
            let g = commonG[Math.floor(Math.random() * commonG.length)];
            let maxMultiplier = Math.floor(100 / g);

            for (let attempt = 0; attempt < 100; attempt++) {
                let multipliers = new Set();
                while (multipliers.size < itemCount) {
                    let k = Math.floor(Math.random() * (maxMultiplier - 1)) + 2;
                    multipliers.add(k);
                }
                let kArr = Array.from(multipliers);
                if (gcdArray(kArr) === 1) {
                    let numbers = kArr.map(k => k * g).sort((a, b) => a - b);
                    if (Math.max(...numbers) <= 100) {
                        return { numbers, answer: g };
                    }
                }
            }
            return itemCount === 3 ? { numbers: [16, 24, 40], answer: 8 } : { numbers: [36, 48], answer: 12 };
        }

        function generateLCM(itemCount) {
            const candidateLCMs = [
                18, 24, 30, 36, 40, 48, 50, 60, 72, 80, 84, 90, 
                100, 120, 140, 150, 160, 180, 200, 210, 240
            ];
            const shuffled = [...candidateLCMs].sort(() => Math.random() - 0.5);
            for (let L of shuffled) {
                let divs = [];
                for (let d = 3; d <= Math.min(100, L); d++) {
                    if (L % d === 0) divs.push(d);
                }
                if (divs.length < itemCount) continue;

                for (let attempt = 0; attempt < 30; attempt++) {
                    let pick = new Set();
                    while (pick.size < itemCount) {
                        pick.add(divs[Math.floor(Math.random() * divs.length)]);
                    }
                    let pickArr = Array.from(pick).sort((a, b) => a - b);
                    if (lcmArray(pickArr) === L) {
                        return { numbers: pickArr, answer: L };
                    }
                }
            }
            return itemCount === 3 ? { numbers: [10, 15, 20], answer: 60 } : { numbers: [12, 16], answer: 48 };
        }

        function formatNumberList(arr) {
            if (arr.length === 2) return `${arr[0]} & ${arr[1]}`;
            return `${arr[0]}, ${arr[1]} & ${arr[2]}`;
        }

        function generateQuestion() {
            answered = false;
            document.getElementById('next-btn').style.display = 'none';
            document.getElementById('feedback').textContent = answerMode === 'choice' ? 'Choose the correct answer!' : 'Type your answer and press Check (or Enter)!';
            document.getElementById('feedback').style.color = '#475569';
            document.getElementById('hint-box').style.display = 'none';

            let type = conceptMode === 'mixed' ? (Math.random() > 0.5 ? 'hcf' : 'lcm') : conceptMode;
            let count = countMode === 'random' ? (Math.random() > 0.5 ? 3 : 2) : parseInt(countMode);

            let problem = type === 'hcf' ? generateHCF(count) : generateLCM(count);
            currentNumbers = problem.numbers;
            currentType = type;
            currentCorrectAnswer = problem.answer;

            if (type === 'hcf') {
                document.getElementById('type-badge').textContent = `🛡️ HCF (${count} Numbers)`;
                document.getElementById('type-badge').style.background = '#4f46e5';
                document.getElementById('question-text').textContent = 'Find the Highest Common Factor (HCF) of:';
            } else {
                document.getElementById('type-badge').textContent = `🚀 LCM (${count} Numbers)`;
                document.getElementById('type-badge').style.background = '#059669';
                document.getElementById('question-text').textContent = 'Find the Lowest Common Multiple (LCM) of:';
            }

            document.getElementById('numbers-display').textContent = formatNumberList(currentNumbers);

            const choicesGrid = document.getElementById('choices-grid');
            const inputContainer = document.getElementById('input-container');
            const answerInput = document.getElementById('answer-input');

            if (answerMode === 'choice') {
                choicesGrid.style.display = 'grid';
                inputContainer.style.display = 'none';

                const options = new Set([currentCorrectAnswer]);
                if (type === 'hcf') {
                    if (currentCorrectAnswer > 1) options.add(1);
                    if (currentCorrectAnswer > 2) options.add(Math.floor(currentCorrectAnswer / 2));
                    options.add(currentCorrectAnswer * 2);
                    options.add(Math.max(1, currentCorrectAnswer - 1));
                } else {
                    options.add(gcdArray(currentNumbers));
                    options.add(Math.max(...currentNumbers));
                    options.add(currentCorrectAnswer * 2);
                    if (currentCorrectAnswer % 2 === 0 && (currentCorrectAnswer / 2) >= Math.max(...currentNumbers)) {
                        options.add(currentCorrectAnswer / 2);
                    }
                }

                while (options.size < 4) {
                    let delta = (Math.floor(Math.random() * 4) + 1) * (type === 'hcf' ? 1 : 10);
                    let val = Math.max(1, currentCorrectAnswer + (Math.random() > 0.5 ? delta : -delta));
                    options.add(val);
                }

                const shuffled = Array.from(options).sort(() => Math.random() - 0.5);
                choicesGrid.innerHTML = '';
                shuffled.forEach(val => {
                    const btn = document.createElement('button');
                    btn.className = 'choice-btn';
                    btn.textContent = val;
                    btn.onclick = () => selectChoice(btn, val, currentCorrectAnswer);
                    choicesGrid.appendChild(btn);
                });
            } else {
                choicesGrid.style.display = 'none';
                inputContainer.style.display = 'flex';
                answerInput.value = '';
                answerInput.disabled = false;
                answerInput.className = 'answer-input';
                setTimeout(() => answerInput.focus(), 50);
            }

            prepareHint(type, currentNumbers, currentCorrectAnswer);
        }

        function prepareHint(type, numbers, answer) {
            const hintBox = document.getElementById('hint-box');
            let html = '';

            if (type === 'hcf') {
                let factorLists = numbers.map(n => getFactors(n));
                let common = factorLists[0].filter(factor => 
                    factorLists.every(list => list.includes(factor))
                );

                numbers.forEach((num, i) => {
                    html += `<p><strong>Factors of ${num}:</strong> ${factorLists[i].join(', ')}</p>`;
                });
                html += `<p style="margin-top: 6px;"><strong>Shared Factors:</strong> ${common.join(', ')}</p>`;
                html += `<p>👉 The <strong>highest</strong> common one is <span class="highlight-ans">${answer}</span>!</p>`;
            } else {
                numbers.forEach(num => {
                    let m = getMultiples(num, answer);
                    html += `<p><strong>Multiples of ${num}:</strong> ${m.join(', ')}${m.includes(answer) ? '' : '...'}</p>`;
                });
                html += `<p style="margin-top: 6px;">👉 The <strong>smallest</strong> common multiple is <span class="highlight-ans">${answer}</span>!</p>`;
            }
            hintBox.innerHTML = html;
        }

        function toggleHint() {
            const hintBox = document.getElementById('hint-box');
            hintBox.style.display = hintBox.style.display === 'block' ? 'none' : 'block';
        }

        function selectChoice(button, selected, correct) {
            if (answered) return;
            answered = true;

            const allButtons = document.querySelectorAll('.choice-btn');
            allButtons.forEach(btn => {
                if (parseInt(btn.textContent) === correct) btn.classList.add('correct');
            });

            handleResult(selected === correct, selected, correct, button);
        }

        function submitTypedAnswer() {
            if (answered) return;
            const input = document.getElementById('answer-input');
            const val = parseInt(input.value.trim());

            if (isNaN(val)) {
                input.focus();
                return;
            }

            answered = true;
            input.disabled = true;

            const isCorrect = (val === currentCorrectAnswer);
            if (isCorrect) input.classList.add('correct');
            else input.classList.add('wrong');

            handleResult(isCorrect, val, currentCorrectAnswer, null);
        }

        function handleResult(isCorrect, userAnswer, correctAnswer, element) {
            // Log entry for this question
            sessionLogs.push({
                qNum: sessionLogs.length + 1,
                time: new Date().toLocaleTimeString(),
                concept: currentType.toUpperCase(),
                numbers: currentNumbers.join(' & '),
                mode: answerMode === 'choice' ? 'Choice' : 'Input',
                userAnswer: userAnswer,
                correctAnswer: correctAnswer,
                isCorrect: isCorrect
            });

            if (isCorrect) {
                score += 10 + (streak * 2);
                streak += 1;
                if (streak > bestStreak) bestStreak = streak;
                if (element) element.classList.add('correct');
                document.getElementById('feedback').textContent = streak > 2 ? `🔥 Wow! ${streak} in a row!` : '✨ Correct! Excellent work!';
                document.getElementById('feedback').style.color = '#15803d';
                playCorrectSound();
                triggerConfetti();
            } else {
                streak = 0;
                if (element) element.classList.add('wrong');
                document.getElementById('feedback').textContent = `Not quite! The answer was ${correctAnswer}. Check the hint!`;
                document.getElementById('feedback').style.color = '#b91c1c';
                document.getElementById('hint-box').style.display = 'block';
                playWrongSound();
            }

            document.getElementById('score').textContent = score;
            document.getElementById('streak').textContent = streak;
            document.getElementById('next-btn').style.display = 'block';
        }

        // Session Summary & Desktop Saver
        async function openSessionSummary() {
            const modal = document.getElementById('summary-modal');
            const total = sessionLogs.length;
            const correctCount = sessionLogs.filter(q => q.isCorrect).length;
            const accuracy = total > 0 ? Math.round((correctCount / total) * 100) : 0;

            document.getElementById('modal-score').textContent = score;
            document.getElementById('modal-acc').textContent = `${accuracy}%`;
            document.getElementById('modal-answered').textContent = `${correctCount}/${total}`;
            document.getElementById('modal-streak').textContent = bestStreak;

            let badge = '🌱 Great Practice!';
            if (accuracy >= 90 && total >= 5) badge = '🌟 Math Superstar!';
            else if (accuracy >= 75 && total >= 3) badge = '🚀 Math Champ!';
            else if (accuracy >= 50) badge = '👍 Good Effort!';
            document.getElementById('summary-badge').textContent = badge;

            modal.style.display = 'flex';

            if (total === 0) {
                document.getElementById('save-status').textContent = 'Play a few questions first to record results!';
                return;
            }

            // Prepare payload
            const payload = {
                timestamp: new Date().toLocaleString(),
                totalQuestions: total,
                correctCount: correctCount,
                incorrectCount: total - correctCount,
                accuracy: accuracy,
                finalScore: score,
                bestStreak: bestStreak,
                badge: badge,
                questions: sessionLogs
            };

            const statusEl = document.getElementById('save-status');
            statusEl.textContent = '💾 Saving report to your Desktop...';
            statusEl.style.color = '#2563eb';

            try {
                // Post to Python server
                const resp = await fetch('/api/save_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const res = await resp.json();
                if (res.status === 'success') {
                    statusEl.textContent = `✅ Saved to Desktop: ${res.file}`;
                    statusEl.style.color = '#059669';
                } else {
                    fallbackClientDownload(payload);
                }
            } catch (err) {
                // Fallback client-side download if running offline / file://
                fallbackClientDownload(payload);
            }
        }

        function fallbackClientDownload(payload) {
            let csv = "=== MATH QUEST SESSION SUMMARY ===\n";
            csv += `Date & Time,${payload.timestamp}\n`;
            csv += `Total Questions,${payload.totalQuestions}\n`;
            csv += `Correct Answers,${payload.correctCount}\n`;
            csv += `Accuracy,${payload.accuracy}%\n`;
            csv += `Final Score,${payload.finalScore}\n`;
            csv += `Best Streak,${payload.bestStreak}\n\n`;
            csv += "=== QUESTION BREAKDOWN ===\n";
            csv += "#,Time,Concept,Numbers,Answer Mode,Child Answer,Correct Answer,Result\n";
            payload.questions.forEach(q => {
                csv += `${q.qNum},${q.time},${q.concept},"${q.numbers}",${q.mode},${q.userAnswer},${q.correctAnswer},${q.isCorrect ? 'CORRECT' : 'WRONG'}\n`;
            });

            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = `Math_Quest_Session_${new Date().toISOString().slice(0,10)}.csv`;
            link.click();

            const statusEl = document.getElementById('save-status');
            statusEl.textContent = '✅ Downloaded CSV Report to your computer!';
            statusEl.style.color = '#059669';
        }

        function closeModalAndContinue() {
            document.getElementById('summary-modal').style.display = 'none';
        }

        function resetSession() {
            score = 0;
            streak = 0;
            bestStreak = 0;
            sessionLogs = [];
            document.getElementById('score').textContent = '0';
            document.getElementById('streak').textContent = '0';
            document.getElementById('summary-modal').style.display = 'none';
            generateQuestion();
        }

        // Enter Key Listener
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const modal = document.getElementById('summary-modal');
                if (modal.style.display === 'flex') return;

                if (!answered) {
                    if (answerMode === 'input') submitTypedAnswer();
                } else {
                    generateQuestion();
                }
            }
        });

        // Confetti
        function triggerConfetti() {
            const canvas = document.getElementById('confetti-canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            const particles = [];
            const colors = ['#f59e0b', '#10b981', '#6366f1', '#ec4899', '#3b82f6'];

            for (let i = 0; i < 45; i++) {
                particles.push({
                    x: canvas.width / 2,
                    y: canvas.height / 2,
                    vx: (Math.random() - 0.5) * 11,
                    vy: (Math.random() - 0.8) * 11,
                    size: Math.random() * 6 + 4,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    life: 45
                });
            }

            function frame() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                let alive = false;
                particles.forEach(p => {
                    p.x += p.vx;
                    p.y += p.vy;
                    p.vy += 0.35;
                    p.life--;
                    if (p.life > 0) {
                        alive = true;
                        ctx.fillStyle = p.color;
                        ctx.fillRect(p.x, p.y, p.size, p.size);
                    }
                });
                if (alive) requestAnimationFrame(frame);
                else ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
            requestAnimationFrame(frame);
        }

        // Start initial question
        generateQuestion();
    </script>
</body>
</html>
"""

# ----------------------------------------------------------------------
# Local Desktop Saver Function
# ----------------------------------------------------------------------
def save_report_to_desktop(data):
    # Locate Desktop across Windows, macOS, Linux
    desktop_dir = Path.home() / "Desktop"
    if not desktop_dir.exists():
        desktop_dir = Path.home()

    now_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"Math_Quest_Session_{now_str}.csv"
    filepath = desktop_dir / filename

    # Write formatted CSV report (utf-8-sig ensures clean display in Excel)
    with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        
        # Summary Header
        writer.writerow(["=== MATH QUEST: SESSION SUMMARY ==="])
        writer.writerow(["Session Date & Time", data.get("timestamp")])
        writer.writerow(["Performance Level", data.get("badge")])
        writer.writerow(["Total Questions Answered", data.get("totalQuestions")])
        writer.writerow(["Correct Answers", data.get("correctCount")])
        writer.writerow(["Incorrect Answers", data.get("incorrectCount")])
        writer.writerow(["Accuracy Rate", f"{data.get('accuracy')}%"])
        writer.writerow(["Final Score Points", data.get("finalScore")])
        writer.writerow(["Highest Streak", data.get("bestStreak")])
        writer.writerow([])
        
        # Detailed Question Breakdown
        writer.writerow(["=== DETAILED QUESTION BREAKDOWN ==="])
        writer.writerow([
            "Question #", 
            "Time", 
            "Concept", 
            "Numbers Given", 
            "Input Mode", 
            "Kid's Answer", 
            "Correct Answer", 
            "Result"
        ])
        
        for q in data.get("questions", []):
            writer.writerow([
                q.get("qNum"),
                q.get("time"),
                q.get("concept"),
                q.get("numbers"),
                q.get("mode"),
                q.get("userAnswer"),
                q.get("correctAnswer"),
                "CORRECT" if q.get("isCorrect") else "WRONG"
            ])
            
    print(f"📊 [Saved] New session report created: {filepath}")
    return filename

# ----------------------------------------------------------------------
# Python Local HTTP Server Handler
# ----------------------------------------------------------------------
class MathGameRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/save_session":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))

            saved_filename = save_report_to_desktop(data)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = json.dumps({"status": "success", "file": saved_filename})
            self.wfile.write(resp.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence routine access log messages to keep terminal clean
        return

def find_available_port(start_port=8080):
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return 8080

def main():
    port = find_available_port()
    server_address = ("127.0.0.1", port)
    
    desktop_path = Path.home() / "Desktop"
    
    print("=" * 60)
    print("🎉 MATH QUEST: HCF & LCM LEARNING TRACKER")
    print(f"🌐 Local Server running at: http://localhost:{port}")
    print(f"📁 Session reports will automatically save to:")
    print(f"   {desktop_path}")
    print("=" * 60)
    print("👉 Keep this terminal window open while playing.")
    print("👉 Press Ctrl+C in this terminal when finished.")
    print("=" * 60)

    webbrowser.open(f"http://localhost:{port}")

    httpd = socketserver.TCPServer(server_address, MathGameRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server closed. Have a wonderful day!")
        httpd.server_close()

if __name__ == "__main__":
    main()
