import streamlit as st
import math
import random
import csv
import io
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
        margin-bottom: 10px;
    }
    .badge-hcf { background-color: #4f46e5; }
    .badge-lcm { background-color: #059669; }
    .numbers-display {
        font-size: 2.6rem;
        font-weight: 900;
        color: #1e1b4b;
        letter-spacing: 1px;
    }
    .hint-card {
        background-color: #fffbeb;
        border: 1px solid #fef3c7;
        border-radius: 12px;
        padding: 16px;
        color: #92400e;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- Math Core Helpers ---
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
                return {"type": "hcf", "numbers": numbers, "answer": g}
    
    return {"type": "hcf", "numbers": [16, 24, 40] if item_count == 3 else [36, 48], "answer": 8 if item_count == 3 else 12}

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
                return {"type": "lcm", "numbers": pick, "answer": L}

    return {"type": "lcm", "numbers": [10, 15, 20] if item_count == 3 else [12, 16], "answer": 60 if item_count == 3 else 48}

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

def create_new_question(concept, count_mode):
    target_type = random.choice(["hcf", "lcm"]) if concept == "Mixed" else concept.lower()
    target_count = random.choice([2, 3]) if count_mode == "Random (2 or 3)" else int(count_mode[0])

    if target_type == "hcf":
        q = generate_hcf_problem(target_count)
    else:
        q = generate_lcm_problem(target_count)

    q["options"] = build_distractors(q["type"], q["numbers"], q["answer"])
    return q

# --- CSV Reporting Helpers ---
def build_csv_string(logs, final_score, best_streak):
    output = io.StringIO()
    writer = csv.writer(output)
    
    total = len(logs)
    correct_count = sum(1 for q in logs if q["is_correct"])
    accuracy = round((correct_count / total) * 100) if total > 0 else 0

    badge = "🌱 Great Practice!"
    if accuracy >= 90 and total >= 5:
        badge = "🌟 Math Superstar!"
    elif accuracy >= 75 and total >= 3:
        badge = "🚀 Math Champ!"
    elif accuracy >= 50:
        badge = "👍 Good Effort!"

    writer.writerow(["=== MATH QUEST: SESSION SUMMARY ==="])
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
    writer.writerow(["Question #", "Time", "Concept", "Numbers Given", "Input Mode", "Kid Answer", "Correct Answer", "Result"])
    for q in logs:
        writer.writerow([
            q["q_num"],
            q["time"],
            q["concept"],
            q["numbers"],
            q["mode"],
            q["user_answer"],
            q["correct_answer"],
            "CORRECT" if q["is_correct"] else "WRONG"
        ])

    return output.getvalue(), badge, accuracy, correct_count, total

def save_session_to_disk(logs, final_score, best_streak):
    csv_text, badge, accuracy, correct_count, total = build_csv_string(logs, final_score, best_streak)
    
    desktop_dir = Path.home() / "Desktop"
    target_dir = desktop_dir if desktop_dir.exists() else Path.home()

    now_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filepath = target_dir / f"Math_Quest_Session_{now_str}.csv"
    
    with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
        f.write(csv_text)

    return filepath, csv_text, badge, accuracy, correct_count, total

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
if "current_question" not in st.session_state:
    st.session_state.current_question = create_new_question("HCF", "Random (2 or 3)")

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Game Settings")

concept = st.sidebar.radio(
    "Skill Concept",
    ["HCF", "LCM", "Mixed"],
    index=0
)

answer_mode = st.sidebar.radio(
    "Answer Mode",
    ["🔘 Multiple Choice", "✍️ Type In"],
    index=0
)

number_count = st.sidebar.radio(
    "Number of Items",
    ["Random (2 or 3)", "2 Numbers", "3 Numbers"],
    index=0
)

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Start Fresh Session"):
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.best_streak = 0
    st.session_state.session_logs = []
    st.session_state.answered = False
    st.session_state.feedback = None
    st.session_state.q_counter += 1
    st.session_state.current_question = create_new_question(concept, number_count)
    st.rerun()

# --- Main Metrics Header ---
st.markdown('<div class="main-title">🧮 Math Quest: HCF & LCM</div>', unsafe_allow_html=True)
st.caption("Master Highest Common Factors & Lowest Common Multiples with numbers up to 100!")

m1, m2, m3, m4 = st.columns(4)
m1.metric("⭐ Score", st.session_state.score)
m2.metric("🔥 Streak", st.session_state.streak)
m3.metric("🏆 Best Streak", st.session_state.best_streak)
m4.metric("📝 Answered", len(st.session_state.session_logs))

# --- Active Question Display ---
q = st.session_state.current_question
q_type = q["type"].upper()
badge_class = "badge-hcf" if q_type == "HCF" else "badge-lcm"
badge_text = "🛡️ Highest Common Factor (HCF)" if q_type == "HCF" else "🚀 Lowest Common Multiple (LCM)"
numbers_text = " & ".join(map(str, q["numbers"])) if len(q["numbers"]) == 2 else f"{q['numbers'][0]}, {q['numbers'][1]} & {q['numbers'][2]}"

st.markdown(f"""
<div class="question-card">
    <div class="badge {badge_class}">{badge_text} ({len(q['numbers'])} Numbers)</div>
    <div style="color: #475569; font-weight: 600; font-size: 1.05rem;">Find the {q_type} of:</div>
    <div class="numbers-display">{numbers_text}</div>
</div>
""", unsafe_allow_html=True)

# --- Answering Logic ---
def record_answer(user_val):
    correct_ans = q["answer"]
    is_correct = (user_val == correct_ans)
    
    st.session_state.answered = True
    st.session_state.session_logs.append({
        "q_num": len(st.session_state.session_logs) + 1,
        "time": datetime.now().strftime("%H:%M:%S"),
        "concept": q_type,
        "numbers": " & ".join(map(str, q["numbers"])),
        "mode": "Choices" if "Choice" in answer_mode else "Typed",
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
            "msg": f"❌ Not quite! The correct answer was {correct_ans}. Check the step-by-step hint below!"
        }

# --- Choices / Input UI ---
if not st.session_state.answered:
    if "Multiple Choice" in answer_mode:
        st.write("👉 **Choose the correct answer:**")
        cols = st.columns(len(q["options"]))
        for i, (col, opt) in enumerate(zip(cols, q["options"])):
            if col.button(str(opt), use_container_width=True, key=f"btn_opt_{st.session_state.q_counter}_{i}_{opt}"):
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

    if st.button("Next Question ➜", type="primary", use_container_width=True):
        st.session_state.answered = False
        st.session_state.feedback = None
        st.session_state.q_counter += 1
        st.session_state.current_question = create_new_question(concept, number_count)
        st.rerun()

# --- Hint Accordion ---
with st.expander("💡 Need a hint? Show Step-by-Step Working", expanded=st.session_state.answered and st.session_state.feedback["status"] == "wrong"):
    if q["type"] == "hcf":
        factor_lists = [get_factors(n) for n in q["numbers"]]
        common_factors = factor_lists[0]
        for fl in factor_lists[1:]:
            common_factors = [f for f in common_factors if f in fl]
        
        hint_md = ""
        for n, fl in zip(q["numbers"], factor_lists):
            hint_md += f"**Factors of {n}:** {', '.join(map(str, fl))}\n\n"
        hint_md += f"**Shared Factors:** {', '.join(map(str, common_factors))}\n\n"
        hint_md += f"👉 The **highest** common factor is **{q['answer']}**!"
        st.markdown(f'<div class="hint-card">{hint_md}</div>', unsafe_allow_html=True)
    else:
        hint_md = ""
        for n in q["numbers"]:
            ml = get_multiples(n, q["answer"])
            ellipsis_str = "" if q["answer"] in ml else "..."
            hint_md += f"**Multiples of {n}:** {', '.join(map(str, ml))}{ellipsis_str}\n\n"
        hint_md += f"👉 The **smallest** common multiple is **{q['answer']}**!"
        st.markdown(f'<div class="hint-card">{hint_md}</div>', unsafe_allow_html=True)

st.markdown("---")

# --- Save Session / Download Report ---
col_action1, col_action2 = st.columns([1, 1])

if len(st.session_state.session_logs) > 0:
    csv_content, badge_name, acc_val, cor_val, tot_val = build_csv_string(
        st.session_state.session_logs,
        st.session_state.score,
        st.session_state.best_streak
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
            filepath, _, _, _, _ = save_session_to_disk(
                st.session_state.session_logs,
                st.session_state.score,
                st.session_state.best_streak
            )
            st.success(f"File written to: `{filepath}`")
else:
    st.info("Complete a few questions to unlock the session report download.")

# --- Real-Time Performance Table ---
if len(st.session_state.session_logs) > 0:
    with st.expander("📊 View This Session's Question Log"):
        df = pd.DataFrame(st.session_state.session_logs)
        df["Result"] = df["is_correct"].apply(lambda x: "✅ Correct" if x else "❌ Wrong")
        df_display = df[["q_num", "time", "concept", "numbers", "mode", "user_answer", "correct_answer", "Result"]]
        df_display.columns = ["#", "Time", "Concept", "Numbers", "Mode", "Kid Answer", "Correct", "Result"]
        st.dataframe(df_display, use_container_width=True, hide_index=True)
