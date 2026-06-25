// ═══════════════════════════════════════════════════════════════
// SignTalk Pro — Web App Logic (Full Feature Build)
// ═══════════════════════════════════════════════════════════════

let state = {
    mode: "ISL",
    speed: 1.0,
    signs: [],
    currentIndex: 0,
    isPlaying: false,
    playTimer: null,
    history: [],
    favorites: [],
    currentText: "",
    user: null,              // null = guest
    quiz: {
        questions: [],
        currentIndex: 0,
        score: 0,
        total: 10,
        answered: false
    },
    achievements: [],
    settings: null
};

// ── DOM refs ──────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

const textInput = $("text-input");
const btnTranslate = $("btn-translate");
const btnClearText = $("btn-clear-text");
const btnStop = $("btn-stop");
const btnFavorite = $("btn-favorite");
const btnMic = $("btn-mic");
const micStatus = $("mic-status");
const btnGif = $("btn-gif");
const gifStatus = $("gif-status");
const speedSlider = $("speed-slider");
const speedValue = $("speed-value");
const signDisplay = $("sign-display");
const signPlaceholder = $("sign-placeholder");
const signImage = $("sign-image");
const signLetter = $("sign-letter");
const progressRow = $("progress-row");
const progressFill = $("progress-fill");
const progressCaption = $("progress-caption");
const statusIndicator = $("status-indicator");
const statCount = $("stat-count");
const goalCount = $("goal-count");
const goalFill = $("goal-fill");

// ═══════════════════════════════════════════════════════════════
// AUTH
// ═══════════════════════════════════════════════════════════════

const authShell = $("auth-shell");
const appShell = $("app-shell");

async function checkSession() {
    try {
        const res = await fetch("/api/me");
        const data = await res.json();
        if (data.user) {
            state.user = data.user;
            enterApp();
        } else {
            showAuthScreen();
        }
    } catch (err) {
        showAuthScreen();
    }
}

function showAuthScreen() {
    authShell.style.display = "flex";
    appShell.style.display = "none";
}

async function enterApp() {
    authShell.style.display = "none";
    appShell.style.display = "flex";

    if (state.user) {
        $("sidebar-username").textContent = state.user.username;
        $("sidebar-avatar").textContent = state.user.username[0].toUpperCase();
        await Promise.all([loadHistory(), loadFavorites(), loadSettings(), loadAchievementsCount()]);
    } else {
        $("sidebar-username").textContent = "Guest User";
        $("sidebar-avatar").textContent = "G";
        renderHistory();
        renderFavorites();
        updateStats();
    }
}

// Auth tab switching
$("auth-tab-login").addEventListener("click", () => switchAuthTab("login"));
$("auth-tab-register").addEventListener("click", () => switchAuthTab("register"));

function switchAuthTab(which) {
    document.querySelectorAll(".auth-tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".auth-form").forEach(f => f.classList.remove("active"));
    $(`auth-tab-${which}`).classList.add("active");
    $(`form-${which}`).classList.add("active");
}

$("form-login").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = $("login-username").value.trim();
    const password = $("login-password").value;
    const errEl = $("login-error");
    errEl.textContent = "";

    try {
        const res = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (!res.ok) {
            errEl.textContent = data.error || "Login failed";
            return;
        }
        state.user = data.user;
        await enterApp();
    } catch (err) {
        errEl.textContent = "Could not reach server";
    }
});

$("form-register").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = $("register-username").value.trim();
    const password = $("register-password").value;
    const errEl = $("register-error");
    errEl.textContent = "";

    try {
        const res = await fetch("/api/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (!res.ok) {
            errEl.textContent = data.error || "Registration failed";
            return;
        }
        state.user = data.user;
        await enterApp();
    } catch (err) {
        errEl.textContent = "Could not reach server";
    }
});

$("btn-guest").addEventListener("click", () => {
    state.user = null;
    enterApp();
});

$("btn-logout").addEventListener("click", async () => {
    if (state.user) {
        await fetch("/api/logout", { method: "POST" });
    }
    state.user = null;
    state.history = [];
    state.favorites = [];
    location.reload();
});

checkSession();

// ── Tab navigation ───────────────────────────────────────────────
document.querySelectorAll(".nav-item").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
        btn.classList.add("active");
        $(`tab-${btn.dataset.tab}`).classList.add("active");

        if (btn.dataset.tab === "achievements") loadAchievements();
        if (btn.dataset.tab === "profile") loadProfile();
        if (btn.dataset.tab === "settings") loadSettings();
    });
});

// ── Mode switch (ISL/ASL) ────────────────────────────────────────
$("btn-isl").addEventListener("click", () => setMode("ISL"));
$("btn-asl").addEventListener("click", () => setMode("ASL"));

function setMode(mode) {
    state.mode = mode;
    $("btn-isl").classList.toggle("active", mode === "ISL");
    $("btn-asl").classList.toggle("active", mode === "ASL");
}

// ── Theme color dots ─────────────────────────────────────────────
document.querySelectorAll(".dot").forEach(dot => {
    dot.addEventListener("click", () => {
        document.querySelectorAll(".dot").forEach(d => d.classList.remove("active"));
        dot.classList.add("active");
        const color = dot.dataset.color;
        document.documentElement.style.setProperty("--primary", color);
    });
});

// ── Speed slider ─────────────────────────────────────────────────
speedSlider.addEventListener("input", () => {
    state.speed = parseFloat(speedSlider.value);
    speedValue.textContent = state.speed.toFixed(1) + "s";
});

// ── Clear text ───────────────────────────────────────────────────
btnClearText.addEventListener("click", () => {
    textInput.value = "";
});

// ═══════════════════════════════════════════════════════════════
// VOICE INPUT (Web Speech API)
// ═══════════════════════════════════════════════════════════════

const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognizer = null;
let isListening = false;

if (SpeechRecognitionAPI) {
    recognizer = new SpeechRecognitionAPI();
    recognizer.continuous = false;
    recognizer.interimResults = true;
    recognizer.lang = "en-US";

    recognizer.onstart = () => {
        isListening = true;
        btnMic.classList.add("listening");
        micStatus.textContent = "🎙️ Listening... speak now";
    };

    recognizer.onresult = (event) => {
        let transcript = "";
        for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        textInput.value = transcript;
    };

    recognizer.onerror = (event) => {
        micStatus.textContent = "⚠️ Mic error: " + event.error;
        stopListening();
    };

    recognizer.onend = () => {
        stopListening();
        if (textInput.value.trim()) {
            micStatus.textContent = "✅ Heard: \"" + textInput.value.trim() + "\"";
        }
    };
} else {
    btnMic.disabled = true;
    btnMic.title = "Voice input not supported in this browser";
}

function stopListening() {
    isListening = false;
    btnMic.classList.remove("listening");
}

btnMic.addEventListener("click", () => {
    if (!recognizer) return;
    if (isListening) {
        recognizer.stop();
    } else {
        micStatus.textContent = "";
        try {
            recognizer.start();
        } catch (err) {
            micStatus.textContent = "⚠️ Could not start microphone";
        }
    }
});

// ═══════════════════════════════════════════════════════════════
// TRANSLATE
// ═══════════════════════════════════════════════════════════════

btnTranslate.addEventListener("click", async () => {
    const text = textInput.value.trim();
    if (!text) return;

    stopPlayback();

    statusIndicator.textContent = "● Loading...";
    statusIndicator.style.color = "var(--warning)";

    try {
        const res = await fetch("/api/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, mode: state.mode })
        });
        const data = await res.json();

        state.signs = data.signs;
        state.currentText = text;
        state.currentIndex = 0;

        if (state.user) {
            await loadHistory();
            announceAchievements(data.new_achievements);
        } else {
            addToHistoryLocal(text, state.mode);
        }
        updateStats();

        startPlayback();

    } catch (err) {
        statusIndicator.textContent = "● Error";
        statusIndicator.style.color = "var(--error)";
        console.error(err);
    }
});

// ── Playback logic ───────────────────────────────────────────────
function startPlayback() {
    state.isPlaying = true;
    statusIndicator.textContent = "● Playing";
    statusIndicator.style.color = "var(--success)";
    progressRow.style.display = "block";
    showSign(0);
}

function showSign(index) {
    if (index >= state.signs.length) {
        state.isPlaying = false;
        statusIndicator.textContent = "● Done";
        statusIndicator.style.color = "var(--success)";
        playDoneSound();
        return;
    }

    state.currentIndex = index;
    const sign = state.signs[index];

    signPlaceholder.style.display = "none";

    if (sign.is_space) {
        signImage.style.display = "none";
        signLetter.textContent = "⎵ (space)";
    } else if (sign.image) {
        signImage.src = sign.image;
        signImage.style.display = "block";
        signLetter.textContent = sign.char;
    } else {
        signImage.style.display = "none";
        signLetter.textContent = sign.char + " (no image)";
    }

    const pct = ((index + 1) / state.signs.length) * 100;
    progressFill.style.width = pct + "%";
    progressCaption.textContent = `Letter ${index + 1} of ${state.signs.length} — "${state.currentText}"`;

    if (state.isPlaying) {
        state.playTimer = setTimeout(() => {
            showSign(index + 1);
        }, state.speed * 1000);
    }
}

function stopPlayback() {
    state.isPlaying = false;
    if (state.playTimer) {
        clearTimeout(state.playTimer);
        state.playTimer = null;
    }
}

btnStop.addEventListener("click", () => {
    stopPlayback();
    statusIndicator.textContent = "● Stopped";
    statusIndicator.style.color = "var(--text-muted)";
});

// ═══════════════════════════════════════════════════════════════
// GIF EXPORT
// ═══════════════════════════════════════════════════════════════

btnGif.addEventListener("click", async () => {
    if (!state.signs.length) {
        gifStatus.textContent = "Translate something first!";
        return;
    }

    const imageSigns = state.signs.filter(s => !s.is_space && s.image);
    if (!imageSigns.length) {
        gifStatus.textContent = "No sign images available to export.";
        return;
    }

    btnGif.classList.add("exporting");
    gifStatus.textContent = "⏳ Building GIF (0%)...";

    try {
        const gif = new GIF({
            workers: 2,
            quality: 10,
            width: 280,
            height: 220,
            workerScript: "/static/gif.worker.js"
        });

        const delayMs = Math.max(state.speed * 1000, 300);

        for (const sign of imageSigns) {
            const img = await loadImageEl(sign.image);
            const canvas = document.createElement("canvas");
            canvas.width = 280;
            canvas.height = 220;
            const ctx = canvas.getContext("2d");
            ctx.fillStyle = "#0d1117";
            ctx.fillRect(0, 0, 280, 220);
            const scale = Math.min(280 / img.width, 200 / img.height);
            const w = img.width * scale;
            const h = img.height * scale;
            ctx.drawImage(img, (280 - w) / 2, (220 - h) / 2 - 10, w, h);
            ctx.fillStyle = "#3b82f6";
            ctx.font = "bold 18px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(sign.char, 140, 205);
            gif.addFrame(canvas, { delay: delayMs });
        }

        gif.on("progress", (p) => {
            gifStatus.textContent = `⏳ Building GIF (${Math.round(p * 100)}%)...`;
        });

        gif.on("finished", (blob) => {
            const url = URL.createObjectURL(blob);
            const filename = `signtalk_${state.currentText.replace(/\s+/g, "_").slice(0, 20)}.gif`;
            gifStatus.innerHTML = `✅ <a href="${url}" download="${filename}">Download GIF</a>`;
            btnGif.classList.remove("exporting");
        });

        gif.render();
    } catch (err) {
        gifStatus.textContent = "⚠️ GIF export failed.";
        btnGif.classList.remove("exporting");
        console.error(err);
    }
});

function loadImageEl(src) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = src;
    });
}

// ═══════════════════════════════════════════════════════════════
// FAVORITES (API-backed when logged in, local for guests)
// ═══════════════════════════════════════════════════════════════

btnFavorite.addEventListener("click", async () => {
    if (!state.currentText) return;

    if (state.user) {
        try {
            const res = await fetch("/api/favorites", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: state.currentText, mode: state.mode })
            });
            const data = await res.json();
            state.favorites = data.favorites;
            renderFavorites();
            announceAchievements(data.new_achievements);
        } catch (err) {
            console.error(err);
        }
    } else {
        const exists = state.favorites.some(
            f => f.text === state.currentText && f.mode === state.mode
        );
        if (!exists) {
            state.favorites.unshift({ text: state.currentText, mode: state.mode, id: Date.now() });
            renderFavorites();
        }
    }
});

async function loadFavorites() {
    try {
        const res = await fetch("/api/favorites");
        const data = await res.json();
        state.favorites = data.favorites || [];
        renderFavorites();
    } catch (err) {
        console.error(err);
    }
}

function renderFavorites() {
    const container = $("favorites-list");
    if (state.favorites.length === 0) {
        container.innerHTML = '<div class="empty-state">No favorites saved yet.</div>';
        return;
    }

    container.innerHTML = state.favorites.map((fav) => `
        <div class="list-item">
            <span class="list-item-text">${escapeHtml(fav.text)}</span>
            <div class="list-item-meta">
                <span class="badge">${fav.mode === "ISL" ? "🇮🇳 ISL" : "🇺🇸 ASL"}</span>
                <div class="list-item-actions">
                    <button class="btn-small" onclick="loadFavorite('${fav.text.replace(/'/g, "\\'")}', '${fav.mode}')">🔄 Load</button>
                    ${state.user ? `<button class="btn-small" onclick="deleteFavorite(${fav.id})">🗑️</button>` : ""}
                </div>
            </div>
        </div>
    `).join("");
}

window.loadFavorite = function(text, mode) {
    setMode(mode);
    textInput.value = text;
    document.querySelector('.nav-item[data-tab="translator"]').click();
    btnTranslate.click();
};

window.deleteFavorite = async function(id) {
    try {
        const res = await fetch(`/api/favorites/${id}`, { method: "DELETE" });
        const data = await res.json();
        state.favorites = data.favorites;
        renderFavorites();
    } catch (err) {
        console.error(err);
    }
};

// ═══════════════════════════════════════════════════════════════
// HISTORY (API-backed when logged in, local for guests)
// ═══════════════════════════════════════════════════════════════

async function loadHistory() {
    try {
        const res = await fetch("/api/history");
        const data = await res.json();
        state.history = data.history || [];
        renderHistory();
        updateStats();
    } catch (err) {
        console.error(err);
    }
}

function addToHistoryLocal(text, mode) {
    const time = new Date().toLocaleString([], {
        month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
    });
    state.history.unshift({ text, mode, created_at: time });
    renderHistory();
}

function renderHistory() {
    const container = $("history-list");
    if (state.history.length === 0) {
        container.innerHTML = '<div class="empty-state">No translations yet — go try the Translator!</div>';
        return;
    }

    container.innerHTML = state.history.map(item => {
        const timeLabel = item.created_at && item.created_at.includes("T")
            ? new Date(item.created_at).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
            : item.created_at;
        return `
        <div class="list-item">
            <span class="list-item-text">${escapeHtml(item.text)}</span>
            <div class="list-item-meta">
                <span class="badge">${item.mode === "ISL" ? "🇮🇳 ISL" : "🇺🇸 ASL"}</span>
                <span class="badge">${timeLabel}</span>
            </div>
        </div>
    `;
    }).join("");
}

$("btn-clear-history").addEventListener("click", async () => {
    if (state.user) {
        await fetch("/api/history", { method: "DELETE" });
    }
    state.history = [];
    renderHistory();
    updateStats();
});

// ── Stats / daily goal ───────────────────────────────────────────
function updateStats() {
    statCount.textContent = state.history.length;
    const completed = Math.min(state.history.length, 10);
    goalCount.textContent = `${completed}/10`;
    goalFill.style.width = `${(completed / 10) * 100}%`;
}

// ═══════════════════════════════════════════════════════════════
// QUIZ
// ═══════════════════════════════════════════════════════════════

$("quiz-btn-isl").addEventListener("click", () => setQuizMode("ISL"));
$("quiz-btn-asl").addEventListener("click", () => setQuizMode("ASL"));

function setQuizMode(mode) {
    state.mode = mode;
    $("quiz-btn-isl").classList.toggle("active", mode === "ISL");
    $("quiz-btn-asl").classList.toggle("active", mode === "ASL");
    $("btn-isl").classList.toggle("active", mode === "ISL");
    $("btn-asl").classList.toggle("active", mode === "ASL");
}

$("btn-quiz-start").addEventListener("click", startQuiz);
$("btn-quiz-again").addEventListener("click", startQuiz);

async function startQuiz() {
    state.quiz = { questions: [], currentIndex: 0, score: 0, total: 10, answered: false };

    $("quiz-start").style.display = "none";
    $("quiz-result").style.display = "none";
    $("quiz-active").style.display = "block";
    $("quiz-feedback").textContent = "";
    $("quiz-feedback").className = "quiz-feedback";

    await loadQuizQuestion();
}

async function loadQuizQuestion() {
    $("quiz-progress").textContent = `Question ${state.quiz.currentIndex + 1} of ${state.quiz.total}`;
    $("quiz-score").textContent = `Score: ${state.quiz.score}`;
    $("quiz-feedback").textContent = "";
    $("quiz-feedback").className = "quiz-feedback";
    state.quiz.answered = false;

    try {
        const res = await fetch(`/api/quiz/question?mode=${state.mode}`);
        const data = await res.json();

        if (!res.ok) {
            $("quiz-options").innerHTML = "";
            $("quiz-feedback").textContent = "⚠️ " + (data.error || "Could not load quiz question.");
            $("quiz-feedback").className = "quiz-feedback incorrect-text";
            return;
        }

        state.quiz.currentQuestion = data;
        $("quiz-image").src = data.image;

        const optionsContainer = $("quiz-options");
        optionsContainer.innerHTML = data.options.map(opt => `
            <button class="quiz-option-btn" data-letter="${opt}">${opt}</button>
        `).join("");

        document.querySelectorAll(".quiz-option-btn").forEach(btn => {
            btn.addEventListener("click", () => answerQuiz(btn.dataset.letter));
        });
    } catch (err) {
        console.error(err);
    }
}

function answerQuiz(selected) {
    if (state.quiz.answered) return;
    state.quiz.answered = true;

    const correct = state.quiz.currentQuestion.correct;
    const isCorrect = selected === correct;

    if (isCorrect) {
        state.quiz.score++;
        $("quiz-feedback").textContent = "✅ Correct!";
        $("quiz-feedback").className = "quiz-feedback correct-text";
        playDoneSound();
    } else {
        $("quiz-feedback").textContent = `❌ Incorrect — it was "${correct}"`;
        $("quiz-feedback").className = "quiz-feedback incorrect-text";
        playClickSound();
    }

    document.querySelectorAll(".quiz-option-btn").forEach(btn => {
        btn.disabled = true;
        if (btn.dataset.letter === correct) btn.classList.add("correct");
        else if (btn.dataset.letter === selected) btn.classList.add("incorrect");
    });

    $("quiz-score").textContent = `Score: ${state.quiz.score}`;

    setTimeout(() => {
        state.quiz.currentIndex++;
        if (state.quiz.currentIndex >= state.quiz.total) {
            finishQuiz();
        } else {
            loadQuizQuestion();
        }
    }, 1200);
}

async function finishQuiz() {
    $("quiz-active").style.display = "none";
    $("quiz-result").style.display = "block";
    $("quiz-final-score").textContent = `Score: ${state.quiz.score} / ${state.quiz.total}`;

    const pct = state.quiz.score / state.quiz.total;
    if (pct === 1) {
        $("quiz-result-icon").textContent = "💯";
        $("quiz-result-text").textContent = "Perfect Score!";
    } else if (pct >= 0.7) {
        $("quiz-result-icon").textContent = "🎉";
        $("quiz-result-text").textContent = "Great Job!";
    } else {
        $("quiz-result-icon").textContent = "💪";
        $("quiz-result-text").textContent = "Keep Practicing!";
    }

    try {
        const res = await fetch("/api/quiz/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode: state.mode, score: state.quiz.score, total: state.quiz.total })
        });
        const data = await res.json();
        announceAchievements(data.new_achievements);
    } catch (err) {
        console.error(err);
    }
}

// ═══════════════════════════════════════════════════════════════
// ACHIEVEMENTS
// ═══════════════════════════════════════════════════════════════

async function loadAchievements() {
    const container = $("achievements-grid");
    if (!state.user) {
        container.innerHTML = '<div class="empty-state">Log in to start earning achievements!</div>';
        return;
    }

    try {
        const res = await fetch("/api/achievements");
        const data = await res.json();
        state.achievements = data.achievements;
        renderAchievements();
    } catch (err) {
        console.error(err);
    }
}

async function loadAchievementsCount() {
    if (!state.user) return;
    try {
        const res = await fetch("/api/achievements");
        const data = await res.json();
        state.achievements = data.achievements;
    } catch (err) {
        console.error(err);
    }
}

function renderAchievements() {
    const container = $("achievements-grid");
    container.innerHTML = state.achievements.map(a => `
        <div class="achievement-card ${a.earned ? "earned" : ""}">
            <div class="achievement-icon">${a.icon}</div>
            <div>
                <div class="achievement-label">${a.label}</div>
                <div class="achievement-desc">${a.desc}</div>
                ${a.earned ? `<div class="achievement-date">Earned ✓</div>` : ""}
            </div>
        </div>
    `).join("");
}

function announceAchievements(keys) {
    if (!keys || !keys.length) return;
    const labels = {
        first_translation: "🎉 First Steps unlocked!",
        ten_translations: "🔥 Getting Fluent unlocked!",
        fifty_translations: "🏆 Sign Master unlocked!",
        first_favorite: "⭐ Bookmarked unlocked!",
        both_modes: "🌐 Bilingual unlocked!",
        quiz_complete: "📝 Quiz Taker unlocked!",
        quiz_perfect: "💯 Perfect Score unlocked!",
        daily_goal: "🎯 Goal Crusher unlocked!"
    };
    keys.forEach((k, i) => {
        setTimeout(() => {
            statusIndicator.textContent = `● ${labels[k] || "Achievement unlocked!"}`;
            statusIndicator.style.color = "var(--warning)";
        }, i * 600);
    });
}

// ═══════════════════════════════════════════════════════════════
// PROFILE
// ═══════════════════════════════════════════════════════════════

async function loadProfile() {
    if (!state.user) {
        $("profile-name").textContent = "Guest User";
        $("profile-avatar").textContent = "G";
        $("profile-since").textContent = "Log in to save your stats";
        ["stat-history", "stat-favorites", "stat-quizzes", "stat-best-quiz", "stat-achievements"].forEach(id => {
            $(id).textContent = "0";
        });
        return;
    }

    try {
        const res = await fetch("/api/profile");
        const data = await res.json();
        $("profile-name").textContent = data.user.username;
        $("profile-avatar").textContent = data.user.username[0].toUpperCase();
        const since = new Date(data.user.created_at).toLocaleDateString([], { month: "long", year: "numeric" });
        $("profile-since").textContent = `Member since ${since}`;

        $("stat-history").textContent = data.stats.history_count;
        $("stat-favorites").textContent = data.stats.favorites_count;
        $("stat-quizzes").textContent = data.stats.quiz_count;
        $("stat-best-quiz").textContent = data.stats.best_quiz_score;
        $("stat-achievements").textContent = data.stats.achievements_count;
    } catch (err) {
        console.error(err);
    }
}

// ═══════════════════════════════════════════════════════════════
// SOUND EFFECTS (Web Audio API — no external files needed)
// ═══════════════════════════════════════════════════════════════

let audioCtx = null;

function getAudioCtx() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    return audioCtx;
}

function playDoneSound() {
    if (!$("setting-sound").checked) return;
    try {
        const ctx = getAudioCtx();
        [[880, 0, 0.15], [1100, 0.15, 0.28]].forEach(([freq, start, end]) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = "sine";
            osc.frequency.value = freq;
            gain.gain.setValueAtTime(0.25, ctx.currentTime + start);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + end);
            osc.start(ctx.currentTime + start);
            osc.stop(ctx.currentTime + end);
        });
    } catch (e) { /* audio not supported */ }
}

function playClickSound() {
    if (!$("setting-sound").checked) return;
    try {
        const ctx = getAudioCtx();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.type = "sine";
        osc.frequency.value = 600;
        gain.gain.setValueAtTime(0.15, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.08);
    } catch (e) { /* ignore */ }
}

// ═══════════════════════════════════════════════════════════════
// DARK / LIGHT MODE
// ═══════════════════════════════════════════════════════════════

const LIGHT_VARS = {
    "--bg-deep":        "#f0f2f5",
    "--bg-panel":       "#ffffff",
    "--bg-card":        "#e8eaed",
    "--border":         "#d0d7de",
    "--text-main":      "#1f2328",
    "--text-secondary": "#57606a",
    "--text-muted":     "#8c959f"
};

const DARK_VARS = {
    "--bg-deep":        "#0d1117",
    "--bg-panel":       "#161b22",
    "--bg-card":        "#21262d",
    "--border":         "#30363d",
    "--text-main":      "#e6edf3",
    "--text-secondary": "#8b949e",
    "--text-muted":     "#6e7681"
};

function applyThemeMode(isDark) {
    const vars = isDark ? DARK_VARS : LIGHT_VARS;
    Object.entries(vars).forEach(([k, v]) => document.documentElement.style.setProperty(k, v));
}

// Apply immediately when user flips the toggle (live preview before saving)
$("setting-dark-mode").addEventListener("change", () => {
    applyThemeMode($("setting-dark-mode").checked);
});

// ═══════════════════════════════════════════════════════════════
// SETTINGS
// ═══════════════════════════════════════════════════════════════

$("setting-mode-isl").addEventListener("click", () => setSettingsMode("ISL"));
$("setting-mode-asl").addEventListener("click", () => setSettingsMode("ASL"));

function setSettingsMode(mode) {
    $("setting-mode-isl").classList.toggle("active", mode === "ISL");
    $("setting-mode-asl").classList.toggle("active", mode === "ASL");
}

$("setting-speed-slider").addEventListener("input", () => {
    $("setting-speed-value").textContent = parseFloat($("setting-speed-slider").value).toFixed(1) + "s";
});

async function loadSettings() {
    if (!state.user) return;
    try {
        const res = await fetch("/api/settings");
        const data = await res.json();
        state.settings = data.settings;

        $("setting-sound").checked = !!data.settings.sound_enabled;
        $("setting-dark-mode").checked = !!data.settings.dark_mode;
        applyThemeMode(!!data.settings.dark_mode);
        $("setting-speed-slider").value = data.settings.default_speed;
        $("setting-speed-value").textContent = data.settings.default_speed.toFixed(1) + "s";
        setSettingsMode(data.settings.default_mode);

        // Apply default speed + mode to the translator too, on first load
        speedSlider.value = data.settings.default_speed;
        state.speed = data.settings.default_speed;
        speedValue.textContent = state.speed.toFixed(1) + "s";
        setMode(data.settings.default_mode);

        if (data.settings.theme_color) {
            document.documentElement.style.setProperty("--primary", data.settings.theme_color);
            document.querySelectorAll(".dot").forEach(d => {
                d.classList.toggle("active", d.dataset.color === data.settings.theme_color);
            });
        }
    } catch (err) {
        console.error(err);
    }
}

$("btn-save-settings").addEventListener("click", async () => {
    if (!state.user) {
        $("settings-saved-msg").textContent = "⚠️ Log in to save settings";
        return;
    }

    const defaultMode = document.querySelector("#setting-mode-isl").classList.contains("active") ? "ISL" : "ASL";
    const activeColor = document.querySelector(".dot.active")?.dataset.color || "#3b82f6";

    const payload = {
        sound_enabled: $("setting-sound").checked ? 1 : 0,
        dark_mode: $("setting-dark-mode").checked ? 1 : 0,
        default_speed: parseFloat($("setting-speed-slider").value),
        default_mode: defaultMode,
        theme_color: activeColor
    };

    try {
        const res = await fetch("/api/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        await res.json();
        $("settings-saved-msg").textContent = "✅ Settings saved!";
        setTimeout(() => { $("settings-saved-msg").textContent = ""; }, 2000);
    } catch (err) {
        $("settings-saved-msg").textContent = "⚠️ Could not save settings";
    }
});

// ── Utility ──────────────────────────────────────────────────────
function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// ── Enter key to translate ───────────────────────────────────────
textInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        btnTranslate.click();
    }
});