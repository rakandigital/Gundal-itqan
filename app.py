import streamlit as st
import pandas as pd
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(page_title="Gundal Itqan", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #f8fafc; }

.landing { text-align:center; margin-top:5px; }
.landing p { color:#475569; }

.sticky-header {
    position: fixed; top: 0; left: 0; width: 100%;
    background: white; padding: 70px 0 20px;
    border-bottom: 1px solid #e2e8f0; z-index: 1000;
    text-align: center;
}
.header-title {
    color:#059669; font-size:1.2rem; font-weight:700;
    text-transform:uppercase; letter-spacing:0.08em;
}
.header-context {
    font-size:1.1rem; font-weight:700; color:#0f172a;
}

.content-area { margin-top:30px; }

div.stButton > button:first-child {
    position: fixed; bottom: 50px; right:25px;
    width: 200px; height: 100px; border-radius: 5%;
    background-color: #10b981 !important; color: white !important;
    font-size: 26px !important; z-index: 99999; border: none !important;
    box-shadow: 0 4px 15px rgba(16,185,129,0.4);
}

.footer {
    text-align:center; color:#94a3b8; font-size:0.75rem;
    margin-top:30px; padding:15px; border-top:1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# ================= DATA =================
@st.cache_data
def load_surah():
    df = pd.read_csv("surah_list.csv")
    return df.sort_values("surah_no")

surah_df = load_surah()

# ================= STATE =================
def init_state():
    defaults = {
        "page": "landing",
        "user_name": "",
        "surah_display": "",
        "surah_name": "",
        "total_ayat": 0,
        "ayah": 1,
        "set_no": 1,
        "progress": {"read":[False]*5, "recite":[False]*5},
        "recap": {"read":[False]*5, "recite":[False]*5, "active": False},
        "logs": []
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ================= LOG =================
def log(action):
    st.session_state.logs.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Nama": st.session_state.user_name,
        "Surah": st.session_state.surah_name,
        "Ayat": st.session_state.ayah,
        "Set": st.session_state.set_no,
        "Aktiviti": action
    })

# ================= LANDING =================
if st.session_state.page == "landing":
    st.markdown("""
    <div class="landing">
        <h1>Gundal Itqan</h1>
        <p>Alat bantuan hafazan al Quran melalui pengulangan sedar dan berperingkat.</p>
        <p><em>Istiqomah. Biar usahanya kecil, asalkan ia berterusan.</em></p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "Sila sediakan mushaf al Quran sebelum memulakan sesi ini. "
        "Gundal Itqan berfungsi sebagai panduan ulangan dan rekod perjalanan hafazan anda, "
        "bukan sebagai gantian mushaf."
    )

    name = st.text_input("Nama anda")
    choice = st.selectbox("Pilih Surah", surah_df["surah_display"])
    row = surah_df[surah_df["surah_display"] == choice].iloc[0]

    st.session_state.surah_display = row["surah_display"]
    st.session_state.surah_name = row["surah_name"]
    st.session_state.total_ayat = int(row["total_ayat"])

    ayat = st.number_input("Ayat permulaan", 1, st.session_state.total_ayat, 1)

    if st.button("Mulakan Hafazan", use_container_width=True):
        if name.strip():
            st.session_state.user_name = name
            st.session_state.ayah = ayat
            st.session_state.page = "hafaz"
            st.rerun()

# ================= HAFAZ =================
elif st.session_state.page == "hafaz":

    st.markdown(f"""
    <div class="sticky-header">
        <div class="header-title">{st.session_state.surah_display}</div>
        <div class="header-context">
            Ayat {st.session_state.ayah} • Set {st.session_state.set_no}/10
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    st.info("Sila rujuk mushaf al Quran untuk ayat yang sedang dihafaz.")

    def tracker(data):
        st.write("Tekan butang + setiap satu kali anda habis membaca ayat semasa.")
        row = "display:flex; gap:4px; margin-bottom:6px;"
        box = "flex:1; height:25px; border-radius:4px; border:1px solid #e2e8f0;"

        st.caption("📖 Baca (Buka Mushaf) - Baca dan ulang baca ayat yang ingin dihafaz dengan melihat mushaf.")
        html = f"<div style='{row}'>"
        for x in data["read"]:
            html += f"<div style='{box} background:{'#10b981' if x else '#e2e8f0'}'></div>"
        st.markdown(html + "</div>", unsafe_allow_html=True)

        st.caption("🧠 Hafaz (Tutup Mushaf) - Tutup mushaf dan masa untuk ulang baca tanpa melihat mushaf.")
        html = f"<div style='{row}'>"
        for x in data["recite"]:
            html += f"<div style='{box} background:{'#ffA500' if x else '#e2e8f0'}'></div>"
        st.markdown(html + "</div>", unsafe_allow_html=True)

    if not st.session_state.recap["active"]:
        tracker(st.session_state.progress)

        if st.button("➕", key="btn_plus_progress"):
            for i in range(5):
                if not st.session_state.progress["read"][i]:
                    st.session_state.progress["read"][i] = True
                    log("READ")
                    st.rerun()
            for i in range(5):
                if not st.session_state.progress["recite"][i]:
                    st.session_state.progress["recite"][i] = True
                    log("RECITE")
                    st.rerun()

            if all(st.session_state.progress["read"]) and all(st.session_state.progress["recite"]):
                if st.session_state.set_no < 10:
                    st.session_state.set_no += 1
                    st.session_state.progress = {"read":[False]*5,"recite":[False]*5}
                else:
                    if st.session_state.ayah > 1:
                        st.session_state.recap["active"] = True
                    else:
                        st.session_state.ayah += 1
                        st.session_state.set_no = 1
                        st.session_state.progress = {"read":[False]*5,"recite":[False]*5}
            st.rerun()

    else:
        st.info("✨ Fasa Recap: Sila ulang ayat yang telah dihafaz sebelumnya, bermula dari ayat pertama.")
        tracker(st.session_state.recap)

        if st.button("➕", key="btn_plus_recap"):
            for i in range(5):
                if not st.session_state.recap["read"][i]:
                    st.session_state.recap["read"][i] = True
                    log("RECAP READ")
                    st.rerun()
            for i in range(5):
                if not st.session_state.recap["recite"][i]:
                    st.session_state.recap["recite"][i] = True
                    log("RECAP RECITE")
                    st.rerun()

            if all(st.session_state.recap["read"]) and all(st.session_state.recap["recite"]):
                if st.session_state.ayah < st.session_state.total_ayat:
                    st.session_state.ayah += 1
                    st.session_state.set_no = 1
                    st.session_state.progress = {"read":[False]*5,"recite":[False]*5}
                    st.session_state.recap = {"read":[False]*5,"recite":[False]*5,"active":False}
                else:
                    st.session_state.page = "completed"
            st.rerun()
            
    with st.expander("⏸️ Berhenti & Lihat Progress"):
        if st.session_state.logs:
            df = pd.DataFrame(st.session_state.logs)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Muat Turun Progress",
                csv,
                "gundal_itqan.csv",
                "text/csv"
            )
        else:
            st.write("Belum ada rekod.")
# ================= COMPLETED =================
elif st.session_state.page == "completed":

    st.markdown("""
    <div style="text-align:center; margin-top:60px;">
        <h2>Tahniah 🎉</h2>
        <p>Anda telah menyelesaikan hafazan surah ini.</p>
        <p><em>Semoga Allah memberkati setiap usaha kecil yang istiqamah.</em></p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📊 Lihat & Muat Turun Rekod Hafazan", expanded=True):
        if st.session_state.logs:
            df = pd.DataFrame(st.session_state.logs)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Muat Turun Rekod",
                csv,
                f"gundal_itqan_{st.session_state.surah_name}.csv",
                "text/csv"
            )
        else:
            st.write("Tiada rekod.")

    if st.button("🏠 Kembali ke Utama", use_container_width=False):
        st.session_state.page = "landing"
        st.session_state.ayah = 1
        st.session_state.set_no = 1
        st.session_state.progress = {"read":[False]*5,"recite":[False]*5}
        st.session_state.recap = {"read":[False]*5,"recite":[False]*5,"active":False}
        st.session_state.logs = []
        st.rerun()

# ================= FOOTER =================
st.markdown("""
<div class="footer">
<p>❤️ <b>Gundal Itqan</b></p>
<p><a href="https://www.bizappay.my/q4oVo1RmSN">Support / Sumbangan</a></p>
<p><small>Free Version · Fokus Mushaf</small></p>
</div>
""", unsafe_allow_html=True)