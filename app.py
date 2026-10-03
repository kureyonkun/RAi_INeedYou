import time

import requests
import streamlit as st

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
DEFAULT_MESSAGE = "🔴 The big red button was pressed!"
MAX_CHARS = 140
COOLDOWN_SECONDS = 10

st.set_page_config(page_title="Big Red Button", page_icon="🔴", layout="centered")

st.markdown(
    """
    <style>
    /* Hide the empty block this <style> tag lives in */
    .stElementContainer:has(style) {
        display: none;
    }

    /* Even top/bottom padding so the page's center is the screen's center */
    .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 3.5rem !important;
        padding-bottom: 3.5rem !important;
    }

    /* Three rows (message / button / note). The equal outer rows keep the
       button dead center; on small screens the page simply scrolls. */
    .st-key-stage {
        --btn: clamp(190px, 62vw, 260px);
        display: grid !important;
        grid-template-rows: 1fr auto 1fr;
        row-gap: 2.5rem;
        min-height: calc(100vh - 7rem);
        min-height: calc(100dvh - 7rem);
        overflow-x: clip;
    }

    .st-key-stage > * {
        width: 100%;
    }

    .st-key-stage > :first-child {
        align-self: end;
    }

    .st-key-stage > :last-child {
        align-self: start;
    }

    .st-key-above,
    .st-key-below {
        width: min(560px, 100%) !important;
        margin: 0 auto;
    }

    /* 16px stops iPhones from zooming in when the box is tapped */
    .st-key-above textarea {
        font-size: 16px !important;
        line-height: 1.5 !important;
    }

    .st-key-below {
        padding-top: 0.75rem;
    }

    .st-key-below .note {
        text-align: center;
        font-size: 0.95rem;
        line-height: 1.5;
        opacity: 0.8;
        font-style: italic;
        margin: 0;
    }

    .st-key-btnwrap {
        position: relative;
        align-items: center;
    }

    .st-key-big_red {
        display: flex;
        justify-content: center;
    }

    /* The big red button itself */
    .st-key-big_red button {
        width: var(--btn);
        height: var(--btn);
        border-radius: 50% !important;
        border: 6px solid #7a0000 !important;
        background: radial-gradient(circle at 35% 30%, #ff6b6b 0%, #e60000 45%, #a30000 100%) !important;
        color: #fff !important;
        box-shadow:
            0 14px 0 #6b0000,
            0 22px 30px rgba(0, 0, 0, 0.45),
            inset 0 -10px 20px rgba(0, 0, 0, 0.25);
        transform: translateY(0);
        transition: transform 0.08s ease-out, box-shadow 0.08s ease-out, filter 0.2s;
        animation: pulse 2.2s ease-in-out infinite;
        cursor: pointer;
        user-select: none;
        -webkit-tap-highlight-color: transparent;
    }

    .st-key-big_red button p {
        font-size: clamp(1.35rem, 6.5vw, 1.9rem) !important;
        font-weight: 900 !important;
        line-height: 1.2;
        letter-spacing: 0.04em;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
    }

    .st-key-big_red button:hover {
        filter: brightness(1.08);
    }

    .st-key-big_red button:focus,
    .st-key-big_red button:focus-visible {
        outline: none !important;
        color: #fff !important;
    }

    /* Pressed: sinks down, shadow collapses, glow flashes */
    .st-key-big_red button:active {
        transform: translateY(12px) scale(0.97);
        box-shadow:
            0 2px 0 #6b0000,
            0 4px 10px rgba(0, 0, 0, 0.4),
            inset 0 8px 20px rgba(0, 0, 0, 0.35),
            0 0 60px 20px rgba(255, 40, 40, 0.6);
        animation: none;
    }

    @keyframes pulse {
        0%, 100% {
            box-shadow:
                0 14px 0 #6b0000,
                0 22px 30px rgba(0, 0, 0, 0.45),
                inset 0 -10px 20px rgba(0, 0, 0, 0.25),
                0 0 0 0 rgba(255, 0, 0, 0.5);
        }
        50% {
            box-shadow:
                0 14px 0 #6b0000,
                0 22px 30px rgba(0, 0, 0, 0.45),
                inset 0 -10px 20px rgba(0, 0, 0, 0.25),
                0 0 0 22px rgba(255, 0, 0, 0);
        }
    }

    /* Shockwave ring shown once after a successful send */
    .st-key-btnwrap .stElementContainer:has(.shockwave) {
        position: absolute;
        inset: 0;
        pointer-events: none;
    }

    .shockwave {
        position: absolute;
        left: 50%;
        top: 50%;
        width: var(--btn);
        height: var(--btn);
        border-radius: 50%;
        border: 6px solid rgba(255, 30, 30, 0.8);
        pointer-events: none;
        animation: shock 0.9s ease-out forwards;
        z-index: 9999;
    }

    @keyframes shock {
        from { transform: translate(-50%, -50%) scale(0.8); opacity: 1; }
        to   { transform: translate(-50%, -50%) scale(3.5); opacity: 0; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def send_pushover(message: str) -> tuple[bool, str]:
    try:
        resp = requests.post(
            PUSHOVER_URL,
            data={
                "token": st.secrets["PUSHOVER_TOKEN"],
                "user": st.secrets["PUSHOVER_USER"],
                "title": "Big Red Button",
                "message": message,
            },
            timeout=10,
        )
    except KeyError:
        return False, "Pushover keys are missing from Streamlit secrets."
    except requests.RequestException as exc:
        return False, f"Network error: {exc}"

    if resp.ok:
        return True, "Notification sent!"
    try:
        errors = ", ".join(resp.json().get("errors", [])) or resp.text
    except ValueError:
        errors = resp.text
    return False, f"Pushover error: {errors}"


def on_press():
    now = time.time()
    remaining = COOLDOWN_SECONDS - (now - st.session_state.get("last_sent", 0))
    if remaining > 0:
        st.session_state.result = (False, f"Easy there! Wait {int(remaining) + 1}s before pressing again.")
        return

    message = st.session_state.get("message", "").strip()[:MAX_CHARS] or DEFAULT_MESSAGE
    ok, info = send_pushover(message)
    st.session_state.result = (ok, info)
    if ok:
        st.session_state.last_sent = now
        st.session_state.message = ""  # clear the textbox after a successful send


result = st.session_state.pop("result", None)

with st.container(key="stage"):
    with st.container(key="above"):
        st.text_area(
            "Name and Message (optional)",
            key="message",
            max_chars=MAX_CHARS,
            height=110,  # roughly three lines
            placeholder="Add a short message with your name so RAi knows who to get back to.",
        )

    with st.container(key="btnwrap"):
        st.button("RAi, I need you!", key="big_red", on_click=on_press)
        if result and result[0]:
            st.markdown('<div class="shockwave"></div>', unsafe_allow_html=True)

    with st.container(key="below"):
        st.markdown(
            '<p class="note">RAi intentionally stays off social media and messaging apps. '
            "But if you know about this page, it means you're important to him, and he "
            "wants you to use this button whenever you need him. So go ahead and press it! 😊</p>",
            unsafe_allow_html=True,
        )

if result:
    ok, info = result
    st.toast(info, icon="✅" if ok else "⚠️")
