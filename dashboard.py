import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Аналіз конверсії угод — CRM Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px; border-radius: 12px; color: white;
        text-align: center; margin-bottom: 10px;
    }
    .metric-card.green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .metric-card.red   { background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%); }
    .metric-card.gold  { background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%); color: #333; }
    .metric-value { font-size: 2rem; font-weight: 700; }
    .metric-label { font-size: 0.85rem; opacity: 0.9; margin-top: 4px; }
    .section-title {
        font-size: 1.2rem; font-weight: 600; color: #2a5298;
        border-left: 4px solid #2a5298; padding-left: 10px; margin: 22px 0 12px;
    }
    .note { font-size: 0.8rem; color: #888; font-style: italic; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# РЕАЛЬНІ ДАНІ (з Raw Data, 647 закритих угод, Jan–Apr 2024)
# ══════════════════════════════════════════════════════════════════════════

monthly_df = pd.DataFrame({
    "Місяць":   ["Січень 2024", "Лютий 2024", "Березень 2024", "Квітень 2024*"],
    "Виграно":  [39, 81, 86, 10],
    "Програно": [88, 138, 181, 24],
})
monthly_df["Всього"]       = monthly_df["Виграно"] + monthly_df["Програно"]
monthly_df["Win Rate (%)"] = (monthly_df["Виграно"] / monthly_df["Всього"] * 100).round(1)

# CRM — всі з Total >= 5 (реальні дані)
crm_df = pd.DataFrame({
    "CRM": [
        "G-PLUS","ZohoCRM","1C as CRM","Pipedrive","Hubspot","altergio",
        "NetHunt CRM","KeyCRM","KeepinCRM","AmoCRM","Creatio",
        "Custom CRM","No CRM","Bitrix24","Other","Firmao","Onebox","Salesdrive",
        "Microsoft Dynamics",
    ],
    "Виграно":  [2,  6,  4, 11,  5,  2,  7, 28,  6, 15,  4,  8, 76, 16, 10,  1,  1,  3,  0],
    "Програно": [0,  4,  3, 10,  5,  2,  7, 34, 11, 30,  8, 18,185, 43, 27,  3,  3, 14,  3],
})
crm_df["Всього"]       = crm_df["Виграно"] + crm_df["Програно"]
crm_df["Win Rate (%)"] = (crm_df["Виграно"] / crm_df["Всього"] * 100).round(2)
crm_df = crm_df.sort_values("Win Rate (%)", ascending=False).reset_index(drop=True)

# Країни (реальні дані)
country_df = pd.DataFrame({
    "Країна": [
        "SK (Словаччина)","AE (ОАЕ)","US (США)","CY (Кіпр)","IL (Ізраїль)",
        "GE (Грузія)","UA (Україна)","TR (Туреччина)","EE (Естонія)",
        "ES (Іспанія)","PL (Польща)","KZ (Казахстан)",
    ],
    "Виграно":  [1, 2, 6, 1, 2, 4, 156, 1, 1, 1, 22, 19],
    "Програно": [0, 1, 5, 1, 2, 5, 255, 2, 2, 2, 59, 75],
})
country_df["Всього"]       = country_df["Виграно"] + country_df["Програно"]
country_df["Win Rate (%)"] = (country_df["Виграно"] / country_df["Всього"] * 100).round(1)
country_df = country_df.sort_values("Win Rate (%)", ascending=False)

# ══════════════════════════════════════════════════════════════════════════
# HELPER: кольорування без matplotlib
# ══════════════════════════════════════════════════════════════════════════
def color_wr(val):
    if val >= 50:  return "background-color:#d4edda;color:#155724;font-weight:600"
    if val >= 30:  return "background-color:#fff3cd;color:#856404;font-weight:600"
    return "background-color:#f8d7da;color:#721c24;font-weight:600"

def color_vol(val, vmax):
    pct = min(val / vmax, 1.0)
    r = int(173 + (41  - 173)*pct)
    g = int(216 + (128 - 216)*pct)
    b = int(230 + (185 - 230)*pct)
    return f"background-color:rgb({r},{g},{b})"

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("📊 CRM Analytics")
    st.caption("Ringostat · Revenue Operations")
    st.divider()
    st.subheader("🔧 Фільтри")
    min_deals   = st.slider("Мін. угод для CRM:", 1, 60, 5)
    show_no_crm = st.checkbox("Включити 'No CRM'", value=True)
    st.divider()
    st.subheader("📌 Ключові факти")
    st.success("🏆 Пік виграшів: **Березень 2024** (86 угод)")
    st.error("📉 Пік програшів: **Березень 2024** (181 угода)")
    st.info("🌍 Топ Win Rate: **SK (Словаччина)** — 100%")
    st.warning("📋 Всього закрито: **647 угод** (Jan–Apr 2024)")
    st.divider()
    st.caption("Джерело: Raw Data · Ringostat Test Task")

# ══════════════════════════════════════════════════════════════════════════
# ЗАГОЛОВОК
# ══════════════════════════════════════════════════════════════════════════
st.title("📊 Аналіз конверсії та результатів угод")
st.markdown("**Ringostat · Revenue Operations Specialist** · Closed Won / Closed Lost · Січень–Квітень 2024")
st.caption("\\* Квітень 2024 — неповний місяць (дані до 3 квітня)")
st.divider()

# ══════════════════════════════════════════════════════════════════════════
# KPI КАРТКИ
# ══════════════════════════════════════════════════════════════════════════
total_won  = monthly_df["Виграно"].sum()
total_lost = monthly_df["Програно"].sum()
overall_wr = round(total_won / (total_won + total_lost) * 100, 1)
peak_won_month = monthly_df.loc[monthly_df["Виграно"].idxmax(), "Місяць"]
peak_won_val   = monthly_df["Виграно"].max()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card green"><div class="metric-value">{total_won}</div><div class="metric-label">✅ Всього виграно</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card red"><div class="metric-value">{total_lost}</div><div class="metric-label">❌ Всього програно</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{overall_wr}%</div><div class="metric-label">📈 Загальний Win Rate</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card gold"><div class="metric-value">647</div><div class="metric-label">📋 Закрито угод (Jan–Apr)</div></div>', unsafe_allow_html=True)

st.markdown("")

# ══════════════════════════════════════════════════════════════════════════
# РЯДОК 1: Місячна динаміка + таблиця
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📅 Динаміка угод по місяцях (2024)</div>', unsafe_allow_html=True)
col_l, col_r = st.columns([2, 1])

with col_l:
    fig_m = go.Figure()
    fig_m.add_trace(go.Bar(x=monthly_df["Місяць"], y=monthly_df["Виграно"],
                           name="Виграно ✅", marker_color="#27ae60"))
    fig_m.add_trace(go.Bar(x=monthly_df["Місяць"], y=monthly_df["Програно"],
                           name="Програно ❌", marker_color="#e74c3c"))
    fig_m.add_trace(go.Scatter(
        x=monthly_df["Місяць"], y=monthly_df["Win Rate (%)"],
        name="Win Rate (%)", yaxis="y2", mode="lines+markers",
        line=dict(color="#f39c12", width=2.5, dash="dot"), marker=dict(size=8),
    ))
    fig_m.update_layout(
        barmode="group", height=340,
        yaxis=dict(title="Кількість угод", gridcolor="#f0f0f0"),
        yaxis2=dict(title="Win Rate (%)", overlaying="y", side="right",
                    range=[0, 60], showgrid=False),
        legend=dict(orientation="h", y=1.12, x=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=20),
        annotations=[
            dict(x="Березень 2024", y=86, text="🏆 Пік виграшів (86)",
                 showarrow=True, arrowhead=2, ax=0, ay=-35,
                 font=dict(color="#27ae60", size=11)),
            dict(x="Березень 2024", y=181, text="⚠️ Пік програшів (181)",
                 showarrow=True, arrowhead=2, ax=60, ay=-30,
                 font=dict(color="#e74c3c", size=11)),
        ]
    )
    st.plotly_chart(fig_m, use_container_width=True)

with col_r:
    st.markdown('<div class="section-title" style="margin-top:0">📋 Місячна таблиця</div>', unsafe_allow_html=True)
    styled_m = (
        monthly_df[["Місяць","Виграно","Програно","Всього","Win Rate (%)"]].style
        .applymap(color_wr, subset=["Win Rate (%)"])
        .format({"Win Rate (%)": "{:.1f}%"})
    )
    st.dataframe(styled_m, use_container_width=True, height=210)
    st.markdown('<p class="note">* Квітень 2024 — дані до 3 квітня (неповний місяць)</p>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# РЯДОК 2: CRM бар + таблиця
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🖥️ Win Rate за CRM клієнта</div>', unsafe_allow_html=True)

filtered = crm_df[crm_df["Всього"] >= min_deals].copy()
if not show_no_crm:
    filtered = filtered[filtered["CRM"] != "No CRM"]

col_chart, col_table = st.columns([1.4, 1])

with col_chart:
    bar_colors = ["#27ae60" if v >= 50 else "#f39c12" if v >= 30 else "#e74c3c"
                  for v in filtered["Win Rate (%)"]]
    fig_c = go.Figure(go.Bar(
        x=filtered["Win Rate (%)"], y=filtered["CRM"], orientation="h",
        marker_color=bar_colors,
        text=[f"{v:.1f}%" for v in filtered["Win Rate (%)"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Win Rate: %{x:.1f}%<extra></extra>",
    ))
    fig_c.add_vline(x=50, line_dash="dash", line_color="#555",
                    annotation_text="50% поріг", annotation_position="top right")
    fig_c.update_layout(
        height=500,
        xaxis=dict(title="Win Rate (%)", range=[0, 130], gridcolor="#f0f0f0"),
        yaxis=dict(title=""),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=80, t=10, b=20),
    )
    st.plotly_chart(fig_c, use_container_width=True)
    st.markdown('<p class="note">🟢 ≥50% &nbsp;|&nbsp; 🟡 30–49% &nbsp;|&nbsp; 🔴 &lt;30%</p>', unsafe_allow_html=True)

with col_table:
    max_all = filtered["Всього"].max()
    styled_c = (
        filtered[["CRM","Виграно","Програно","Всього","Win Rate (%)"]].style
        .applymap(color_wr, subset=["Win Rate (%)"])
        .applymap(lambda v: color_vol(v, max_all), subset=["Всього"])
        .format({"Win Rate (%)": "{:.2f}%"})
    )
    st.dataframe(styled_c, use_container_width=True, height=500)

# ══════════════════════════════════════════════════════════════════════════
# РЯДОК 3: Scatter + Країни
# ══════════════════════════════════════════════════════════════════════════
col_s, col_cnt = st.columns(2)

with col_s:
    st.markdown('<div class="section-title">🔍 Обсяг угод vs Win Rate</div>', unsafe_allow_html=True)
    fig_sc = px.scatter(
        filtered, x="Всього", y="Win Rate (%)",
        size="Виграно", color="Win Rate (%)", text="CRM",
        color_continuous_scale="RdYlGn", range_color=[0, 70], height=360,
        hover_data={"Виграно": True, "Програно": True, "Всього": True},
    )
    fig_sc.add_hline(y=50, line_dash="dash", line_color="#888",
                     annotation_text="50% Win Rate", annotation_position="right")
    fig_sc.update_traces(textposition="top center", textfont_size=10)
    fig_sc.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10), coloraxis_showscale=False,
        xaxis=dict(gridcolor="#f0f0f0", title="Всього угод"),
        yaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_sc, use_container_width=True)
    st.markdown('<p class="note">Розмір кола = кількість виграних угод</p>', unsafe_allow_html=True)

with col_cnt:
    st.markdown('<div class="section-title">🌍 Win Rate по країнах</div>', unsafe_allow_html=True)
    fig_cnt = go.Figure(go.Bar(
        x=country_df["Win Rate (%)"],
        y=country_df["Країна"],
        orientation="h",
        marker_color=["#27ae60" if v >= 50 else "#f39c12" if v >= 30 else "#e74c3c"
                      for v in country_df["Win Rate (%)"]],
        text=[f"{v:.0f}% ({w}w/{l}l)"
              for v, w, l in zip(country_df["Win Rate (%)"],
                                  country_df["Виграно"],
                                  country_df["Програно"])],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Win Rate: %{x:.1f}%<extra></extra>",
    ))
    fig_cnt.update_layout(
        height=360,
        xaxis=dict(title="Win Rate (%)", range=[0, 130], gridcolor="#f0f0f0"),
        yaxis=dict(title="", autorange="reversed"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=120, t=10, b=20),
    )
    st.plotly_chart(fig_cnt, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# РЯДОК 4: Donut по CRM + Stage funnel
# ══════════════════════════════════════════════════════════════════════════
col_d, col_f = st.columns(2)

with col_d:
    st.markdown('<div class="section-title">🥧 Розподіл виграних угод по CRM (топ-8)</div>', unsafe_allow_html=True)
    top8 = filtered.nlargest(8, "Виграно")
    fig_pie = px.pie(
        top8, values="Виграно", names="CRM",
        hole=0.4, height=320,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(font_size=11),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_f:
    st.markdown('<div class="section-title">📊 Розподіл угод за статусами (999 лідів)</div>', unsafe_allow_html=True)
    stage_df = pd.DataFrame({
        "Статус":     ["Closed Lost", "Closed Won", "Negotiations", "Project set up", "Trial", "Payment"],
        "Кількість":  [431, 216, 158, 39, 36, 15],
    })
    fig_stage = px.bar(
        stage_df, x="Кількість", y="Статус", orientation="h",
        color="Статус", height=320,
        color_discrete_map={
            "Closed Won":    "#27ae60",
            "Closed Lost":   "#e74c3c",
            "Negotiations":  "#3498db",
            "Project set up":"#9b59b6",
            "Trial":         "#f39c12",
            "Payment":       "#1abc9c",
        },
        text="Кількість",
    )
    fig_stage.update_traces(textposition="outside")
    fig_stage.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=50, t=10, b=10),
        xaxis=dict(gridcolor="#f0f0f0"),
        yaxis=dict(categoryorder="total ascending"),
    )
    st.plotly_chart(fig_stage, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# ВИСНОВКИ
# ══════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div class="section-title">💡 Ключові висновки</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.info("**📅 Місячна динаміка**\n\n🏆 Пік виграшів: **Березень 2024 — 86 угод**\n\n⚠️ Пік програшів: **Березень 2024 — 181 угода**\n\n📈 Найкращий Win Rate: **Лютий 2024 — 37.0%**")
with c2:
    st.success("**🏆 Топ CRM за Win Rate**\n\n1. ZohoCRM — **60.00%** (10 угод)\n2. 1C as CRM — **57.14%** (7 угод)\n3. Pipedrive — **52.38%** (21 угода)\n4. Hubspot — **50.00%** (10 угод)")
with c3:
    st.error("**⚠️ Низька конверсія**\n\nMicrosoft Dynamics — **0%** (3 угоди)\n\nSalesdrive — **17.65%** (17 угод)\n\nBitrix24 — **27.12%** (59 угод)\n\nNo CRM (261 угода) — **29.12%**")

st.divider()
st.caption("📊 Ringostat · Revenue Operations Specialist · Test Task · Closed Won / Closed Lost · 2024")
