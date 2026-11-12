import streamlit as st
import math
import random
import csv
import io
import urllib.parse
from functools import reduce
from datetime import datetime
from pathlib import Path
import pandas as pd

# --- Page Setup ---
st.set_page_config(
    page_title="Math Quest: HCF & LCM",
    page_icon="🧮",
    layout="centered"
)

# --- Question Bank Configuration ---
SHEET_ID = "1OrTQ0UonsxQIWsid-GLcH-X8UcO4_Eu6ivlTUs7-wds"
TAB_NAME = "HCF LCM"
LOCAL_CSV_FILENAME = "P4_Math_Questions_HCF_LCM.csv"

# --- Custom Styling ---
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #312e81;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .question-card {
        background: #f8fafc;
        border: 2px solid #cbd5e1;
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    }
    .drill-card {
        background: #f8fafc;
        border: 2px dashed #94a3b8;
        border-radius: 18px;
        padding: 22px;
        text-align: center;
        margin-bottom: 20px;
    }
    .badge {
        display: inline-block;
        padding: 5px 16px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.85rem;
        color: white;
        margin-bottom: 12px;
    }
    .badge-hcf { background-color: #4f46e5; }
    .badge-lcm { background-color: #059669; }
    .badge-word { background-color: #0284c7; }
    .numbers-display {
        font-size: 2.6rem;
        font-weight: 900;
        color: #1e1b4b;
        letter-spacing: 1px;
    }
    .word-problem-text {
        font-size: 1.22rem;
        font-weight: 600;
        color: #0f172a;
        line-height: 1.65;
        text-align: left;
        margin-top: 6px;
    }
    .hint-card {
        background-color: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 12px;
        padding: 16px;
        color: #92400e;
        line-height: 1.65;
        font-size: 1.02rem;
    }
    .summary-card {
        background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 100%);
        border: 2px solid #818cf8;
        border-radius: 18px;
        padding: 24px;
        margin: 16px 0;
        text-align: center;
    }
    div.stButton > button {
        font-size: 1.05rem;
        font-weight: 700;
        border-radius: 12px;
        padding-top: 0.6rem;
        padding-bottom: 0.6rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Pandas Question Bank Loader ---
def classify_concept(row):
    expl = str(row.get("explanation", ""))
    if "Highest Common Factor" in expl or "HCF(" in expl or "HCF =" in expl:
        return "HCF"
    return "LCM"

@st.cache_data(ttl=120, show_spinner=False)
def load_question_bank(uploaded_bytes=None):
    """
    Loads the 'HCF LCM' question bank using pandas.
    Priority:
      1. User-uploaded CSV file (if provided in sidebar)
      2. Live Google Sheets CSV export ('P4 Math Questions' -> 'HCF LCM' tab)
      3. Local CSV fallback ('P4_Math_Questions_HCF_LCM.csv')
    """
    required_cols = {"id", "title", "question", "option_a", "option_b", "option_c", "option_d", "correct", "explanation"}
    df = None
    source_label = ""

    if uploaded_bytes is not None:
        df = pd.read_csv(io.BytesIO(uploaded_bytes))
        source_label = "Uploaded CSV File"
    else:
        encoded_tab = urllib.parse.quote(TAB_NAME)
        gsheet_csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_tab}"
        try:
            df = pd.read_csv(gsheet_csv_url)
            if not required_cols.issubset(set(df.columns)):
                df = None
            else:
                source_label = f"Google Sheets: P4 Math Questions ({TAB_NAME})"
        except Exception:
            df = None

        if df is None:
            local_paths = [
                Path(__file__).resolve().parent / LOCAL_CSV_FILENAME,
                Path(LOCAL_CSV_FILENAME)
            ]
            for lp in local_paths:
                if lp.exists():
                    df = pd.read_csv(lp)
                    source_label = f"Local Bank: {lp.name}"
                    break

    if df is None or df.empty:
        return pd.DataFrame(), "Unavailable"

    # Clean & standardize schema
    df = df.dropna(subset=["question", "option_a", "option_b", "option_c", "option_d", "correct"]).copy()
    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df["correct"] = df["correct"].astype(str).str.strip().str.lower()
    for col in ["title", "question", "option_a", "option_b", "option_c", "option_d", "explanation"]:
        df[col] = df[col].astype(str).str.strip()

    df["concept_tag"] = df.apply(classify_concept, axis=1)
    return df, source_label

# --- Math Core Helpers (For Quick Number Drills) ---
def gcd_multi(numbers):
    return reduce(math.gcd, numbers)

def lcm_two(a, b):
    return abs(a * b) // math.gcd(a, b)

def lcm_multi(numbers):
    return reduce(lcm_two, numbers)

def get_factors(n):
    return [i for i in range(1, n + 1) if n % i == 0]

def get_multiples(n, target_lcm, min_count=4):
    multiples = []
    i = 1
    while n * i <= target_lcm or i <= min_count:
        multiples.append(n * i)
        i += 1
        if i > 12:
            break
    return multiples

# --- Procedural Question Generators ---
def generate_hcf_problem(item_count):
    common_factors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 20]
    g = random.choice(common_factors)
    max_multiplier = max(2, 100 // g)

    for _ in range(100):
        multipliers = set()
        while len(multipliers) < item_count:
            multipliers.add(random.randint(2, max_multiplier))
        mult_list = list(multipliers)
        if gcd_multi(mult_list) == 1:
            numbers = sorted([k * g for k in mult_list])
            if max(numbers) <= 100:
                return {"source": "drill", "type": "hcf", "numbers": numbers, "answer": g}

    return {
        "source": "drill",
        "type": "hcf",
        "numbers": [16, 24, 40] if item_count == 3 else [36, 48],
        "answer": 8 if item_count == 3 else 12
    }

def generate_lcm_problem(item_count):
    candidate_lcms = [
        18, 24, 30, 36, 40, 48, 50, 60, 72, 80, 84, 90,
        100, 120, 140, 150, 160, 180, 200, 210, 240
    ]
    shuffled_lcms = candidate_lcms.copy()
    random.shuffle(shuffled_lcms)

    for L in shuffled_lcms:
        divisors = [d for d in range(3, min(101, L + 1)) if L % d == 0]
        if len(divisors) < item_count:
            continue
        for _ in range(30):
            pick = random.sample(divisors, item_count)
            pick.sort()
            if lcm_multi(pick) == L:
                return {"source": "drill", "type": "lcm", "numbers": pick, "answer": L}

    return {
        "source": "drill",
        "type": "lcm",
        "numbers": [10, 15, 20] if item_count == 3 else [12, 16],
        "answer": 60 if item_count == 3 else 48
    }

def build_distractors(problem_type, numbers, correct_ans):
    options = {correct_ans}
    candidates = set()

    if problem_type == "hcf":
        if correct_ans > 1:
            candidates.add(1)
        if correct_ans > 2:
            candidates.add(correct_ans // 2)
        candidates.add(correct_ans * 2)
        candidates.add(max(1, correct_ans - 1))
    else:
        candidates.add(gcd_multi(numbers))
        candidates.add(max(numbers))
        candidates.add(correct_ans * 2)
        if correct_ans % 2 == 0 and (correct_ans // 2) >= max(numbers):
            candidates.add(correct_ans // 2)

    candidates = {c for c in candidates if c > 0 and c != correct_ans}
    if len(candidates) >= 3:
        options.update(random.sample(list(candidates), 3))
    else:
        options.update(candidates)

    while len(options) < 4:
        step = 1 if problem_type == "hcf" else 10
        delta = random.randint(1, 4) * step
        val = max(1, correct_ans + (delta if random.random() > 0.5 else -delta))
        options.add(val)

    opt_list = list(options)[:4]
    random.shuffle(opt_list)
    return opt_list

def build_word_problem_from_row(row, shuffle_choices=False):
    corr_letter = str(row["correct"]).strip().lower()
    corr_text = str(row[f"option_{corr_letter}"]).strip()
    raw_options = [
        str(row["option_a"]).strip(),
        str(row["option_b"]).strip(),
        str(row["option_c"]).strip(),
        str(row["option_d"]).strip(),
    ]


    return {
        "source": "bank",
        "bank_id": int(row["id"]),
        "title": str(row["title"]),
        "type": str(row["concept_tag"]).lower(),
        "question_text": str(row["question"]),
        "options": raw_options,
        "answer": corr_text,
        "explanation": str(row["explanation"])
    }

def create_next_question(game_mode, concept, count_mode, bank_df, shuffle_choices=True):
    use_bank = False
    if game_mode == "📖 Word Problems (HCF LCM Bank)":
        use_bank = True
    elif game_mode == "🔀 Mixed Challenge":
        use_bank = (random.random() < 0.65) and (not bank_df.empty)

    if use_bank and not bank_df.empty:
        # Filter by concept if requested
        if concept in ["HCF", "LCM"]:
            filtered_df = bank_df[bank_df["concept_tag"] == concept]
            if filtered_df.empty:
                filtered_df = bank_df
        else:
            filtered_df = bank_df

        valid_ids = filtered_df["id"].tolist()
        # Refill queue if empty or out of sync with current filter
        queue = [qid for qid in st.session_state.bank_queue if qid in valid_ids]
        if not queue:
            queue = valid_ids.copy()
            if st.session_state.get("question_order", "🔀 Shuffled") == "🔀 Shuffled":
                random.shuffle(queue)

        next_id = queue.pop(0)
        st.session_state.bank_queue = queue
        row = filtered_df[filtered_df["id"] == next_id].iloc[0]
        return build_word_problem_from_row(row, shuffle_choices=shuffle_choices)

    # Fallback / Procedural Quick Number Drill
    target_type = random.choice(["hcf", "lcm"]) if concept == "Mixed" else concept.lower()
    target_count = random.choice([2, 3]) if count_mode == "Random (2 or 3)" else int(count_mode[0])

    if target_type == "hcf":
        q = generate_hcf_problem(target_count)
    else:
        q = generate_lcm_problem(target_count)

    q["options"] = build_distractors(q["type"], q["numbers"], q["answer"])
    return q

# --- CSV Reporting Helpers ---
def get_performance_badge(accuracy, total):
    if accuracy >= 90 and total >= 5:
        return "🌟 Math Superstar!"
    elif accuracy >= 75 and total >= 3:
        return "🚀 Math Champ!"
    elif accuracy >= 50:
        return "👍 Good Effort!"
    return "🌱 Great Practice!"

def build_csv_string(logs, final_score, best_streak, player_name="Student"):
    output = io.StringIO()
    writer = csv.writer(output)

    total = len(logs)
    correct_count = sum(1 for q in logs if q["is_correct"])
    accuracy = round((correct_count / total) * 100) if total > 0 else 0
    badge = get_performance_badge(accuracy, total)

    writer.writerow(["=== MATH QUEST: SESSION SUMMARY ==="])
    writer.writerow(["Player Name", player_name])
    writer.writerow(["Session Date & Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow(["Performance Level", badge])
    writer.writerow(["Total Questions Answered", total])
    writer.writerow(["Correct Answers", correct_count])
    writer.writerow(["Incorrect Answers", total - correct_count])
    writer.writerow(["Accuracy Rate", f"{accuracy}%"])
    writer.writerow(["Final Score", final_score])
    writer.writerow(["Best Streak", best_streak])
    writer.writerow([])
    writer.writerow(["=== DETAILED QUESTION BREAKDOWN ==="])
    writer.writerow(["Question #", "Time", "Source", "Concept", "Prompt / Numbers", "Input Mode", "Kid Answer", "Correct Answer", "Result"])
    for q in logs:
        writer.writerow([
            q["q_num"],
            q["time"],
            q["source"],
            q["concept"],
            q["numbers"],
            q["mode"],
            q["user_answer"],
            q["correct_answer"],
            "CORRECT" if q["is_correct"] else "WRONG"
        ])

    return output.getvalue(), badge, accuracy, correct_count, total

def save_session_to_disk(logs, final_score, best_streak, player_name="Student"):
    csv_text, badge, accuracy, correct_count, total = build_csv_string(logs, final_score, best_streak, player_name)

    desktop_dir = Path.home() / "Desktop"
    target_dir = desktop_dir if desktop_dir.exists() else Path.home()

    now_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    safe_name = "".join(c for c in player_name if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_") or "Student"
    filepath = target_dir / f"Math_Quest_{safe_name}_{now_str}.csv"

    with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
        f.write(csv_text)

    return filepath, csv_text, badge, accuracy, correct_count, total

# --- Sidebar Controls ---
st.sidebar.header("👤 Player & Mode")
player_name = st.sidebar.text_input("Player Name", value="Student")

game_mode = st.sidebar.radio(
    "Game Mode",
    ["📖 Word Problems (HCF LCM Bank)", "🔢 Quick Number Drills", "🔀 Mixed Challenge"],
    index=0
)

concept = st.sidebar.radio(
    "Skill Concept",
    ["Mixed", "HCF", "LCM"],
    index=0
)

# Settings specific to Word Problems vs Quick Drills
if game_mode != "🔢 Quick Number Drills":
    question_order = st.sidebar.radio(
        "Question Order",
        ["🔀 Shuffled", "🔢 Sequential (Q1 → Q20)"],
        index=0,
        key="question_order"
    )
shuffle_choices = False

if game_mode != "📖 Word Problems (HCF LCM Bank)":
    answer_mode = st.sidebar.radio(
        "Drill Answer Mode",
        ["🔘 Multiple Choice", "✍️ Type In"],
        index=0
    )
    number_count = st.sidebar.radio(
        "Drill Item Count",
        ["Random (2 or 3)", "2 Numbers", "3 Numbers"],
        index=0
    )
else:
    answer_mode = "🔘 Multiple Choice"
    number_count = "Random (2 or 3)"

# Question Bank Data Source Status
st.sidebar.markdown("---")
st.sidebar.subheader("📚 Question Bank Source")
uploaded_csv = st.sidebar.file_uploader("Optional: Upload Custom CSV", type=["csv"])
uploaded_bytes = uploaded_csv.getvalue() if uploaded_csv is not None else None

bank_df, bank_source = load_question_bank(uploaded_bytes)
if not bank_df.empty:
    st.sidebar.caption(f"✅ {bank_source} ({len(bank_df)} Qs)")
else:
    st.sidebar.warning("⚠️ Question bank CSV not found. Using Quick Drills.")

if st.sidebar.button("🔄 Reload Question Bank", use_container_width=True):
    load_question_bank.clear()
    st.rerun()

# --- Session State Initialization ---
if "score" not in st.session_state:
    st.session_state.score = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "best_streak" not in st.session_state:
    st.session_state.best_streak = 0
if "session_logs" not in st.session_state:
    st.session_state.session_logs = []
if "answered" not in st.session_state:
    st.session_state.answered = False
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "q_counter" not in st.session_state:
    st.session_state.q_counter = 0
if "bank_queue" not in st.session_state:
    st.session_state.bank_queue = []
if "session_ended" not in st.session_state:
    st.session_state.session_ended = False
if "current_question" not in st.session_state:
    st.session_state.current_question = create_next_question(game_mode, concept, number_count, bank_df, shuffle_choices)

# Reset question if user switches Game Mode or Concept filter while unanswered
filter_signature = f"{game_mode}|{concept}"
if "last_filter_sig" not in st.session_state:
    st.session_state.last_filter_sig = filter_signature
elif st.session_state.last_filter_sig != filter_signature:
    st.session_state.last_filter_sig = filter_signature
    st.session_state.bank_queue = []
    st.session_state.answered = False
    st.session_state.feedback = None
    st.session_state.q_counter += 1
    st.session_state.current_question = create_next_question(game_mode, concept, number_count, bank_df, shuffle_choices)

st.sidebar.markdown("---")
col_sb1, col_sb2 = st.sidebar.columns(2)
with col_sb1:
    if st.button("🔄 New Game", use_container_width=True):
        st.session_state.score = 0
        st.session_state.streak = 0
        st.session_state.best_streak = 0
        st.session_state.session_logs = []
        st.session_state.bank_queue = []
        st.session_state.answered = False
        st.session_state.feedback = None
        st.session_state.session_ended = False
        st.session_state.q_counter += 1
        st.session_state.current_question = create_next_question(game_mode, concept, number_count, bank_df, shuffle_choices)
        st.rerun()
with col_sb2:
    if st.button("🏁 End Game", use_container_width=True):
        st.session_state.session_ended = True
        st.rerun()

# --- Main Metrics Header ---
st.markdown('<div class="main-title">🧮 Math Quest: HCF & LCM</div>', unsafe_allow_html=True)
st.caption(f"Welcome, **{player_name}**! Master Highest Common Factors & Lowest Common Multiples.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("⭐ Score", st.session_state.score)
m2.metric("🔥 Streak", st.session_state.streak)
m3.metric("🏆 Best Streak", st.session_state.best_streak)
m4.metric("📝 Answered", len(st.session_state.session_logs))

# --- Mid-Game Exit / End-of-Session Review Screen ---
if st.session_state.session_ended:
    total_q = len(st.session_state.session_logs)
    correct_q = sum(1 for item in st.session_state.session_logs if item["is_correct"])
    acc_pct = round((correct_q / total_q) * 100) if total_q > 0 else 0
    perf_badge = get_performance_badge(acc_pct, total_q)

    st.markdown(f"""
    <div class="summary-card">
        <div style="font-size: 1.6rem; font-weight: 800; color: #1e1b4b;">{perf_badge}</div>
        <div style="font-size: 1.1rem; color: #334155; margin-top: 6px;">
            Session Summary for <strong>{player_name}</strong>
        </div>
        <div style="font-size: 1.25rem; font-weight: 700; color: #312e81; margin-top: 12px;">
            Score: {st.session_state.score} pts &nbsp;|&nbsp; Accuracy: {correct_q}/{total_q} ({acc_pct}%) &nbsp;|&nbsp; Best Streak: {st.session_state.best_streak}
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_end1, c_end2 = st.columns(2)
    with c_end1:
        if st.button("▶️ Resume Playing", type="primary", use_container_width=True):
            st.session_state.session_ended = False
            st.rerun()
    with c_end2:
        if st.button("🔄 Start Fresh Session", use_container_width=True):
            st.session_state.score = 0
            st.session_state.streak = 0
            st.session_state.best_streak = 0
            st.session_state.session_logs = []
            st.session_state.bank_queue = []
            st.session_state.answered = False
            st.session_state.feedback = None
            st.session_state.session_ended = False
            st.session_state.q_counter += 1
            st.session_state.current_question = create_next_question(game_mode, concept, number_count, bank_df, shuffle_choices)
            st.rerun()

else:
    # --- Active Question Display ---
    q = st.session_state.current_question
    q_type = q["type"].upper()
    is_bank = (q.get("source") == "bank")

    if is_bank:
        # Neutral badge before answering so concept (HCF vs LCM) is not spoiled!
        if st.session_state.answered:
            b_class = "badge-hcf" if q_type == "HCF" else "badge-lcm"
            b_label = f"📖 Question #{q['bank_id']} • {q_type} Word Problem"
        else:
            b_class = "badge-word"
            b_label = f"📖 Word Problem Challenge • Question #{q['bank_id']}"

        st.markdown(f"""
        <div class="question-card">
            <span class="badge {b_class}">{b_label}</span>
            <div class="word-problem-text">{q['question_text']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        badge_class = "badge-hcf" if q_type == "HCF" else "badge-lcm"
        badge_text = "🛡️ Highest Common Factor (HCF)" if q_type == "HCF" else "🚀 Lowest Common Multiple (LCM)"
        numbers_text = " & ".join(map(str, q["numbers"])) if len(q["numbers"]) == 2 else f"{q['numbers'][0]}, {q['numbers'][1]} & {q['numbers'][2]}"

        st.markdown(f"""
        <div class="drill-card">
            <div class="badge {badge_class}">{badge_text} ({len(q['numbers'])} Numbers)</div>
            <div style="color: #475569; font-weight: 600; font-size: 1.05rem;">Find the {q_type} of:</div>
            <div class="numbers-display">{numbers_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Answering Logic ---
    def record_answer(user_val):
        correct_ans = q["answer"]
        is_correct = (str(user_val).strip() == str(correct_ans).strip())

        if is_bank:
            summary_prompt = f"Q#{q['bank_id']}: {q['question_text'][:65]}..."
            src_label = "Question Bank"
        else:
            summary_prompt = " & ".join(map(str, q["numbers"]))
            src_label = "Quick Drill"

        st.session_state.answered = True
        st.session_state.session_logs.append({
            "q_num": len(st.session_state.session_logs) + 1,
            "time": datetime.now().strftime("%H:%M:%S"),
            "source": src_label,
            "concept": q_type,
            "numbers": summary_prompt,
            "mode": "Choices" if (is_bank or "Choice" in answer_mode) else "Typed",
            "user_answer": user_val,
            "correct_answer": correct_ans,
            "is_correct": is_correct
        })

        if is_correct:
            st.session_state.score += 10 + (st.session_state.streak * 2)
            st.session_state.streak += 1
            if st.session_state.streak > st.session_state.best_streak:
                st.session_state.best_streak = st.session_state.streak
            st.session_state.feedback = {
                "status": "correct",
                "msg": f"🎉 Excellent! {st.session_state.streak} in a row!" if st.session_state.streak > 2 else "✨ Correct! Outstanding work!"
            }
            if st.session_state.streak >= 3:
                st.balloons()
        else:
            st.session_state.streak = 0
            st.session_state.feedback = {
                "status": "wrong",
                "msg": f"❌ Not quite! The correct answer was **{correct_ans}**. Check the step-by-step explanation below!"
            }

    # --- Choices / Input UI (Dynamic A., B., C., D. prefixes at runtime) ---
    option_prefixes = ["A", "B", "C", "D"]

    if not st.session_state.answered:
        if is_bank or "Multiple Choice" in answer_mode:
            st.write("👉 **Choose the correct answer:**")
            # For word problems with text options, render in a clean 2x2 grid for high readability
            if is_bank:
                row1_cols = st.columns(2)
                row2_cols = st.columns(2)
                grid_cols = [row1_cols[0], row1_cols[1], row2_cols[0], row2_cols[1]]
                for i, (col, opt) in enumerate(zip(grid_cols, q["options"])):
                    label_str = f"{option_prefixes[i]}. {opt}"
                    if col.button(label_str, use_container_width=True, key=f"btn_opt_{st.session_state.q_counter}_{i}_{opt}"):
                        record_answer(opt)
                        st.rerun()
            else:
                cols = st.columns(len(q["options"]))
                for i, (col, opt) in enumerate(zip(cols, q["options"])):
                    label_str = f"{option_prefixes[i]}. {opt}"
                    if col.button(label_str, use_container_width=True, key=f"btn_opt_{st.session_state.q_counter}_{i}_{opt}"):
                        record_answer(opt)
                        st.rerun()
        else:
            with st.form(f"typed_form_{st.session_state.q_counter}", clear_on_submit=False):
                st.write("👉 **Type your answer and press Check:**")
                user_input = st.number_input(
                    "Your Answer",
                    min_value=1,
                    max_value=2000,
                    step=1,
                    value=None,
                    placeholder="Type number here..."
                )
                submit_btn = st.form_submit_button("Check ➜", use_container_width=True)
                if submit_btn:
                    if user_input is not None:
                        record_answer(int(user_input))
                        st.rerun()
                    else:
                        st.warning("Please enter a number before checking!")
    else:
        if st.session_state.feedback["status"] == "correct":
            st.success(st.session_state.feedback["msg"])
        else:
            st.error(st.session_state.feedback["msg"])

        col_next1, col_next2 = st.columns([3, 1])
        with col_next1:
            if st.button("Next Question ➜", type="primary", use_container_width=True):
                st.session_state.answered = False
                st.session_state.feedback = None
                st.session_state.q_counter += 1
                st.session_state.current_question = create_next_question(game_mode, concept, number_count, bank_df, shuffle_choices)
                st.rerun()
        with col_next2:
            if st.button("🏁 Finish", use_container_width=True):
                st.session_state.session_ended = True
                st.rerun()

    # --- Hint / Solution Explanation Accordion ---
    if is_bank:
        expander_title = "📖 Step-by-Step Solution & Explanation" if st.session_state.answered else "💡 Need a strategy hint?"
        with st.expander(expander_title, expanded=st.session_state.answered):
            if st.session_state.answered:
                st.markdown(f'<div class="hint-card"><strong>Concept:</strong> {q_type}<br><br><strong>Explanation:</strong> {q["explanation"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="hint-card">'
                    '<strong>How to decide between HCF and LCM:</strong><br>'
                    '• <strong>Slicing down / sharing into equal groups</strong> (with none left over, or subtracting leftovers first) → Use <strong>HCF</strong>.<br>'
                    '• <strong>Repeating cycles / matching pack sizes / lining up rows</strong> (adding remainders at the end) → Use <strong>LCM</strong>.'
                    '</div>',
                    unsafe_allow_html=True
                )
    else:
        with st.expander("💡 Need a hint? Show Step-by-Step Working", expanded=st.session_state.answered and st.session_state.feedback["status"] == "wrong"):
            if q["type"] == "hcf":
                factor_lists = [get_factors(n) for n in q["numbers"]]
                common_factors = factor_lists[0]
                for fl in factor_lists[1:]:
                    common_factors = [f for f in common_factors if f in fl]

                hint_md = ""
                for n, fl in zip(q["numbers"], factor_lists):
                    hint_md += f"**Factors of {n}:** {', '.join(map(str, fl))}<br><br>"
                hint_md += f"**Shared Factors:** {', '.join(map(str, common_factors))}<br><br>"
                hint_md += f"👉 The **highest** common factor is **{q['answer']}**!"
                st.markdown(f'<div class="hint-card">{hint_md}</div>', unsafe_allow_html=True)
            else:
                hint_md = ""
                for n in q["numbers"]:
                    ml = get_multiples(n, q["answer"])
                    ellipsis_str = "" if q["answer"] in ml else "..."
                    hint_md += f"**Multiples of {n}:** {', '.join(map(str, ml))}{ellipsis_str}<br><br>"
                hint_md += f"👉 The **smallest** common multiple is **{q['answer']}**!"
                st.markdown(f'<div class="hint-card">{hint_md}</div>', unsafe_allow_html=True)

st.markdown("---")

# --- Save Session / Download Report ---
col_action1, col_action2 = st.columns([1, 1])

if len(st.session_state.session_logs) > 0:
    csv_content, badge_name, acc_val, cor_val, tot_val = build_csv_string(
        st.session_state.session_logs,
        st.session_state.score,
        st.session_state.best_streak,
        player_name
    )

    with col_action1:
        st.download_button(
            label="⬇️ Download Session CSV Report",
            data=csv_content.encode("utf-8-sig"),
            file_name=f"Math_Quest_Session_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_action2:
        if st.button("💾 Save to Desktop / Server Disk", use_container_width=True):
            filepath, _, _, _, _, _ = save_session_to_disk(
                st.session_state.session_logs,
                st.session_state.score,
                st.session_state.best_streak,
                player_name
            )
            st.success(f"File written to: `{filepath}`")
else:
    st.info("Complete a few questions to unlock the session report download.")

# --- Real-Time Performance Table ---
if len(st.session_state.session_logs) > 0:
    with st.expander("📊 View This Session's Question Log"):
        df_log = pd.DataFrame(st.session_state.session_logs)
        df_log["Result"] = df_log["is_correct"].apply(lambda x: "✅ Correct" if x else "❌ Wrong")
        df_display = df_log[["q_num", "time", "source", "concept", "numbers", "user_answer", "correct_answer", "Result"]]
        df_display.columns = ["#", "Time", "Source", "Concept", "Question / Numbers", "Kid Answer", "Correct", "Result"]
        st.dataframe(df_display, use_container_width=True, hide_index=True)
