"""
MediSense — Smart Health Advisory System
FINAL VERSION: app5 stability + app4 clickable chips + next-level UI enhancements
─────────────────────────────────────────────────────────────────────────────────
New in this version:
  • Truly clickable Quick-Select chips (st.button per chip, no multiselect needed)
  • Expanded symptom list (25 chips across 5 categories)
  • Particle/star animated hero background (CSS only)
  • Symptom counter badge showing how many are selected
  • Severity level indicator on results
  • Animated scan-line result reveal
  • Smooth chip toggle with category labels
  • Body-system hint icons next to chips
  • All app5 textarea/text-fill-color visibility fixes
  • Correct flat-file db_path (same folder as script)
  • @keyframes pulseRing for the live-dot
  • Improved mobile responsiveness

FIXES (cloud-ready):
  • Hero badges and footer now use f-strings so APP_VERSION / TOTAL_QUICK_CHIPS interpolate
  • Microphone button gracefully falls back on cloud (no sounddevice crash)
  • Broken Kannada tab_appointment label replaced with safe fallback
  • SQLite db stored in /tmp so it works on read-only cloud filesystems
"""

import streamlit as st
import os
import sys
import time as _time


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DISCLAIMER
from analyser import analyse_symptoms
from multilingualprocessor import MultilingualProcessor
from voice_input_helper import get_voice_input_from_file
from reminder_system import MedicineReminderSystem
from ui_translator import get_label
from followup_questions import get_followup_questions
from diet_advice import get_diet_advice, DIET_ADVICE
from appointment_finder import get_nearby_doctors_info

# (No WebRTC VAD) Use RMS fallback for silence detection.
WEBRTC_VAD_AVAILABLE = False

# ── Use /tmp for the DB so it works on Streamlit Cloud (ephemeral is fine) ────
REMINDER_DB_PATH = "/tmp/medisense_reminders.db"

APP_VERSION = "v3.2"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediSense",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Master CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ────────────────── Variables ────────────────── */
:root {
  --bg:        #030810;
  --bg2:       #060d1a;
  --surface:   rgba(255,255,255,0.03);
  --glass:     rgba(255,255,255,0.055);
  --glass-b:   rgba(255,255,255,0.09);
  --border:    rgba(255,255,255,0.07);
  --border-h:  rgba(0,212,170,0.38);
  --cyan:      #00d4aa;
  --cyan-dim:  rgba(0,212,170,0.14);
  --blue:      #4f8ef7;
  --blue-dim:  rgba(79,142,247,0.14);
  --violet:    #a78bfa;
  --amber:     #f59e0b;
  --rose:      #f43f5e;
  --text:      #e2eeff;
  --muted:     #546785;
  --muted2:    #354260;
  --glow-c:    rgba(0,212,170,0.18);
  --glow-b:    rgba(79,142,247,0.18);
  --r:         20px;
}

/* ────────────────── Reset ────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* ────────────────── App background — star field + grid ────────────────── */
[data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  background-image:
    radial-gradient(ellipse 90% 60% at 8%  10%,  rgba(0,212,170,0.07) 0%, transparent 55%),
    radial-gradient(ellipse 70% 50% at 92% 85%,  rgba(79,142,247,0.07) 0%, transparent 55%),
    radial-gradient(ellipse 40% 35% at 55% 5%,   rgba(167,139,250,0.04) 0%, transparent 50%),
    linear-gradient(rgba(255,255,255,0.016) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.016) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 100% 100%, 48px 48px, 48px 48px;
}

[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
footer { visibility: hidden !important; display: none !important; }
#MainMenu { visibility: hidden !important; }
.viewerBadge_container__1QSob { display: none !important; }
.viewerBadge_link__1S137 { display: none !important; }

/* ────────────────── Scrollbar ────────────────── */
::-webkit-scrollbar       { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--muted2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan); }

/* ────────────────── Keyframes ────────────────── */
@keyframes fadeUp    { from { opacity:0; transform:translateY(22px); } to { opacity:1; transform:translateY(0); } }
@keyframes blink     { 0%,100%{opacity:1;} 50%{opacity:0.25;} }
@keyframes floatY    { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-7px);} }
@keyframes pulseRing {
  0%   { transform:scale(1);   opacity:0.7; }
  100% { transform:scale(2.2); opacity:0; }
}
@keyframes scanIn {
  0%   { clip-path: inset(0 100% 0 0); opacity:0; }
  100% { clip-path: inset(0 0%   0 0); opacity:1; }
}
@keyframes shimmer {
  0%   { background-position: -300% center; }
  100% { background-position:  300% center; }
}
@keyframes chipPop {
  0%   { transform: scale(1); }
  40%  { transform: scale(1.12); }
  100% { transform: scale(1); }
}

/* ────────────────── Hero ────────────────── */
.hero {
  position:relative; padding:52px 56px 48px; margin-bottom:28px;
  border-radius:28px;
  background: linear-gradient(135deg,
    rgba(0,212,170,0.06) 0%,
    rgba(3,8,16,0.97)   40%,
    rgba(79,142,247,0.06) 100%
  );
  border:1px solid var(--border); overflow:hidden; animation:fadeUp 0.7s ease both;
}
/* Floating orbs */
.hero::before {
  content:''; position:absolute; top:-90px; right:-90px; width:340px; height:340px;
  background:radial-gradient(circle,rgba(0,212,170,0.11)0%,transparent 65%);
  border-radius:50%; animation:floatY 7s ease-in-out infinite;
  pointer-events:none;
}
.hero::after {
  content:''; position:absolute; bottom:-70px; left:18%; width:260px; height:260px;
  background:radial-gradient(circle,rgba(79,142,247,0.09)0%,transparent 65%);
  border-radius:50%; animation:floatY 9s ease-in-out infinite reverse;
  pointer-events:none;
}
/* Decorative corner accent */
.hero-corner {
  position:absolute; top:0; right:0; width:200px; height:200px;
  background:conic-gradient(from 180deg at 100% 0%, rgba(0,212,170,0.08) 0deg, transparent 90deg);
  pointer-events:none;
}

.hero-eyebrow {
  display:inline-flex; align-items:center; gap:10px; position:relative;
  background:rgba(0,212,170,0.08); border:1px solid rgba(0,212,170,0.22);
  border-radius:100px; padding:5px 16px; font-size:0.66rem; font-weight:700;
  letter-spacing:2px; text-transform:uppercase; color:var(--cyan); margin-bottom:20px;
}
.live-dot {
  position:relative; width:8px; height:8px; border-radius:50%;
  background:var(--cyan); box-shadow:0 0 10px var(--cyan);
  animation:blink 2s ease-in-out infinite; display:inline-block; flex-shrink:0;
}
.live-dot::after {
  content:''; position:absolute; inset:-2px;
  border-radius:50%; border:1.5px solid var(--cyan);
  animation:pulseRing 2s ease-out infinite; opacity:0;
}

.hero-title {
  font-family:'Syne',sans-serif; font-size:clamp(2.6rem,5.5vw,4rem); font-weight:800;
  line-height:1.0; letter-spacing:-2.5px;
  background:linear-gradient(135deg,#ffffff 15%,#b8d5ff 50%,var(--cyan) 88%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  margin:0 0 12px; display:block;
}
.hero-sub {
  font-size:1.05rem; color:var(--muted); font-weight:300;
  max-width:500px; line-height:1.65; letter-spacing:0.15px;
}
.hero-badge-row { display:flex; gap:10px; flex-wrap:wrap; margin-top:26px; }
.hero-badge {
  background:var(--surface); border:1px solid var(--border); border-radius:10px;
  padding:6px 14px; font-size:0.71rem; color:var(--muted); font-weight:500;
  transition:all 0.2s ease;
}
.hero-badge:hover { border-color:var(--cyan); color:var(--cyan); }
.hero-badge span { color:var(--cyan); margin-right:4px; }

/* ────────────────── Tabs ────────────────── */
[data-testid="stTabs"] [role="tablist"] {
  background:rgba(255,255,255,0.025)!important; border:1px solid var(--border)!important;
  border-radius:18px!important; padding:6px!important; gap:4px!important;
  backdrop-filter:blur(16px)!important;
}
[data-testid="stTabs"] button[role="tab"] {
  font-family:'Syne',sans-serif!important; font-weight:600!important;
  font-size:0.78rem!important; letter-spacing:0.5px!important; color:var(--muted)!important;
  border-radius:13px!important; padding:10px 22px!important;
  transition:all 0.25s ease!important; border:none!important; position:relative!important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  background:linear-gradient(135deg,var(--blue),var(--cyan))!important;
  color:#fff!important;
  box-shadow:0 4px 20px rgba(0,212,170,0.28),0 0 0 1px rgba(0,212,170,0.12)!important;
}
[data-testid="stTabs"] button[role="tab"]:hover:not([aria-selected="true"]) {
  color:var(--text)!important; background:rgba(255,255,255,0.05)!important;
}
[data-testid="stTabContent"] { animation:fadeUp 0.4s ease both!important; }

/* ────────────────── Section title ────────────────── */
.sec-title {
  font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:700; color:var(--text);
  margin:4px 0 24px; display:flex; align-items:center; gap:14px;
}
.sec-title::before {
  content:''; display:block; width:4px; height:24px; flex-shrink:0;
  background:linear-gradient(to bottom,var(--cyan),var(--blue));
  border-radius:4px; box-shadow:0 0 14px var(--glow-c);
}

/* ────────────────── Glass panel (HTML-only blocks) ────────────────── */
.gpanel {
  background:var(--glass); border:1px solid var(--border); border-radius:22px;
  padding:28px 30px; backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px);
  transition:border-color 0.3s,box-shadow 0.3s; position:relative; overflow:hidden;
}
.gpanel::before {
  content:''; position:absolute; top:0; left:0; right:0; height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,212,170,0.35),rgba(79,142,247,0.35),transparent);
  pointer-events:none;
}
.gpanel:hover { border-color:var(--border-h); box-shadow:0 0 50px rgba(0,212,170,0.05); }

/* ────────────────── Panel title ────────────────── */
.panel-title {
  font-family:'Syne',sans-serif; font-weight:700; font-size:0.9rem;
  margin-bottom:18px; color:#e2eeff; display:flex; align-items:center; gap:8px;
}

/* ────────────────── Quick-Select chip system ────────────────── */
.chip-cat {
  font-size:0.6rem; font-weight:700; letter-spacing:1.8px;
  text-transform:uppercase; color:var(--muted2); margin: 10px 0 6px;
}
.chip-grid { display:flex; flex-wrap:wrap; gap:7px; margin-bottom:4px; }

.chip-btn > button {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 100px !important;
  padding: 5px 14px !important;
  font-size: 0.76rem !important;
  font-weight: 500 !important;
  color: var(--muted) !important;
  font-family: 'DM Sans', sans-serif !important;
  cursor: pointer !important;
  transition: all 0.18s ease !important;
  white-space: nowrap !important;
  min-height: unset !important;
  line-height: 1.4 !important;
  width: auto !important;
}
.chip-btn > button:hover {
  border-color: var(--cyan) !important;
  color: var(--cyan) !important;
  background: var(--cyan-dim) !important;
  box-shadow: 0 0 14px rgba(0,212,170,0.18) !important;
  transform: translateY(-1px) !important;
}
.chip-active > button {
  background: linear-gradient(135deg, var(--cyan-dim), var(--blue-dim)) !important;
  border-color: var(--cyan) !important;
  color: var(--cyan) !important;
  font-weight: 700 !important;
  box-shadow: 0 0 16px rgba(0,212,170,0.22), inset 0 0 8px rgba(0,212,170,0.06) !important;
}
.chip-active > button:hover {
  box-shadow: 0 0 22px rgba(0,212,170,0.32), inset 0 0 8px rgba(0,212,170,0.08) !important;
}

.chip-counter {
  display:inline-flex; align-items:center; justify-content:center;
  background:linear-gradient(135deg,var(--cyan),var(--blue));
  color:#fff; border-radius:100px; padding:2px 10px;
  font-size:0.68rem; font-weight:800; letter-spacing:0.5px;
  margin-left:8px; vertical-align:middle;
  box-shadow: 0 2px 10px rgba(0,212,170,0.3);
}

/* ────────────────── Results ────────────────── */
.result-block { animation:fadeUp 0.6s ease both; }
.result-condition {
  background:linear-gradient(135deg,rgba(0,212,170,0.07),rgba(0,212,170,0.02));
  border:1px solid rgba(0,212,170,0.22); border-radius:18px; padding:24px 28px;
  position:relative; overflow:hidden; animation:scanIn 0.5s ease both;
}
.result-condition::before {
  content:''; position:absolute; left:0; top:0; bottom:0; width:3px;
  background:linear-gradient(to bottom,var(--cyan),transparent);
}
.result-advice {
  background:linear-gradient(135deg,rgba(79,142,247,0.07),rgba(79,142,247,0.02));
  border:1px solid rgba(79,142,247,0.22); border-radius:18px; padding:24px 28px;
  position:relative; overflow:hidden;
}
.result-advice::before {
  content:''; position:absolute; left:0; top:0; bottom:0; width:3px;
  background:linear-gradient(to bottom,var(--blue),transparent);
}
.rlabel { font-size:0.62rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px; }
.rvalue { font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:700; margin-bottom:6px; }
.rtags  { margin-top:12px; display:flex; flex-wrap:wrap; gap:6px; }
.rtag   {
  background:rgba(0,212,170,0.09); border:1px solid rgba(0,212,170,0.18);
  border-radius:6px; padding:3px 10px; font-size:0.71rem; color:var(--cyan);
}
.confidence-pill {
  display:inline-flex; align-items:center; gap:6px;
  background:rgba(255,255,255,0.06); border:1px solid rgba(79,142,247,0.35);
  border-radius:999px; padding:6px 12px; font-size:0.74rem;
  color:#dbeafe; margin-top:10px;
}
.alt-pred {
  background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08);
  border-radius:12px; padding:8px 12px; margin-top:10px;
  font-size:0.78rem; color:var(--muted);
}
.uncertainty-note {
  background:rgba(245,158,11,0.12);
  border:1px solid rgba(245,158,11,0.24);
  color:#fbbf24;
  border-radius:14px;
  padding:14px 16px;
  margin-top:12px;
  font-size:0.82rem;
  line-height:1.5;
}
.explain-item {
  margin-top:6px;
  padding-left:10px;
  border-left:2px solid rgba(79,142,247,0.35);
  color:var(--text);
}
.severity-badge {
  display:inline-flex; align-items:center; gap:5px;
  border-radius:8px; padding:4px 12px; font-size:0.7rem;
  font-weight:700; letter-spacing:0.8px; text-transform:uppercase;
  margin-top:12px;
}

/* ────────────────── Metric cards ────────────────── */
.mcard {
  background:var(--glass); border:1px solid var(--border); border-radius:20px;
  padding:28px 20px 24px; text-align:center; position:relative; overflow:hidden;
  transition:all 0.3s ease; backdrop-filter:blur(18px); animation:fadeUp 0.5s ease both;
}
.mcard::after {
  content:''; position:absolute; inset:0;
  background:radial-gradient(circle at 50% 0%,rgba(0,212,170,0.04)0%,transparent 60%);
  pointer-events:none;
}
.mcard:hover { transform:translateY(-5px); border-color:rgba(0,212,170,0.28);
  box-shadow:0 20px 50px rgba(0,0,0,0.45),0 0 24px rgba(0,212,170,0.07); }
.mcard-icon { font-size:1.7rem; margin-bottom:10px; display:block; }
.mcard-val {
  font-family:'Syne',sans-serif; font-size:2.4rem; font-weight:800;
  background:linear-gradient(135deg,var(--cyan),var(--blue));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  background-clip:text; line-height:1; margin-bottom:7px;
}
.mcard-lbl { font-size:0.68rem; font-weight:600; letter-spacing:1.3px;
  text-transform:uppercase; color:var(--muted); }

/* ────────────────── Reminder items ────────────────── */
.rem-item {
  background:var(--glass); border:1px solid var(--border); border-radius:14px;
  padding:14px 18px; display:flex; align-items:center; gap:14px;
  margin-bottom:8px; transition:all 0.2s ease;
}
.rem-item:hover { border-color:rgba(0,212,170,0.22); background:var(--glass-b); }
.rem-time {
  background:linear-gradient(135deg,var(--cyan-dim),var(--blue-dim));
  border:1px solid rgba(0,212,170,0.22); color:var(--cyan);
  font-family:'Syne',sans-serif; font-weight:700; font-size:0.78rem;
  padding:6px 13px; border-radius:10px; white-space:nowrap;
}
.rem-name { font-weight:500; font-size:0.92rem; flex:1; color:var(--text); }

/* ────────────────── Empty state ────────────────── */
.empty-state { text-align:center; padding:52px 20px; color:var(--muted); }
.e-icon  { font-size:3.2rem; display:block; margin-bottom:16px; animation:floatY 3s ease-in-out infinite; }
.e-title { font-family:'Syne',sans-serif; font-size:1rem; font-weight:700;
  color:var(--muted); margin-bottom:8px; }
.e-sub   { font-size:0.8rem; color:var(--muted2); }

/* ────────────────── Feature cards ────────────────── */
.feat-card {
  background:var(--glass); border:1px solid var(--border); border-radius:18px;
  padding:26px 20px; text-align:center; transition:all 0.28s ease;
  position:relative; overflow:hidden;
}
.feat-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg,var(--cyan),var(--blue));
  transform:scaleX(0); transition:transform 0.32s ease; transform-origin:left;
}
.feat-card:hover::before { transform:scaleX(1); }
.feat-card:hover { border-color:rgba(0,212,170,0.22); transform:translateY(-4px);
  box-shadow:0 16px 40px rgba(0,0,0,0.38); }
.feat-icon  { font-size:2.2rem; margin-bottom:14px; }
.feat-title { font-family:'Syne',sans-serif; font-weight:700; font-size:0.9rem;
  color:var(--text); margin-bottom:8px; }
.feat-desc  { font-size:0.78rem; color:var(--muted); line-height:1.6; }

/* ────────────────── Disclaimer ────────────────── */
.disc {
  background:rgba(245,158,11,0.05); border:1px solid rgba(245,158,11,0.18);
  border-radius:14px; padding:16px 22px; font-size:0.78rem; color:var(--muted);
  line-height:1.75; margin-top:24px;
}
.disc strong { color:var(--amber); }

/* ────────────────── Footer ────────────────── */
.footer {
  text-align:center; padding:30px 0 18px; font-size:0.72rem; color:var(--muted2);
  border-top:1px solid var(--border); margin-top:52px; letter-spacing:0.4px;
}
.footer .hl { color:var(--cyan); font-weight:600; }

/* ────────────────── Form inputs — visibility fix ────────────────── */
[data-testid="stTextArea"] textarea {
  background: rgba(8, 18, 38, 0.88) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  color: #e2eeff !important;
  caret-color: var(--cyan) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.9rem !important;
  -webkit-text-fill-color: #e2eeff !important;
  transition: border-color 0.22s, box-shadow 0.22s !important;
}
[data-testid="stTextArea"] textarea::placeholder {
  color: #546785 !important;
  -webkit-text-fill-color: #546785 !important;
}
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 3px var(--glow-c) !important;
  background: rgba(0,28,48,0.92) !important;
  -webkit-text-fill-color: #e2eeff !important;
}
[data-testid="stTextInput"] input {
  background: rgba(8, 18, 38, 0.88) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  color: #e2eeff !important;
  caret-color: var(--cyan) !important;
  -webkit-text-fill-color: #e2eeff !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.9rem !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 3px var(--glow-c) !important;
  -webkit-text-fill-color: #e2eeff !important;
}
[data-testid="stWidgetLabel"] p, label {
  font-size:0.7rem!important; font-weight:700!important; letter-spacing:1.2px!important;
  text-transform:uppercase!important; color:var(--muted)!important;
}
[data-testid="stSelectbox"] > div > div {
  background:rgba(8,18,38,0.88)!important; border:1px solid var(--border)!important;
  border-radius:12px!important; color:var(--text)!important;
}
[data-testid="stTimeInput"] input {
  background:rgba(8,18,38,0.88)!important; border:1px solid var(--border)!important;
  border-radius:10px!important; color:var(--text)!important;
  -webkit-text-fill-color:#e2eeff!important;
}

/* ────────────────── Streamlit container styling ────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: 22px !important;
  backdrop-filter: blur(20px) !important;
  -webkit-backdrop-filter: blur(20px) !important;
  overflow: visible !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: var(--border-h) !important;
}

/* ────────────────── Primary buttons ────────────────── */
.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button {
  background:linear-gradient(135deg,var(--blue)0%,var(--cyan)100%)!important;
  border:none!important; border-radius:14px!important; color:#fff!important;
  font-family:'Syne',sans-serif!important; font-weight:700!important;
  font-size:0.84rem!important; letter-spacing:0.6px!important; padding:13px 24px!important;
  transition:all 0.25s ease!important;
  box-shadow:0 4px 20px rgba(0,212,170,0.22)!important; width:100%!important;
}
.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button:hover {
  transform:translateY(-2px)!important;
  box-shadow:0 10px 32px rgba(0,212,170,0.38)!important;
}

/* ────────────────── Secondary buttons ────────────────── */
.stButton > button:not([kind="primary"]) {
  background:rgba(255,255,255,0.04)!important; border:1px solid var(--border)!important;
  border-radius:10px!important; color:var(--muted)!important;
  font-family:'DM Sans',sans-serif!important; font-weight:500!important;
  transition:all 0.2s ease!important;
}
.stButton > button:not([kind="primary"]):hover {
  border-color:var(--rose)!important; color:var(--rose)!important;
  background:rgba(244,63,94,0.06)!important;
}

/* ────────────────── Alerts / spinner ────────────────── */
[data-testid="stAlert"] { border-radius:14px!important; font-family:'DM Sans',sans-serif!important; }
[data-testid="stSpinner"] > div { border-top-color:var(--cyan)!important; }

/* ────────────────── Sidebar ────────────────── */
[data-testid="stSidebar"] {
  background:rgba(4,10,22,0.97)!important;
  border-right:1px solid var(--border)!important;
  backdrop-filter:blur(24px)!important;
}

/* ────────────────── Analyze button row ────────────────── */
.analyze-row { margin-top:4px; }

/* ────────────────── Progress bar override ────────────────── */
[data-testid="stProgressBar"] > div > div {
  background: linear-gradient(90deg, var(--cyan), var(--blue)) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Symptom categories for enhanced chip selector ─────────────────────────────
SYMPTOM_CATEGORIES = {
    "🌡️ General": [
        "fever", "fatigue", "weakness", "weight_loss", "chills"
    ],
    "🫁 Respiratory": [
        "cough", "breathlessness", "chest_pain", "wheezing"
    ],
    "🤢 Digestive": [
        "nausea", "vomiting", "stomach_pain", "diarrhoea", "loss_of_appetite"
    ],
    "🧠 Neurological": [
        "headache", "dizziness", "blurred_and_distorted_vision", "anxiety"
    ],
    "🦴 Musculoskeletal": [
        "joint_pain", "muscle_wasting", "back_pain", "skin_rash"
    ],
}
TOTAL_QUICK_CHIPS = sum(len(symptoms) for symptoms in SYMPTOM_CATEGORIES.values())


# ── Session state ─────────────────────────────────────────────────────────────
def _init_state():
  if 'translator' not in st.session_state:
    st.session_state.translator = MultilingualProcessor()
  if 'reminder_system' not in st.session_state:
    st.session_state.reminder_system = MedicineReminderSystem(REMINDER_DB_PATH)
  if 'language' not in st.session_state:
    st.session_state.language = 'en'
  if 'selected_chips' not in st.session_state:
    st.session_state.selected_chips = set()
  if 'last_input' not in st.session_state:
    st.session_state.last_input = ''
  if 'followup_responses' not in st.session_state:
    st.session_state.followup_responses = {}
  if 'followup_just_ran' not in st.session_state:
    st.session_state.followup_just_ran = False
  if 'last_result' not in st.session_state:
    st.session_state.last_result = None
  if 'voice_fill' not in st.session_state:
    st.session_state.voice_fill = ''
  if 'voice_toast' not in st.session_state:
    st.session_state.voice_toast = None
  if 'alarm_dismissed' not in st.session_state:
    st.session_state.alarm_dismissed = set()
  if 'voice_duration' not in st.session_state:
    st.session_state.voice_duration = 8
  if 'voice_autostop' not in st.session_state:
    st.session_state.voice_autostop = True
  if 'voice_silence_threshold' not in st.session_state:
    st.session_state.voice_silence_threshold = 700
  if 'voice_silence_duration' not in st.session_state:
    st.session_state.voice_silence_duration = 1.0


# ── Analysis runner ───────────────────────────────────────────────────────────
def _run_analysis(symptom_input: str):
    lang = st.session_state.get('language', 'en')
    with st.spinner(get_label('running_diagnostic', lang)):
        result = analyse_symptoms(symptom_input)
    if result['disease'] == 'Unknown':
        st.session_state.last_result = None
        st.warning(get_label('no_symptoms', lang))
    else:
        st.session_state.last_input = symptom_input
        if st.session_state.followup_responses:
            result['followup_answers'] = st.session_state.followup_responses
        st.session_state.last_result = result
        st.rerun()


def _collect_followup_answers(result):
    followups = get_followup_questions(result.get('matched', []))
    answers = {}
    for symptom, questions in followups.items():
        for idx, (prompt, input_type, extra) in enumerate(questions):
            key = f"followup_{symptom}_{idx}"
            answer = st.session_state.get(key)
            if input_type == 'number':
                if answer is None or answer == 0:
                    continue
            elif answer in (None, ''):
                continue
            answers[prompt] = answer
    return answers


def _rerun_with_followup(result):
  answers = _collect_followup_answers(result)
  st.session_state.followup_responses = answers
  # mark that we triggered a follow-up re-run so UI can show a confirmation
  st.session_state.followup_just_ran = True
  base_input = st.session_state.get('last_input', '')
  extra_text = ' '.join(f"{prompt} {answer}" for prompt, answer in answers.items())
  if extra_text:
    _run_analysis(f"{base_input} {extra_text}".strip())
  else:
    _run_analysis(base_input)


def _get_severity(disease: str, low_confidence: bool = False) -> tuple:
    """Return (level, color, emoji) based on disease name and confidence."""
    if low_confidence:
        return "Possible match", "#f59e0b", "⚠️"

    emergency = {'Heart attack', 'Paralysis (brain hemorrhage)'}
    high = {'Pneumonia', 'Malaria', 'Dengue', 'Typhoid', 'Tuberculosis', 'AIDS'}
    medium = {'Diabetes', 'Hypertension', 'Hepatitis B', 'Hepatitis C', 'Hepatitis D'}

    if disease in emergency:
        return "Emergency", "#f43f5e", "🚨"
    elif disease in high:
        return "Seek Medical Attention", "#f59e0b", "⚠️"
    elif disease in medium:
        return "Consult a Doctor", "#a78bfa", "🩺"
    else:
        return "Self-care & Monitor", "#00d4aa", "💚"


# ── Tab 1: Symptom Analyzer ───────────────────────────────────────────────────
def show_symptom_analyzer():
    lang = st.session_state.get('language', 'en')
    # Show confirmation once after a follow-up re-run
    if st.session_state.get('followup_just_ran'):
        st.success('Re-run completed with follow-up details.')
        st.session_state.followup_just_ran = False
    st.markdown(f'<div class="sec-title">{get_label("symptom_analyzer", lang)}</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        with st.container(border=True):
          lang_options = {'English': 'en', 'Hindi': 'hi', 'Kannada': 'kn'}
          options = list(lang_options.keys())
          # Determine current selection from session state language code
          current_code = st.session_state.get('language', 'en')
          current_label = next((k for k, v in lang_options.items() if v == current_code), options[0])
          selected_lang = st.selectbox(
            get_label('language', st.session_state.language),
            options=options,
            index=options.index(current_label),
            key="lang_sel"
          )
          # Update session language only if changed
          sel_code = lang_options.get(selected_lang, 'en')

          st.session_state.language = sel_code

          # ── Voice mic button — graceful fallback on cloud ─────────────────
          def _store_voice(text, source="mic"):
            if not text:
              st.warning(get_label('could_not_understand', st.session_state.language))
              return
            if text.startswith("Speech service unavailable") or text.startswith("An error occurred"):
              st.warning(text)
              return
            prefix = "🎤 Captured" if source == "mic" else "🎤 Transcribed"
            st.session_state.voice_fill = text
            st.session_state.voice_toast = {'msg': f"{prefix}: {text}", 'ts': _time.time()}
            st.rerun()

          st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
          
          # ── Native browser microphone (Streamlit 1.37+) ──────────────────
          st.caption("Tap the microphone below to record your symptoms:")
          audio_data = st.audio_input("Record symptoms", label_visibility="collapsed")
          if audio_data:
              audio_hash = hash(audio_data.getvalue())
              if st.session_state.get("last_audio_hash") != audio_hash:
                  st.session_state["last_audio_hash"] = audio_hash
                  with st.spinner(get_label('transcribing', st.session_state.language)):
                      text = get_voice_input_from_file(audio_data)
                  _store_voice(text, "mic")

          # ── Voice file upload fallback ─────────────────────────────────────
          st.caption(get_label('voice_backup_caption', st.session_state.language))
          uploaded_audio = st.file_uploader(
              get_label('upload_voice', st.session_state.language),
              type=["wav", "flac"],
              key="voice_upload"
          )
          if uploaded_audio is not None:
              if st.button(get_label('transcribe_btn', st.session_state.language), key="voice_upload_btn"):
                  with st.spinner(get_label('transcribing', st.session_state.language)):
                      text = get_voice_input_from_file(uploaded_audio)
                  _store_voice(text, "file")

          # ── 5-second countdown toast ──────────────────────────────────────
          TOAST_DURATION = 5.0
          toast = st.session_state.voice_toast
          if toast:
              elapsed = _time.time() - toast['ts']
              if elapsed < TOAST_DURATION:
                  pct = max(0.0, 1.0 - elapsed / TOAST_DURATION)
                  st.markdown(f"""
                  <div style="
                      background:linear-gradient(135deg,rgba(0,212,170,0.12),rgba(0,212,170,0.04));
                      border:1px solid rgba(0,212,170,0.38);
                      border-radius:14px; padding:12px 16px 8px; margin-bottom:10px;
                  ">
                      <div style="font-size:0.86rem;color:#00d4aa;font-weight:600;line-height:1.4;">
                          ✅ {toast['msg']}
                      </div>
                      <div style="margin-top:8px;height:3px;
                          background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden;">
                          <div style="height:100%;width:{pct*100:.1f}%;
                              background:linear-gradient(90deg,#00d4aa,#4f8ef7);
                              border-radius:2px;transition:width 0.95s linear;">
                          </div>
                      </div>
                  </div>
                  """, unsafe_allow_html=True)
                  _time.sleep(1.0)
                  st.rerun()
              else:
                  st.session_state.voice_toast = None

          # ── Symptom textarea ──────────────────────────────────────────────
          chip_text = ", ".join(
              s.replace("_", " ") for s in sorted(st.session_state.selected_chips)
          )
          textarea_val = st.session_state.voice_fill or chip_text

          symptom_input = st.text_area(
              get_label('describe_symptoms', st.session_state.language),
              value=textarea_val,
              height=130,
              placeholder=get_label('placeholder_symptoms', st.session_state.language),
          )

          if st.button(get_label('analyze_btn', st.session_state.language), type="primary", key="analyze_btn"):
              combined = symptom_input.strip() or chip_text.strip()
              if combined:
                  st.session_state.voice_toast = None
                  st.session_state.voice_fill  = ''
                  _run_analysis(combined)
              else:
                  st.warning(get_label('no_input', st.session_state.language))

    # ── Right: clickable chip panel
    with col_right:
        with st.container(border=True):
            count = len(st.session_state.selected_chips)
            counter_html = (
                f'<span class="chip-counter">{count} {get_label("selected_count", lang)}</span>'
                if count else ""
            )
            st.markdown(
                f'<div class="panel-title">⚡ {get_label("quick_select", lang)}{counter_html}</div>',
                unsafe_allow_html=True
            )

            for cat_label, symptoms in SYMPTOM_CATEGORIES.items():
                st.markdown(f'<div class="chip-cat">{cat_label}</div>', unsafe_allow_html=True)
                cols = st.columns(3)
                for i, sym in enumerate(symptoms):
                    label = sym.replace("_", " ").title()
                    is_active = sym in st.session_state.selected_chips
                    css_class = "chip-active" if is_active else "chip-btn"
                    with cols[i % 3]:
                        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                        if st.button(
                            f"{'✓ ' if is_active else ''}{label}",
                            key=f"chip_{sym}",
                            use_container_width=True
                        ):
                            if is_active:
                                st.session_state.selected_chips.discard(sym)
                            else:
                                st.session_state.selected_chips.add(sym)
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if st.button("🔍 Analyze Selected →", key="analyze_chips", use_container_width=True, type="primary"):
                if st.session_state.selected_chips:
                    _run_analysis(", ".join(st.session_state.selected_chips))
                else:
                    st.warning("Tap a symptom chip above to select it.")

            if st.session_state.selected_chips:
                if st.button("✕ Clear All", key="clear_chips", use_container_width=True):
                    st.session_state.selected_chips = set()
                    st.rerun()

    # ── Results
    if st.session_state.last_result:
        result = st.session_state.last_result
        disease = result['disease']
        sev_label, sev_color, sev_icon = _get_severity(disease, result.get('low_confidence', False))

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="result-block">', unsafe_allow_html=True)
        r1, r2 = st.columns(2, gap="medium")

        with r1:
            tags_html = "".join(f'<span class="rtag">{t.replace("_"," ")}</span>' for t in result.get('matched', []))
            lang_tag = (
                f'<span style="font-size:0.65rem;color:var(--violet);margin-left:4px;">'
                f'• Detected: {result.get("language","English")}</span>'
            ) if result.get("language") and result.get("language") != "English" else ""

            confidence_html = ""
            if result.get('confidence') is not None:
                confidence_pct = int(round(result['confidence'] * 100))
                confidence_html = (
                    f'<div class="confidence-pill">'
                    f'🔍 Prediction confidence: <strong>{confidence_pct}%</strong>'
                    f'</div>'
                )

            alt_predictions_html = ""
            alternatives = result.get('top_predictions', [])[1:]
            if alternatives:
                alt_predictions_html = '<div style="margin-top:14px;font-size:0.82rem;color:var(--muted);">'
                alt_predictions_html += '<strong>Other possible matches:</strong>'
                for alt in alternatives:
                    alt_predictions_html += (
                        f'<div class="alt-pred">{alt["disease"]} '
                        f'({int(round(alt["confidence"] * 100))}% likely)</div>'
                    )
                alt_predictions_html += '</div>'

            low_confidence_html = ""
            if result.get('low_confidence'):
                low_confidence_html = (
                    '<div class="uncertainty-note">'
                    'This prediction is not definitive. Please consult a healthcare professional with your symptoms. '
                    'The model indicates several conditions are similarly likely.'
                    '</div>'
                )

            followup_summary_html = ""
            followup_answers = result.get('followup_answers', {})
            if followup_answers:
              followup_summary_html = '<div style="margin-top:14px;font-size:0.85rem;color:var(--muted);">'
              followup_summary_html += '<strong>Additional details provided:</strong>'
              for prompt, answer in followup_answers.items():
                followup_summary_html += f'<div class="followup-item">• {prompt} {answer}</div>'
              followup_summary_html += '</div>'

            explanation_html = ""
            if result.get('explanation'):
                explanation_html = '<div style="margin-top:8px;font-size:0.82rem;color:var(--muted);">'
                explanation_html += '<strong>Why this result:</strong>'
                for ex in result.get('explanation', []):
                    explanation_html += f'<div class="explain-item">{ex}</div>'
                explanation_html += '</div>'

            st.markdown(f"""
            <div class="result-condition">
                <div class="rlabel" style="color:var(--cyan);">Detected Condition{lang_tag}</div>
                <div class="rvalue">{disease}</div>
                {confidence_html}
                <div style="
                  display:inline-flex; align-items:center; gap:5px;
                  background:rgba(0,0,0,0.25); border:1px solid {sev_color}44;
                  border-radius:8px; padding:4px 12px; margin-top:10px;
                  font-size:0.7rem; font-weight:700; color:{sev_color};
                  letter-spacing:0.8px; text-transform:uppercase;
                ">{sev_icon} {sev_label}</div>
                <div class="rtags">{tags_html}</div>
                {alt_predictions_html}
                {low_confidence_html}
                {followup_summary_html}
            </div>
            """, unsafe_allow_html=True)

        with r2:
            st.markdown(f"""
            <div class="result-advice">
                <div class="rlabel" style="color:var(--blue);">Advisory</div>
                <div style="font-size:0.88rem;line-height:1.75;margin-top:8px;color:var(--text);">
                    {result['advice']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.last_result:
            _render_followup_questions(result)

    disclaimer_text = st.session_state.translator.get_disclaimer(lang)
    st.markdown(f"""
    <div class="disc">
        <strong>⚠️ {get_label('disclaimer', lang)}:</strong>
        {disclaimer_text}
    </div>
    """, unsafe_allow_html=True)


# ── Follow-up questions helper ─────────────────────────────────────────────────
def _render_followup_questions(result):
    followups = get_followup_questions(result.get('matched', []))
    if not followups:
        return

    with st.expander('📝 Follow-up Questions', expanded=True):
        st.markdown(
            '<div style="color:#e2eeff;margin-bottom:10px;">Answer these extra questions to help your healthcare provider get better context.</div>',
            unsafe_allow_html=True
        )
        for symptom, questions in followups.items():
            st.markdown(f"<div style='font-weight:700;margin-top:12px;color:#00d4aa;'>{symptom.replace('_',' ').title()}</div>", unsafe_allow_html=True)
            for idx, (prompt, input_type, extra) in enumerate(questions):
                key = f"followup_{symptom}_{idx}"
                if input_type == 'text':
                    st.text_input(prompt, key=key)
                elif input_type == 'number':
                    st.number_input(prompt, min_value=0, max_value=100, key=key)
                elif input_type == 'select' and isinstance(extra, list):
                    st.selectbox(prompt, options=extra, key=key)
        if st.button('🔄 Re-run diagnostic with follow-up details', type='primary', key='followup_rerun'):
            _rerun_with_followup(result)


# ── Tab 2: Medicine Reminders ─────────────────────────────────────────────────
def show_medicine_reminders():
    st.markdown('<div class="sec-title">Medicine Reminders</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        with st.container(border=True):
            st.markdown('<div class="panel-title">＋ Add New Reminder</div>', unsafe_allow_html=True)
            with st.form("add_reminder_form"):
                med_name = st.text_input("Medicine Name", placeholder="e.g. Metformin 500mg")
                med_dose = st.text_input("Dosage (optional)", placeholder="e.g. 1 tablet")

                st.markdown(
                    '<div style="font-size:0.7rem;font-weight:700;letter-spacing:1.2px;'
                    'text-transform:uppercase;color:#546785;margin:10px 0 8px;">'
                    'Scheduled Time</div>',
                    unsafe_allow_html=True
                )
                tc1, tc2, tc3 = st.columns([2, 2, 2])
                with tc1:
                    hour_12 = st.selectbox(
                        "Hour",
                        options=list(range(1, 13)),
                        index=7,
                        format_func=lambda h: f"{h:02d}",
                        key="rem_hour"
                    )
                with tc2:
                    minute = st.selectbox(
                        "Minute",
                        options=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
                        format_func=lambda m: f":{m:02d}",
                        key="rem_min"
                    )
                with tc3:
                    period = st.selectbox(
                        "AM / PM",
                        options=["AM", "PM"],
                        key="rem_period"
                    )

                med_notes = st.text_input("Notes (optional)", placeholder="e.g. Take after food")
                submitted = st.form_submit_button("💊 Set Reminder", use_container_width=True)
                if submitted:
                    hour_24 = (hour_12 % 12) + (12 if period == "PM" else 0)
                    time_24 = f"{hour_24:02d}:{minute:02d}"
                    if med_name.strip():
                        st.session_state.reminder_system.add_reminder(
                            med_name.strip(),
                            time_24,
                            dosage=med_dose.strip(),
                            notes=med_notes.strip(),
                        )
                        st.success(f"✅ Reminder set for **{med_name.strip()}**")
                        st.rerun()
                    else:
                        st.error("Please enter a medicine name.")

    with col2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">📅 Today\'s Schedule</div>', unsafe_allow_html=True)
            reminders = st.session_state.reminder_system.get_reminders()
            if reminders:
                for rem in reminders:
                    display_t = st.session_state.reminder_system.get_display_time(rem['time'])
                    dosage_text = f" · {rem['dosage']}" if rem.get('dosage') else ""
                    ra, rb = st.columns([6, 1])
                    with ra:
                        st.markdown(f"""
                        <div class="rem-item">
                            <div class="rem-time">⏰ {display_t}</div>
                            <div class="rem-name">💊 {rem['medicine_name']}<span style="font-size:0.78rem;color:var(--muted);">{dosage_text}</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                    with rb:
                        st.markdown("<div style='margin-top:6px'>", unsafe_allow_html=True)
                        if st.button("✕", key=f"del_{rem['id']}"):
                            st.session_state.reminder_system.delete_reminder(rem['id'])
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="empty-state">
                    <span class="e-icon">💊</span>
                    <div class="e-title">No reminders yet</div>
                    <div class="e-sub">Add your first medicine reminder on the left</div>
                </div>
                """, unsafe_allow_html=True)


# ── Tab 3: Dashboard ──────────────────────────────────────────────────────────
def show_dashboard():
    import matplotlib.pyplot as plt

    st.markdown('<div class="sec-title">Health Dashboard</div>', unsafe_allow_html=True)

    stats = st.session_state.reminder_system.get_statistics()
    rate  = stats.get('adherence_rate', 0.0)
    total = stats.get('total_reminders', 0)
    taken = stats.get('total_taken', 0)
    missed = stats.get('total_missed', 0)

    m1, m2, m3, m4 = st.columns(4, gap="medium")
    for col, icon, val, lbl in [
        (m1, "📋", total,           "Active Reminders"),
        (m2, "✅", taken,           "Doses Taken"),
        (m3, "⚠️", missed,          "Doses Missed"),
        (m4, "📈", f"{rate:.1f}%",  "Adherence Rate"),
    ]:
        with col:
            st.markdown(f"""
            <div class="mcard">
                <span class="mcard-icon">{icon}</span>
                <div class="mcard-val">{val}</div>
                <div class="mcard-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    d_col, b_col = st.columns([1, 2], gap="large")

    with d_col:
        fig, ax = plt.subplots(figsize=(3.2, 3.2), subplot_kw=dict(aspect='equal'))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        done = min(rate, 100)
        left = max(100 - rate, 0)
        ax.pie([done, left], colors=['#00d4aa', '#0d1e35'], startangle=90,
               wedgeprops=dict(width=0.40, edgecolor='none'), counterclock=False)
        ax.text(0,  0.08, f"{rate:.0f}%", ha='center', va='center',
                fontsize=22, fontweight='bold', color='#00d4aa', fontfamily='DejaVu Sans')
        ax.text(0, -0.22, "adherence", ha='center', va='center',
                fontsize=7, color='#546785', fontfamily='DejaVu Sans')
        ax.axis('off')
        plt.tight_layout(pad=0)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with b_col:
        bar_color  = "#00d4aa" if rate >= 70 else "#f59e0b" if rate >= 40 else "#f43f5e"
        status_msg = ("🟢 Excellent — keep it up!" if rate >= 70
                      else "🟡 Good, room to improve" if rate >= 40
                      else "🔴 Try to stay consistent")
        st.markdown(f"""
        <div class="gpanel">
          <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
            <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.85rem;color:#e2eeff;">
              Overall Adherence
            </span>
            <span style="color:{bar_color};font-weight:800;font-size:0.92rem;">{rate:.1f}%</span>
          </div>
          <div style="background:#0a1628;border-radius:10px;height:13px;overflow:hidden;
                      box-shadow:inset 0 2px 6px rgba(0,0,0,0.5);">
            <div style="width:{rate}%;height:100%;
                        background:linear-gradient(90deg,{bar_color}99,{bar_color});
                        border-radius:10px;box-shadow:0 0 14px {bar_color}66;
                        transition:width 1s ease;"></div>
          </div>
          <div style="margin-top:10px;font-size:0.78rem;color:#546785;">{status_msg}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:18px;">
            <div style="background:rgba(0,212,170,0.06);border:1px solid rgba(0,212,170,0.14);
                        border-radius:12px;padding:16px;text-align:center;">
              <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#00d4aa;">{taken}</div>
              <div style="font-size:0.65rem;color:#546785;text-transform:uppercase;letter-spacing:1px;margin-top:4px;">Taken</div>
            </div>
            <div style="background:rgba(244,63,94,0.06);border:1px solid rgba(244,63,94,0.14);
                        border-radius:12px;padding:16px;text-align:center;">
              <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#f43f5e;">{missed}</div>
              <div style="font-size:0.65rem;color:#546785;text-transform:uppercase;letter-spacing:1px;margin-top:4px;">Missed</div>
            </div>
            <div style="background:rgba(79,142,247,0.06);border:1px solid rgba(79,142,247,0.14);
                        border-radius:12px;padding:16px;text-align:center;">
              <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#4f8ef7;">{total}</div>
              <div style="font-size:0.65rem;color:#546785;text-transform:uppercase;letter-spacing:1px;margin-top:4px;">Scheduled</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ── Diet Planner ──────────────────────────────────────────────────────────────
def show_diet_planner():
    lang = st.session_state.get('language', 'en')
    st.markdown(f'<div class="sec-title">{get_label("tab_diet", lang)}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="panel-title">🥗 Diet Planner</div>', unsafe_allow_html=True)
        condition = st.text_input(
            get_label('disease', lang),
            value=(st.session_state.last_result['disease'] if st.session_state.last_result else ''),
            placeholder='e.g. Diabetes, Pneumonia, Hepatitis B',
            key='diet_condition'
        )

        if condition.strip():
            diet = get_diet_advice(condition.strip())
            exact_match = condition.strip() in DIET_ADVICE
            if not exact_match:
                st.info('Showing general healthy diet guidance because this condition is not in the built-in list.', icon='ℹ️')

            st.markdown(f"""
            <div style='margin-top:18px;'>
              <div class='rlabel' style='color:var(--cyan);'>Diet Advice for {condition.strip()}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px;">', unsafe_allow_html=True)
            st.markdown('<div class="gpanel"><div class="rlabel" style="color:var(--blue);">Eat</div>', unsafe_allow_html=True)
            for item in diet['eat']:
                st.markdown(f'<div style="margin:4px 0;">• {item}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="gpanel"><div class="rlabel" style="color:var(--rose);">Avoid</div>', unsafe_allow_html=True)
            for item in diet['avoid']:
                st.markdown(f'<div style="margin:4px 0;">• {item}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info('Analyze your symptoms first or enter a condition to get diet recommendations.', icon='ℹ️')


# ── Appointment Finder ───────────────────────────────────────────────────────
def show_appointment_finder():
    lang = st.session_state.get('language', 'en')
    st.markdown(f'<div class="sec-title">{get_label("tab_appointment", lang)}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="panel-title">📅 Doctor Finder</div>', unsafe_allow_html=True)
        location = st.text_input('Enter your city or locality', placeholder='e.g. Bangalore, India', key='doctor_location')

        if st.button('Search nearby doctors', type='primary', use_container_width=True, key='search_doctors_btn'):
            if location.strip():
                info = get_nearby_doctors_info(location.strip())
                st.success(f'Doctor search ready for {info["location_query"]}')
                if info.get('coordinates'):
                    lat, lon = info['coordinates']
                    st.markdown(f'**Detected coordinates:** {lat:.5f}, {lon:.5f}')
                st.markdown(f"[Open doctor search in Google Maps]({info['doctors_search_url']})")
            else:
                st.warning(get_label('no_input', lang))


# ── Tab 6: About ──────────────────────────────────────────────────────────────
def show_about():
    st.markdown('<div class="sec-title">About MediSense</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="gpanel" style="margin-bottom:22px;">
        <div style="font-family:'Syne',sans-serif;font-size:1.55rem;font-weight:800;
                    margin-bottom:12px;color:#e2eeff;letter-spacing:-0.5px;">
            Smart Health Advisory System
        </div>
        <div style="color:#546785;font-size:0.9rem;line-height:1.85;max-width:640px;">
            An AI-powered multilingual health tool built to help communities — especially
            in rural and low-connectivity areas — understand symptoms, receive basic health
            guidance, and manage their medications through an intuitive, accessible interface.
        </div>
        <div style="margin-top:20px;display:flex;gap:10px;flex-wrap:wrap;">
            <span style="background:rgba(0,212,170,0.09);border:1px solid rgba(0,212,170,0.22);
                         color:#00d4aa;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;
                         text-transform:uppercase;padding:5px 14px;border-radius:9px;">
                Malnad College of Engineering
            </span>
            <span style="background:rgba(79,142,247,0.09);border:1px solid rgba(79,142,247,0.22);
                         color:#4f8ef7;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;
                         text-transform:uppercase;padding:5px 14px;border-radius:9px;">
                Interdisciplinary Project
            </span>
            <span style="background:rgba(167,139,250,0.09);border:1px solid rgba(167,139,250,0.22);
                         color:#a78bfa;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;
                         text-transform:uppercase;padding:5px 14px;border-radius:9px;">
                41 Diseases · 132 Symptoms
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("🩺", "Symptom Analysis",   "ML-powered disease prediction across 41 conditions and 132 symptoms"),
        ("🌐", "Multilingual",       "English, Hindi & Kannada — auto-detected, auto-translated"),
        ("🎤", "Voice Input",        "Hands-free symptom entry via speech recognition"),
        ("💊", "Smart Reminders",    "Persistent medicine scheduling with SQLite-backed storage"),
        ("🥗", "Diet Planner",       "Condition-specific nutritional guidance for recovery and wellness"),
        ("📅", "Doctor Finder",      "Local doctor search links with Google Maps support"),
        ("📊", "Live Dashboard",     "Animated adherence donut, 4 KPI cards & progress tracking"),
        ("🔒", "Privacy-first",      "All data stored locally — zero cloud dependency, zero tracking"),
    ]

    c1, c2, c3 = st.columns(3, gap="medium")
    for i, (icon, title, desc) in enumerate(features):
        with [c1, c2, c3][i % 3]:
            st.markdown(f"""
            <div class="feat-card" style="margin-bottom:16px;">
                <div class="feat-icon">{icon}</div>
                <div class="feat-title">{title}</div>
                <div class="feat-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="gpanel" style="margin-bottom:22px;">
      <div class="panel-title">✨ What's New</div>
      <ul style="margin:0;padding-left:18px;color:#dbeafe;line-height:1.7;font-size:0.92rem;">
        <li>Model probabilities calibrated for safer confidence reporting.</li>
        <li>Low-confidence warnings and transparent reasoning added.</li>
        <li>Version badge added to the hero panel.</li>
        <li>README updated with retraining workflow.</li>
      </ul>
    </div>
    <div class="gpanel">
      <div class="panel-title">🛠️ Tech Stack</div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <span style="background:rgba(0,212,170,0.07);border:1px solid rgba(0,212,170,0.18);
                     color:#00d4aa;padding:6px 16px;border-radius:10px;font-size:0.78rem;font-weight:600;">
          Python
        </span>
        <span style="background:rgba(79,142,247,0.07);border:1px solid rgba(79,142,247,0.18);
                     color:#4f8ef7;padding:6px 16px;border-radius:10px;font-size:0.78rem;font-weight:600;">
          Streamlit
        </span>
        <span style="background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.18);
                     color:#f59e0b;padding:6px 16px;border-radius:10px;font-size:0.78rem;font-weight:600;">
          scikit-learn · Decision Tree
        </span>
        <span style="background:rgba(167,139,250,0.07);border:1px solid rgba(167,139,250,0.18);
                     color:#a78bfa;padding:6px 16px;border-radius:10px;font-size:0.78rem;font-weight:600;">
          SQLite · pandas · matplotlib
        </span>
        <span style="background:rgba(244,63,94,0.07);border:1px solid rgba(244,63,94,0.18);
                     color:#f43f5e;padding:6px 16px;border-radius:10px;font-size:0.78rem;font-weight:600;">
          googletrans · SpeechRecognition
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Alarm / notification system ──────────────────────────────────────────────
def inject_alarm_system(reminders):
    """Inject JS that checks time every 30s and rings + notifies for due medicines."""
    import json
    from datetime import datetime
    import streamlit.components.v1 as components

    rem_list = [{"time": r["time"], "name": r["medicine_name"].encode('utf-8', errors='replace').decode('utf-8')} for r in reminders]
    rem_json = json.dumps(rem_list, ensure_ascii=True)

    now = datetime.now()
    current_hhmm = now.strftime("%H:%M")
    today_key = now.strftime("%Y-%m-%d")

    for rem in reminders:
        key = f"{today_key}|{rem['time']}|{rem['medicine_name']}"
        if rem["time"] == current_hhmm and key not in st.session_state.alarm_dismissed:
            st.session_state.alarm_dismissed.add(key)
            st.toast(f"💊 Time to take **{rem['medicine_name']}**!", icon="🔔")

    components.html(f"""
    <script>
    (function() {{
      var TARGET = window.parent || window;
      if (TARGET._mediSenseAlarmRunning) return;
      TARGET._mediSenseAlarmRunning = true;

      var reminders = {rem_json};

      function playChime() {{
        try {{
          var AudioCtx = window.AudioContext || window.webkitAudioContext;
          if (!AudioCtx) return;
          var ctx = new AudioCtx();
          if (ctx.state === 'suspended') ctx.resume();
          var notes = [523.25, 659.25, 783.99, 1046.5];
          notes.forEach(function(freq, i) {{
            var osc  = ctx.createOscillator();
            var gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, ctx.currentTime);
            gain.gain.setValueAtTime(0,    ctx.currentTime + i * 0.22);
            gain.gain.linearRampToValueAtTime(0.5,   ctx.currentTime + i * 0.22 + 0.06);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.22 + 0.65);
            osc.start(ctx.currentTime + i * 0.22);
            osc.stop(ctx.currentTime  + i * 0.22 + 0.7);
          }});
        }} catch(e) {{ console.warn('Chime error:', e); }}
      }}

      function sendNotification(name) {{
        if (!("Notification" in window)) return;
        if (Notification.permission === "granted") {{
          new Notification("MediSense Reminder", {{
            body: "Time to take: " + name,
            tag:  "medisense-" + name,
            requireInteraction: true
          }});
        }} else if (Notification.permission !== "denied") {{
          Notification.requestPermission().then(function(p) {{
            if (p === "granted") sendNotification(name);
          }});
        }}
      }}

      function showBanner(name) {{
        var doc = window.parent.document;
        var existing = doc.getElementById('ms-alarm-banner');
        if (existing) existing.remove();
        var banner = doc.createElement('div');
        banner.id = 'ms-alarm-banner';
        banner.innerHTML =
          '<style>' +
          '@keyframes msSlideIn {{ from {{ opacity:0;transform:translateX(-50%) translateY(-28px); }} to {{ opacity:1;transform:translateX(-50%) translateY(0); }} }}' +
          '@keyframes msPulse {{ 0%,100% {{ box-shadow:0 0 40px rgba(0,212,170,0.45),0 8px 40px rgba(0,0,0,0.7); }} 50% {{ box-shadow:0 0 72px rgba(0,212,170,0.80),0 8px 40px rgba(0,0,0,0.7); }} }}' +
          '#ms-alarm-banner .ms-inner {{ animation: msSlideIn 0.4s cubic-bezier(.22,1,.36,1) both, msPulse 1.8s ease-in-out 0.5s infinite; }}' +
          '</style>' +
          '<div class="ms-inner" style="position:fixed;top:18px;left:50%;transform:translateX(-50%);z-index:999999;min-width:320px;max-width:520px;background:linear-gradient(135deg,#0a2a1e,#051424);border:2px solid #00d4aa;border-radius:18px;padding:18px 24px 16px;box-shadow:0 0 40px rgba(0,212,170,0.45),0 8px 40px rgba(0,0,0,0.7);font-family:system-ui,sans-serif;">' +
          '<div style="display:flex;align-items:center;gap:14px;">' +
          '<span style="font-size:2rem;">&#128276;</span>' +
          '<div style="flex:1;">' +
          '<div style="font-size:0.65rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#00d4aa;margin-bottom:4px;">Medicine Reminder</div>' +
          '<div style="font-size:1.05rem;font-weight:700;color:#e2eeff;">Time to take <span style="color:#00d4aa;">' + name + '</span></div>' +
          '</div>' +
          '<button onclick="document.getElementById(\'ms-alarm-banner\').remove()" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);border-radius:10px;color:#5a7194;cursor:pointer;font-size:1rem;padding:6px 12px;" onmouseover="this.style.borderColor=\'#f43f5e\';this.style.color=\'#f43f5e\';" onmouseout="this.style.borderColor=\'rgba(255,255,255,0.15)\';this.style.color=\'#5a7194\';">&#x2715;</button>' +
          '</div></div>';
        doc.body.appendChild(banner);
        setTimeout(function() {{
          var b = doc.getElementById('ms-alarm-banner');
          if (b) b.remove();
        }}, 60000);
      }}

      if ("Notification" in window && Notification.permission === "default") {{
        setTimeout(function() {{ Notification.requestPermission(); }}, 1500);
      }}

      TARGET._msFired = TARGET._msFired || {{}};

      function checkReminders() {{
        var now   = new Date();
        var hhmm  = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
        var today = now.toISOString().slice(0,10);
        reminders.forEach(function(rem) {{
          var key = today + '|' + rem.time + '|' + rem.name;
          if (rem.time === hhmm && !TARGET._msFired[key]) {{
            TARGET._msFired[key] = true;
            playChime();
            sendNotification(rem.name);
            showBanner(rem.name);
          }}
        }});
      }}

      checkReminders();
      setInterval(checkReminders, 30000);
    }})();
    </script>
    """, height=0)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    _init_state()

    lang = st.session_state.get('language', 'en')

    all_reminders = st.session_state.reminder_system.get_reminders()
    inject_alarm_system(all_reminders)

    # FIX: use f-string so TOTAL_QUICK_CHIPS and APP_VERSION interpolate correctly
    st.markdown(f"""
    <div class="hero">
        <div class="hero-corner"></div>
        <div class="hero-eyebrow">
            <span class="live-dot"></span>
            AI-Powered Health Advisory System
        </div>
        <div class="hero-title">MediSense</div>
        <div class="hero-sub">
            Understand symptoms. Manage medications. Stay informed.
            <br>Built for everyone, in every language.
        </div>
        <div class="hero-badge-row">
            <div class="hero-badge"><span>🧠</span>ML Diagnosis</div>
            <div class="hero-badge"><span>🌐</span>3 Languages</div>
            <div class="hero-badge"><span>🎤</span>Voice Ready</div>
            <div class="hero-badge"><span>⚡</span>{TOTAL_QUICK_CHIPS} Quick-Select Chips</div>
            <div class="hero-badge"><span>📱</span>Mobile Friendly</div>
            <div class="hero-badge"><span>🏷️</span>{APP_VERSION} Release</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        get_label('tab_analyzer', lang),
        get_label('tab_reminders', lang),
        get_label('tab_dashboard', lang),
        get_label('tab_diet', lang),
        get_label('tab_appointment', lang),
        get_label('tab_about', lang),
    ])
    with tab1:
        show_symptom_analyzer()
    with tab2:
        show_medicine_reminders()
    with tab3:
        show_dashboard()
    with tab4:
        show_diet_planner()
    with tab5:
        show_appointment_finder()
    with tab6:
        show_about()

    # FIX: use f-string so APP_VERSION interpolates in footer
    st.markdown(f"""
    <div class="footer">
        Built with ❤️ at <span class="hl">Malnad College of Engineering</span> ·
        Powered by <span class="hl">Streamlit</span> &amp;
        <span class="hl">Machine Learning</span> ·
        <span class="hl">MediSense {APP_VERSION}</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()