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

# ── Дані ──────────────────────────────────────────────────────────────────
monthly_df = pd.DataFrame({
    "Місяць":   ["2023-07","2023-08","2023-09","2023-10","2023-11","2023-12",
                 "2024-01","2024-02","2024-03","2024-04","2024-05","2024-06"],
    "Виграно":  [42, 55, 60, 72, 85, 91, 106, 88, 74, 69, 58, 50],
    "Програно": [68, 82, 95, 110, 130, 148, 95, 176, 140, 118, 95, 80],
})
monthly_df["Всього"]     = monthly_df["Виграно"] + monthly_df["Програно"]
monthly_df["Win Rate (%)"] = (monthly_df["Виграно"] / monthly_df["Всього"] * 100).round(1)

crm_df = pd.DataFrame({
    "CRM":      ["ZohoCRM","1C as CRM","Pipedrive","NetHunt CRM","Hubspot",
                 "KeyCRM","KeepinCRM","AmoCRM","Creatio","Custom CRM",
                 "No CRM","Bitrix24","Other","Salesdrive"],
    "Виграно":  [6, 4, 11, 7, 5, 28, 6, 15, 4, 8, 76, 16, 10, 3],
    "Програно": [4, 3, 10, 7, 5, 34, 11, 30, 8, 18, 185, 43, 27, 14],
})
crm_df["Всього"]      = crm_df["Виграно"] + crm_df["Програно"]
crm_df["Win Rate (%)"] = (crm_df["Виграно"] / crm_df["Всього"] * 100).round(2)
crm_df = crm_df.sort_values("Win Rate (%)", ascending=False).reset_index(drop=True)

# helper: color Win Rate cell manually (no matplotlib needed)
def color_winrate(val):
    if val >= 50:
        bg = "#d4edda"; color = "#155724"
    elif val >= 30:
        bg = "#fff3cd"; color = "#856404"
    else:
        bg = "#f8d7da"; color = "#721c24"
    return f"background-color: {bg}; color: {color}; font-weight: 600"

def color_bar_col(val, vmax):
    pct = min(val / vmax, 1.0)
    r = int(173 + (41  - 173) * pct)
    g = int(216 + (128 - 216) * pct)
    b = int(230 + (185 - 230) * pct)
    return f"background-color: rgb({r},{g},{b})"

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 CRM Analytics")
    st.caption("Звіт з аналізу конверсії угод")
    st.divider()
    st.subheader("🔧 Фільтри")
    min_deals   = st.slider("Мін. кількість угод (CRM):", 1, 60, 1)
    show_no_crm = st.checkbox("Включити 'No CRM'", value=True)
    st.divider()
    st.subheader("📌 Ключові факти")
    st.success("🏆 Найбільше виграно: **Січень 2024** (106 угод)")
    st.error("📉 Найбільше програно: **Лютий 2024** (176 угод)")
    st.info("🥇 Найкращий Win Rate: **Словаччина (SK)** — 100%")
    st.divider()
    st.caption("Дані: Closed Won / Closed Lost · 2023–2024")

# ── Заголовок ──────────────────────────────────────────────────────────────
st.title("📊 Аналіз конверсії та результатів угод")
st.markdown("Детальний звіт по закритих угодах **Closed Won** та **Closed Lost** · 2023–2024")
st.divider()

# ── KPI картки ────────────────────────────────────────────────────────────
total_won  = crm_df["Виграно"].sum()
total_lost = crm_df["Програно"].sum()
overall_wr = round(total_won / (total_won + total_lost) * 100, 1)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card green"><div class="metric-value">{total_won}</div><div class="metric-label">✅ Всього виграно угод</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card red"><div class="metric-value">{total_lost}</div><div class="metric-label">❌ Всього програно угод</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{overall_wr}%</div><div class="metric-label">📈 Загальний Win Rate</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card gold"><div class="metric-value">SK 🇸🇰</div><div class="metric-label">🏆 Найкращий Win Rate по країні</div></div>', unsafe_allow_html=True)

st.markdown("")

# ── Місячна динаміка ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">📅 Динаміка угод по місяцях</div>', unsafe_allow_html=True)
col_l, col_r = st.columns([2, 1])

with col_l:
    fig_m = go.Figure()
    fig_m.add_trace(go.Bar(x=monthly_df["Місяць"], y=monthly_df["Виграно"],
                           name="Виграно ✅", marker_color="#27ae60"))
    fig_m.add_trace(go.Bar(x=monthly_df["Місяць"], y=monthly_df["Програно"],
                           name="Програно ❌", marker_color="#e74c3c"))
    fig_m.add_trace(go.Scatter(x=monthly_df["Місяць"], y=monthly_df["Win Rate (%)"],
                               name="Win Rate (%)", yaxis="y2", mode="lines+markers",
                               line=dict(color="#f39c12", width=2.5, dash="dot"),
                               marker=dict(size=6)))
    fig_m.update_layout(
        barmode="group", height=340,
        yaxis=dict(title="Кількість угод", gridcolor="#f0f0f0"),
        yaxis2=dict(title="Win Rate (%)", overlaying="y", side="right",
                    range=[0, 70], showgrid=False),
        legend=dict(orientation="h", y=1.12, x=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=40),
        xaxis=dict(tickangle=30),
        annotations=[
            dict(x="2024-01", y=106, text="🏆 Пік виграшів", showarrow=True,
                 arrowhead=2, ax=0, ay=-35, font=dict(color="#27ae60", size=11)),
            dict(x="2024-02", y=176, text="⚠️ Пік програшів", showarrow=True,
                 arrowhead=2, ax=0, ay=-35, font=dict(color="#e74c3c", size=11)),
        ]
    )
    st.plotly_chart(fig_m, use_container_width=True)

with col_r:
    st.markdown('<div class="section-title" style="margin-top:0">📋 Таблиця по місяцях</div>', unsafe_allow_html=True)
    m_show = monthly_df[["Місяць","Виграно","Програно","Win Rate (%)"]].copy()
    styled_m = (
        m_show.style
        .applymap(color_winrate, subset=["Win Rate (%)"])
        .format({"Win Rate (%)": "{:.1f}%"})
    )
    st.dataframe(styled_m, use_container_width=True, height=330)

# ── CRM Win Rate ───────────────────────────────────────────────────────────
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
        height=420,
        xaxis=dict(title="Win Rate (%)", range=[0, 80], gridcolor="#f0f0f0"),
        yaxis=dict(title=""),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=70, t=10, b=20),
    )
    st.plotly_chart(fig_c, use_container_width=True)
    st.markdown('<p class="note">🟢 ≥50% Win Rate &nbsp;|&nbsp; 🟡 30–49% &nbsp;|&nbsp; 🔴 &lt;30%</p>', unsafe_allow_html=True)

with col_table:
    crm_show = filtered[["CRM","Виграно","Програно","Всього","Win Rate (%)"]].copy()
    max_all  = crm_show["Всього"].max()
    styled_c = (
        crm_show.style
        .applymap(color_winrate, subset=["Win Rate (%)"])
        .applymap(lambda v: color_bar_col(v, max_all), subset=["Всього"])
        .format({"Win Rate (%)": "{:.2f}%"})
    )
    st.dataframe(styled_c, use_container_width=True, height=420)

# ── Scatter + Donut ────────────────────────────────────────────────────────
col_s, col_p = st.columns(2)

with col_s:
    st.markdown('<div class="section-title">🔍 Обсяг угод vs Win Rate</div>', unsafe_allow_html=True)
    fig_sc = px.scatter(
        filtered, x="Всього", y="Win Rate (%)",
        size="Виграно", color="Win Rate (%)", text="CRM",
        color_continuous_scale="RdYlGn", range_color=[0, 70], height=320,
        hover_data={"Виграно": True, "Програно": True, "Всього": True},
    )
    fig_sc.add_hline(y=50, line_dash="dash", line_color="#888")
    fig_sc.update_traces(textposition="top center", textfont_size=10)
    fig_sc.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10), coloraxis_showscale=False,
        xaxis=dict(gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_sc, use_container_width=True)
    st.markdown('<p class="note">Розмір кола = кількість виграних угод</p>', unsafe_allow_html=True)

with col_p:
    st.markdown('<div class="section-title">🥧 Розподіл виграних угод по CRM</div>', unsafe_allow_html=True)
    fig_pie = px.pie(
        filtered.nlargest(8, "Виграно"), values="Виграно", names="CRM",
        hole=0.4, height=320,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(font_size=11),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Висновки ───────────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-title">💡 Ключові висновки</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.info("**📅 Місячні піки**\n\nНайбільше виграно: **Січень 2024 — 106 угод**\n\nНайбільше програно: **Лютий 2024 — 176 угод**")
with c2:
    st.success("**🏆 Топ CRM за конверсією**\n\n1. ZohoCRM — **60.00%**\n2. 1C as CRM — **57.14%**\n3. Pipedrive — **52.38%**")
with c3:
    st.error("**⚠️ Низька конверсія**\n\nSalesdrive — **17.65%**\n\nBitrix24 — **27.12%**\n\nNo CRM (261 угод) — **29.12%**")

st.divider()
st.caption("📊 Звіт з аналізу конверсії та результатів угод · Closed Won / Closed Lost · 2023–2024")
