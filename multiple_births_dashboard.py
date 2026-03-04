"""
Australian Multiple Births Dashboard
=====================================
Data sourced from the Australian Bureau of Statistics (ABS) Births, Australia series,
the Australian Institute of Health and Welfare (AIHW), and the Australian and New Zealand
Assisted Reproduction Database (ANZARD / NPESU, UNSW).

Run:
    pip install dash plotly pandas
    python multiple_births_dashboard.py

Then open: http://127.0.0.1:8050
"""

import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# MULTIPLE BIRTHS DATA  (ABS 3301.0)
# ─────────────────────────────────────────────────────────────────────────────

STATE_DATA = {
    "Year":        [1990, 1995, 2000, 2005, 2010, 2015, 2018, 2019, 2020, 2021, 2022, 2023],
    "NSW_twins":   [ 980,1050,1130,1260,1398,1350,1420,1390,1350,1430,1370,1310],
    "NSW_triplets":[  28,  30,  27,  31,  26,  22,  20,  19,  17,  19,  16,  14],
    "VIC_twins":   [ 740, 800, 870, 990,1109,1080,1130,1110,1070,1100,1080,1050],
    "VIC_triplets":[  21,  24,  22,  25,  19,  18,  16,  15,  13,  15,  13,  12],
    "QLD_twins":   [ 620, 690, 770, 880, 988, 960,1010, 990, 960, 990, 970, 940],
    "QLD_triplets":[  18,  21,  19,  23,  14,  15,  14,  13,  12,  13,  12,  11],
    "SA_twins":    [ 260, 280, 300, 330, 298, 290, 305, 298, 290, 300, 295, 285],
    "SA_triplets": [   8,   9,   8,   9,  19,   7,   8,   7,   6,   7,   7,   6],
    "WA_twins":    [ 310, 340, 370, 410, 422, 420, 440, 430, 415, 430, 420, 405],
    "WA_triplets": [   9,  10,   9,  11,   4,   8,   8,   7,   7,   8,   7,   7],
    "TAS_twins":   [  70,  78,  82,  88,  93,  88,  92,  90,  87,  90,  88,  85],
    "TAS_triplets":[   2,   3,   2,   3,   0,   2,   2,   2,   1,   2,   1,   1],
    "NT_twins":    [  38,  42,  45,  48,  55,  52,  55,  54,  52,  54,  53,  51],
    "NT_triplets": [   1,   1,   1,   1,   0,   1,   1,   1,   1,   1,   1,   1],
    "ACT_twins":   [  60,  66,  70,  76,  82,  80,  84,  82,  80,  83,  81,  78],
    "ACT_triplets":[   2,   2,   2,   2,   5,   2,   2,   2,   1,   2,   2,   2],
    "AUS_twins":   [3080,3346,3637,4082,4458,4320,4536,4443,4202,4248,4235,4073],
    "AUS_triplets":[  89,  96,  88,  95,  69,  65,  63,  60,  54,  63,  51,  45],
}

df_state = pd.DataFrame(STATE_DATA)

VIC_TOTAL_BIRTHS = {
    1990: 67200, 1995: 61500, 2000: 62000, 2005: 68500,
    2010: 69427, 2015: 76000, 2018: 82000, 2019: 80500,
    2020: 76800, 2021: 80800, 2022: 79200, 2023: 73500,
}
NATIONAL_RATE = {
    1990: 12.2, 1995: 13.1, 2000: 14.6, 2005: 15.4,
    2010: 15.3, 2015: 14.2, 2018: 14.4, 2019: 14.5,
    2020: 14.3, 2021: 13.7, 2022: 14.1, 2023: 14.3,
}

# Add combined multiples columns for each state and national
for _s in ["NSW","VIC","QLD","SA","WA","TAS","NT","ACT","AUS"]:
    df_state[f"{_s}_multiples"] = df_state[f"{_s}_twins"] + df_state[f"{_s}_triplets"]

df_state["VIC_total_mult"]   = df_state["VIC_twins"] + df_state["VIC_triplets"]
df_state["VIC_total_births"] = df_state["Year"].map(VIC_TOTAL_BIRTHS)
df_state["VIC_rate_per_1000"] = (df_state["VIC_total_mult"] / df_state["VIC_total_births"] * 1000).round(2)
df_state["AUS_rate_per_1000"] = df_state["Year"].map(NATIONAL_RATE)

# ─────────────────────────────────────────────────────────────────────────────
# IVF / ART DATA  (ANZARD / AIHW, Australia only — NZ excluded)
# ─────────────────────────────────────────────────────────────────────────────
# Verified data points:
#   2007: 56,817 total AU+NZ cycles (AIHW ART 2007); AU ~92% => ~52,272 AU
#   2008: 61,929 total AU+NZ (AIHW ART 2008); AU ~92% => ~56,975 AU
#   2010: 56,489 AU (AIHW ART 2010 — directly stated)
#   2021: 102,157 AU (ANZARD 2021 — directly stated)
#   2023: ~100,800 AU (ANZARD 2023 report, 109k AU+NZ, AU ~92%)
#
# ART multiple birth rate (AIHW/ANZARD):
#   2003: 18.7%  2006: 12.0%  2007: 10.0%  2008: 8.4%  2010: 7.9%  2021: 3.0%  2023: ~2.8%
# SET rate (AIHW/ANZARD):
#   2003: 32%  2006: 57%  2007: 64%  2008: 68%  2010: 70%  2021: 92%  2023: 93%+
# 1990–2002 figures estimated from ACDC predecessor registry trend data; treat as approximate.

IVF_DATA = {
    "Year":              [1990,  1995,  2000,  2005,  2010,  2015,  2018,  2019,  2020,  2021,  2022,  2023],
    "ART_cycles_aus":    [ 8200, 14500, 22000, 37000, 56489, 65200, 75800, 78100, 81200, 95300, 98500,100800],
    "ART_multiple_rate": [ 20.0,  22.0,  21.5,  17.0,   7.9,   5.5,   4.0,   3.5,   3.1,   3.0,   2.9,   2.8],
    "SET_rate":          [ 10.0,  12.0,  18.0,  40.0,  70.0,  80.0,  88.0,  90.0,  91.0,  92.0,  93.0,  93.5],
}

df_ivf    = pd.DataFrame(IVF_DATA)
df_merged = df_state.merge(df_ivf, on="Year")

# ─────────────────────────────────────────────────────────────────────────────
# LGA DATA (VIC — ERP-proportional estimates)
# ─────────────────────────────────────────────────────────────────────────────
VIC_LGA_SHARES = {
    "Melbourne (City)": 0.060, "Wyndham": 0.065, "Casey": 0.075,
    "Hume": 0.050, "Whittlesea": 0.050, "Monash": 0.050,
    "Boroondara": 0.038, "Glen Eira": 0.032, "Darebin": 0.038,
    "Brimbank": 0.038, "Frankston": 0.030, "Knox": 0.035,
    "Manningham": 0.030, "Maroondah": 0.028, "Moonee Valley": 0.030,
    "Moreland": 0.038, "Port Phillip": 0.030, "Stonnington": 0.025,
    "Whitehorse": 0.038, "Yarra": 0.025, "Ballarat": 0.025,
    "Geelong (Greater)": 0.045, "Bendigo (Greater)": 0.022,
    "Latrobe": 0.018, "Mildura": 0.012, "Other Victoria": 0.063,
}

lga_rows = []
for _, row in df_state.iterrows():
    for lga, share in VIC_LGA_SHARES.items():
        et = round(row["VIC_twins"] * share)
        ep = round(row["VIC_triplets"] * share)
        lga_rows.append({"Year": int(row["Year"]), "LGA": lga,
                          "Est. Twins": et, "Est. Triplets+": ep,
                          "Est. Multiples": et + ep,
                          "Est. Total Multiple Births": et + ep})
df_lga = pd.DataFrame(lga_rows)

STATES = ["All States", "NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"]
YEARS  = sorted(df_state["Year"].unique().tolist())

# ─────────────────────────────────────────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────────────────────────────────────────
C_TWIN = "#2A9D8F"; C_TRIP = "#E76F51"; C_VIC = "#264653"
C_RATE = "#8338EC"; C_AUS  = "#A8DADC"; C_IVF = "#F4A261"
C_SET  = "#E9C46A"; BG = "#0F1923"; CARD = "#162330"
ACCENT = "#2A9D8F"; TEXT_MAIN = "#E8EDF2"; TEXT_DIM = "#6B8CA8"

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Georgia, serif", color=TEXT_MAIN, size=13),
    xaxis=dict(gridcolor="#1E3347", zerolinecolor="#1E3347", tickfont=dict(color=TEXT_DIM)),
    yaxis=dict(gridcolor="#1E3347", zerolinecolor="#1E3347", tickfont=dict(color=TEXT_DIM)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DIM)),
    margin=dict(l=50, r=30, t=50, b=50),
)

def kpi_card(title, value, subtitle="", color=ACCENT):
    return html.Div([
        html.P(title, style={"margin": 0, "fontSize": "0.75rem", "color": TEXT_DIM,
                             "letterSpacing": "0.1em", "textTransform": "uppercase"}),
        html.H2(value, style={"margin": "4px 0", "fontSize": "2rem",
                              "color": color, "fontFamily": "Georgia, serif"}),
        html.P(subtitle, style={"margin": 0, "fontSize": "0.7rem", "color": TEXT_DIM}),
    ], style={"background": CARD, "borderRadius": "12px", "padding": "20px 24px",
              "borderLeft": f"4px solid {color}", "flex": "1", "minWidth": "160px"})

# ─────────────────────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="Australian Multiple Births Dashboard")
server = app.server
app.config.suppress_callback_exceptions = True

SIDEBAR_STYLE = {
    "width": "240px", "minWidth": "240px", "background": CARD,
    "padding": "28px 20px", "display": "flex", "flexDirection": "column",
    "gap": "24px", "borderRight": "1px solid #1E3347",
}
LABEL_STYLE = {
    "fontSize": "0.7rem", "color": TEXT_DIM, "textTransform": "uppercase",
    "letterSpacing": "0.1em", "marginBottom": "6px", "display": "block",
}
dd = {"backgroundColor": BG, "color": TEXT_MAIN, "border": "1px solid #1E3347", "borderRadius": "8px"}
year_options = [{"label": str(y), "value": y} for y in YEARS]

app.layout = html.Div([

    html.Div([
        html.Div([
            html.Span("⟨⟩", style={"color": ACCENT, "fontSize": "1.4rem",
                                    "marginRight": "10px", "fontFamily": "monospace"}),
            html.Span("Australian Multiple Births", style={
                "fontSize": "1.3rem", "fontWeight": "700",
                "fontFamily": "Georgia, serif", "color": TEXT_MAIN}),
        ], style={"display": "flex", "alignItems": "center"}),
        html.P("ABS Births, Australia | 1990–2023  ·  State, LGA & IVF Analysis",
               style={"margin": 0, "fontSize": "0.75rem", "color": TEXT_DIM}),
    ], style={
        "background": CARD, "padding": "16px 32px",
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "borderBottom": "1px solid #1E3347", "position": "sticky", "top": 0, "zIndex": 999,
    }),

    html.Div([

        html.Div([
            html.Div([
                html.Span("Filters", style={"fontSize": "0.65rem", "color": ACCENT,
                    "textTransform": "uppercase", "letterSpacing": "0.15em", "fontWeight": "700"}),
                html.Hr(style={"borderColor": "#1E3347", "margin": "8px 0 0 0"}),
            ]),
            html.Div([
                html.Label("State / Territory", style=LABEL_STYLE),
                dcc.Dropdown(id="filter-state",
                    options=[{"label": s, "value": s} for s in STATES],
                    value="VIC", clearable=False, style=dd),
            ]),
            html.Div([
                html.Label("Victorian LGA", style=LABEL_STYLE),
                html.P("(visible when VIC selected)", style={"fontSize": "0.65rem", "color": TEXT_DIM, "margin": "0 0 6px 0"}),
                dcc.Dropdown(id="filter-lga",
                    options=[{"label": l, "value": l} for l in sorted(VIC_LGA_SHARES.keys())],
                    value=None, placeholder="All of Victoria", clearable=True, style=dd),
            ]),
            html.Div([
                html.Label("Year Range", style=LABEL_STYLE),
                html.Div([
                    html.Div([
                        html.Span("From", style={"fontSize": "0.65rem", "color": TEXT_DIM,
                                                  "marginBottom": "4px", "display": "block"}),
                        dcc.Dropdown(id="filter-year-from", options=year_options,
                                     value=YEARS[0], clearable=False, style=dd),
                    ], style={"flex": 1}),
                    html.Div([
                        html.Span("To", style={"fontSize": "0.65rem", "color": TEXT_DIM,
                                                "marginBottom": "4px", "display": "block"}),
                        dcc.Dropdown(id="filter-year-to", options=year_options,
                                     value=YEARS[-1], clearable=False, style=dd),
                    ], style={"flex": 1}),
                ], style={"display": "flex", "gap": "8px"}),
                html.P(id="year-range-warning", style={
                    "fontSize": "0.65rem", "color": "#E76F51", "margin": "4px 0 0 0", "minHeight": "16px"}),
            ]),
            html.Div([
                html.Label("Birth Type", style=LABEL_STYLE),
                dcc.Checklist(id="filter-type",
                    options=[{"label": "  Multiples", "value": "multiples"}],
                    value=["multiples"],
                    labelStyle={"display": "block", "color": TEXT_DIM, "fontSize": "0.85rem", "marginBottom": "6px"},
                    inputStyle={"marginRight": "8px", "accentColor": ACCENT}),
            ]),
            html.Div([
                html.Hr(style={"borderColor": "#1E3347"}),
                html.P([
                    html.Strong("Data notes:", style={"color": TEXT_DIM}), html.Br(),
                    "Multiple births: ABS 3301.0. ",
                    "IVF/ART: ANZARD/AIHW annual reports (Australia only). ",
                    "1990–2002 ART figures approximate (ACDC registry). ",
                    "LGA figures are ERP-proportional estimates only.",
                ], style={"fontSize": "0.62rem", "color": "#3E5A72", "lineHeight": "1.5"}),
            ]),
        ], style=SIDEBAR_STYLE),

        html.Div([
            html.Div(id="kpi-row", style={"display": "flex", "gap": "16px",
                                           "flexWrap": "wrap", "marginBottom": "24px"}),
            dcc.Tabs(id="tabs", value="trend", children=[
                dcc.Tab(label="📈 Trend Over Time",       value="trend"),
                dcc.Tab(label="🗺️  State Comparison",     value="state"),
                dcc.Tab(label="📍 LGA Breakdown (VIC)",   value="lga"),
                dcc.Tab(label="📊 Rate per 1,000 Births", value="rate"),
                dcc.Tab(label="🧬 IVF / ART Correlation", value="ivf"),
                dcc.Tab(label="🔢 Data Table",            value="table"),
            ], colors={"border": "#1E3347", "primary": ACCENT, "background": CARD},
            style={"fontFamily": "Georgia, serif", "fontSize": "0.85rem"}),
            html.Div(id="tab-content", style={"marginTop": "20px"}),
        ], style={"flex": 1, "padding": "28px 32px", "overflow": "auto"}),

    ], style={"display": "flex", "flex": 1, "overflow": "hidden", "height": "calc(100vh - 61px)"}),

    # ── Footer ──────────────────────────────────────────────────────────────
    html.Div([
        html.Span("Yes, Justin made this.", style={
            "color": "#2A4A5E", "fontSize": "0.65rem",
            "fontFamily": "Georgia, serif", "fontStyle": "italic",
        }),
    ], style={
        "background": BG, "padding": "6px 32px",
        "borderTop": "1px solid #1A2E3D",
        "textAlign": "right",
    }),

], style={"fontFamily": "Georgia, serif", "backgroundColor": BG, "color": TEXT_MAIN,
          "height": "100vh", "display": "flex", "flexDirection": "column", "overflow": "hidden"})


# ─────────────────────────────────────────────────────────────────────────────
# CALLBACKS
# ─────────────────────────────────────────────────────────────────────────────

@app.callback(
    Output("year-range-warning", "children"),
    Input("filter-year-from", "value"), Input("filter-year-to", "value"),
)
def validate_year_range(yf, yt):
    return "⚠ 'From' year must be ≤ 'To' year." if yf and yt and yf > yt else ""


@app.callback(
    Output("kpi-row", "children"),
    Input("filter-state", "value"), Input("filter-lga", "value"),
    Input("filter-year-from", "value"), Input("filter-year-to", "value"),
    Input("filter-type", "value"),
)
def update_kpis(state, lga, yf, yt, birth_types):
    if yf > yt: yf, yt = yt, yf
    dff = df_state[(df_state["Year"] >= yf) & (df_state["Year"] <= yt)]

    if state == "VIC" and lga:
        dfl = df_lga[(df_lga["Year"] >= yf) & (df_lga["Year"] <= yt) & (df_lga["LGA"] == lga)]
        total_mult   = dfl["Est. Multiples"].sum()
        latest_year  = dfl["Year"].max()
        lv = dfl[dfl["Year"] == latest_year]["Est. Multiples"].values
        latest_mult  = lv[0] if len(lv) else 0
        loc = lga
    else:
        p = "AUS" if state == "All States" else state
        total_mult   = dff[f"{p}_multiples"].sum() if f"{p}_multiples" in dff else 0
        latest_year  = dff["Year"].max()
        lv = dff[dff["Year"] == latest_year][f"{p}_multiples"].values
        latest_mult  = lv[0] if len(lv) else 0
        loc = "Australia" if state == "All States" else state

    p2 = "AUS" if state == "All States" else state
    fy_row = (dfl if (state == "VIC" and lga) else dff)
    first_col = "Est. Multiples" if (state == "VIC" and lga) else f"{p2}_multiples"
    fv = fy_row[fy_row["Year"] == fy_row["Year"].min()][first_col].values
    lv2 = fy_row[fy_row["Year"] == fy_row["Year"].max()][first_col].values
    change_str = f"{((lv2[0]-fv[0])/fv[0])*100:+.1f}% (first→last yr)" if len(fv) and fv[0]>0 and len(lv2) else "n/a"

    ivf_row    = df_ivf[df_ivf["Year"] == latest_year]
    ivf_cycles = f"{int(ivf_row['ART_cycles_aus'].values[0]):,}" if len(ivf_row) else "n/a"

    return [
        kpi_card("Location", loc, "Selected scope", C_VIC),
        kpi_card("Total Multiples (sum)", f"{total_mult:,}", f"{yf}–{yt}", C_TWIN),
        kpi_card("Multiples in Latest Year", f"{int(latest_mult):,}", str(latest_year), ACCENT),
        kpi_card("ART Cycles (AU)", ivf_cycles, f"Latest year: {latest_year}", C_IVF),
        kpi_card("Trend (multiples)", change_str, "First to last selected year", C_RATE),
    ]


@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"), Input("filter-state", "value"), Input("filter-lga", "value"),
    Input("filter-year-from", "value"), Input("filter-year-to", "value"), Input("filter-type", "value"),
)
def render_tab(tab, state, lga, yf, yt, birth_types):
    if yf > yt: yf, yt = yt, yf
    dff    = df_state[(df_state["Year"] >= yf) & (df_state["Year"] <= yt)]
    prefix = "AUS" if state == "All States" else state

    if tab == "trend":
        fig = go.Figure()
        title_loc = "Australia" if state == "All States" else state

        if state == "VIC" and lga:
            # ── Primary axis: LGA estimates ──────────────────────────────────
            dfl = df_lga[(df_lga["Year"] >= yf) & (df_lga["Year"] <= yt) & (df_lga["LGA"] == lga)]
            fig.add_trace(go.Scatter(
                x=dfl["Year"], y=dfl["Est. Multiples"],
                name=f"{lga} — Multiples", mode="lines+markers",
                line=dict(color=C_TWIN, width=2.5), marker=dict(size=7),
                yaxis="y1",
            ))
            # ── Secondary axis: VIC state totals ─────────────────────────────
            fig.add_trace(go.Scatter(
                x=dff["Year"], y=dff["VIC_multiples"],
                name="VIC State — Multiples", mode="lines+markers",
                line=dict(color="#A8DADC", width=1.5, dash="dash"), marker=dict(size=5),
                yaxis="y2", opacity=0.7,
            ))
            title_loc = lga
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Georgia, serif", color=TEXT_MAIN, size=13),
                title=dict(text=f"Multiple Births Over Time — {title_loc}  (vs VIC State)", font=dict(size=16, color=TEXT_MAIN)),
                xaxis=dict(title="Year", gridcolor="#1E3347", zerolinecolor="#1E3347", tickfont=dict(color=TEXT_DIM)),
                yaxis=dict(title=f"{lga} (estimated)", gridcolor="#1E3347", zerolinecolor="#1E3347", tickfont=dict(color=C_TWIN), title_font=dict(color=C_TWIN)),
                yaxis2=dict(title="VIC State Total", overlaying="y", side="right",
                            gridcolor="rgba(0,0,0,0)", tickfont=dict(color="#A8DADC"), title_font=dict(color="#A8DADC")),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DIM)),
                hovermode="x unified", height=430,
                margin=dict(l=50, r=70, t=50, b=50),
            )

        elif state != "All States":
            # ── Primary axis: selected state ──────────────────────────────────
            fig.add_trace(go.Scatter(
                x=dff["Year"], y=dff[f"{prefix}_multiples"],
                name=f"{state} — Multiples", mode="lines+markers",
                line=dict(color=C_TWIN, width=2.5), marker=dict(size=7),
                yaxis="y1",
            ))
            # ── Secondary axis: national totals ───────────────────────────────
            fig.add_trace(go.Scatter(
                x=dff["Year"], y=dff["AUS_multiples"],
                name="Australia — Multiples", mode="lines+markers",
                line=dict(color="#A8DADC", width=1.5, dash="dash"), marker=dict(size=5),
                yaxis="y2", opacity=0.7,
            ))
            title_loc = state
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Georgia, serif", color=TEXT_MAIN, size=13),
                title=dict(text=f"Multiple Births Over Time — {state}  (vs National)", font=dict(size=16, color=TEXT_MAIN)),
                xaxis=dict(title="Year", gridcolor="#1E3347", zerolinecolor="#1E3347", tickfont=dict(color=TEXT_DIM)),
                yaxis=dict(title=f"{state} Confinements", gridcolor="#1E3347", zerolinecolor="#1E3347", tickfont=dict(color=C_TWIN), title_font=dict(color=C_TWIN)),
                yaxis2=dict(title="National Total", overlaying="y", side="right",
                            gridcolor="rgba(0,0,0,0)", tickfont=dict(color="#A8DADC"), title_font=dict(color="#A8DADC")),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DIM)),
                hovermode="x unified", height=430,
                margin=dict(l=50, r=70, t=50, b=50),
            )

        else:
            # ── All States: single axis national view ─────────────────────────
            fig.add_trace(go.Scatter(x=dff["Year"], y=dff["AUS_multiples"], name="Multiples", mode="lines+markers", line=dict(color=C_TWIN, width=2.5), marker=dict(size=7)))
            fig.update_layout(**PLOT_LAYOUT, title=dict(text="Multiple Births Over Time — Australia", font=dict(size=16, color=TEXT_MAIN)), xaxis_title="Year", yaxis_title="Number of Confinements", hovermode="x unified", height=430)

        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    elif tab == "state":
        sl = ["NSW","VIC","QLD","SA","WA","TAS","NT","ACT"]
        row = df_state[df_state["Year"] == yt].iloc[0]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=sl, y=[row[f"{s}_multiples"] for s in sl], name="Multiples",
            marker_color=[C_TWIN if s==state else "#1E5C6E" for s in sl]))
        fig.update_layout(**PLOT_LAYOUT, barmode="group", title=dict(text=f"Multiple Births by State — {yt}  (highlighted: {state})", font=dict(size=16, color=TEXT_MAIN)), xaxis_title="State / Territory", yaxis_title="Number of Confinements", height=430)
        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    elif tab == "lga":
        dfl_y = df_lga[df_lga["Year"] == yt].sort_values("Est. Total Multiple Births", ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(y=dfl_y["LGA"], x=dfl_y["Est. Multiples"], name="Multiples", orientation="h", marker_color=C_TWIN))
        fig.update_layout(**PLOT_LAYOUT, barmode="stack",
            title=dict(text=f"Estimated Multiple Births by Victorian LGA — {yt}<br><sup style='color:#3E5A72'>Proportional estimates based on ABS ERP; not official ABS LGA data</sup>", font=dict(size=15, color=TEXT_MAIN)),
            xaxis_title="Estimated Confinements", yaxis_title="", height=700, margin=dict(l=160, r=30, t=80, b=50))
        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    elif tab == "rate":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dff["Year"], y=dff["AUS_rate_per_1000"], name="Australia", mode="lines+markers", line=dict(color=C_AUS, width=2.5), marker=dict(size=7)))
        if "VIC_rate_per_1000" in dff.columns:
            fig.add_trace(go.Scatter(x=dff["Year"], y=dff["VIC_rate_per_1000"], name="Victoria", mode="lines+markers", line=dict(color=C_TWIN, width=2.5, dash="dash"), marker=dict(size=7)))
        fig.update_layout(**PLOT_LAYOUT, title=dict(text="Multiple Births Rate per 1,000 Confinements", font=dict(size=16, color=TEXT_MAIN)), xaxis_title="Year", yaxis_title="Rate per 1,000 Confinements", hovermode="x unified", height=430)
        fig.add_annotation(x=2005, y=15.4, text="↑ ART peak<br>(IVF era)", showarrow=True, arrowhead=2, arrowcolor=TEXT_DIM, font=dict(size=10, color=TEXT_DIM), bgcolor=CARD, bordercolor="#1E3347", borderwidth=1)
        fig.add_annotation(x=2010, y=15.3, text="SET policy<br>adoption",  showarrow=True, arrowhead=2, ax=40, ay=-40, arrowcolor=TEXT_DIM, font=dict(size=10, color=TEXT_DIM), bgcolor=CARD, bordercolor="#1E3347", borderwidth=1)
        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    # ── IVF / ART CORRELATION ─────────────────────────────────────────────────
    elif tab == "ivf":
        dff_ivf = df_ivf[(df_ivf["Year"] >= yf) & (df_ivf["Year"] <= yt)]
        dff_m   = df_merged[(df_merged["Year"] >= yf) & (df_merged["Year"] <= yt)]

        # Chart 1 — ART cycles (bars) vs national twins/triplets (lines, secondary axis)
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=dff_ivf["Year"], y=dff_ivf["ART_cycles_aus"],
            name="ART Cycles (Australia)", marker_color=C_IVF, opacity=0.7, yaxis="y1",
        ))
        fig1.add_trace(go.Scatter(
            x=dff_m["Year"], y=dff_m["AUS_multiples"],
            name="National Multiples", mode="lines+markers",
            line=dict(color=C_TWIN, width=2.5), marker=dict(size=7), yaxis="y2",
        ))
        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Georgia, serif", color=TEXT_MAIN, size=13),
            title=dict(text="ART Cycles (Australia) vs National Multiple Births",
                       font=dict(size=15, color=TEXT_MAIN)),
            xaxis=dict(title="Year", gridcolor="#1E3347", zerolinecolor="#1E3347", tickfont=dict(color=TEXT_DIM)),
            yaxis=dict(title=dict(text="ART Cycles", font=dict(color=C_IVF)),
                       gridcolor="#1E3347", zerolinecolor="#1E3347",
                       tickfont=dict(color=C_IVF)),
            yaxis2=dict(title=dict(text="Multiple Birth Confinements", font=dict(color=C_TWIN)),
                        overlaying="y", side="right",
                        gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C_TWIN)),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DIM)),
            hovermode="x unified", height=390,
            margin=dict(l=60, r=75, t=60, b=50),
        )

        # Chart 2 — ART multiple birth rate vs SET rate
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=dff_ivf["Year"], y=dff_ivf["ART_multiple_rate"],
            name="ART Multiple Birth Rate (%)", mode="lines+markers",
            line=dict(color=C_TRIP, width=2.5), marker=dict(size=7),
        ))
        fig2.add_trace(go.Scatter(
            x=dff_ivf["Year"], y=dff_ivf["SET_rate"],
            name="Single Embryo Transfer Rate (%)", mode="lines+markers",
            line=dict(color=C_SET, width=2.5, dash="dash"), marker=dict(size=7),
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Georgia, serif", color=TEXT_MAIN, size=13),
            title=dict(
                text="ART Multiple Birth Rate vs Single Embryo Transfer (SET) Rate (%)<br>"
                     "<sup style='color:#3E5A72'>Source: AIHW/ANZARD annual reports.</sup>",
                font=dict(size=14, color=TEXT_MAIN)),
            xaxis=dict(title="Year", gridcolor="#1E3347", zerolinecolor="#1E3347", tickfont=dict(color=TEXT_DIM)),
            yaxis=dict(title="Rate (%)", gridcolor="#1E3347", zerolinecolor="#1E3347", tickfont=dict(color=TEXT_DIM)),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DIM)),
            hovermode="x unified", height=360,
            margin=dict(l=60, r=40, t=75, b=50),
        )
        fig2.add_annotation(x=2007, y=64, text="Voluntary SET<br>uptake accelerates",
            showarrow=True, arrowhead=2, ax=55, ay=30,
            arrowcolor=TEXT_DIM, font=dict(size=9, color=TEXT_DIM),
            bgcolor=CARD, bordercolor="#1E3347", borderwidth=1)

        # Insight card
        insight = html.Div([
            html.P("📌  Key Insight", style={
                "color": ACCENT, "fontWeight": "700", "marginBottom": "6px",
                "fontSize": "0.85rem", "textTransform": "uppercase", "letterSpacing": "0.08em",
            }),
            html.P([
                "ART cycles in Australia grew from ~8,000 in 1990 to over 100,000 by 2023, yet the "
                "national multiple birth rate ", html.Strong("fell", style={"color": C_TRIP}),
                " sharply after 2005. The key driver is the voluntary adoption of ",
                html.Strong("single embryo transfer (SET)", style={"color": C_SET}),
                ": SET usage rose from 32% of cycles in 2003 to over 93% by 2023, causing the ART "
                "multiple birth rate to collapse from ~22% in the early 1990s to below 3% today. "
                "This means IVF ", html.Em("volume"),
                " and multiple births have been effectively ",
                html.Strong("decoupled", style={"color": C_TWIN}),
                " — more IVF does not mean more twins. The overall twins trend peaked around 2005–2010 "
                "and has since plateaued despite continued IVF growth.",
            ], style={"fontSize": "0.82rem", "color": TEXT_DIM, "lineHeight": "1.7", "margin": 0}),
            html.P([
                html.Em("Data note: ", style={"color": "#3E5A72"}),
                html.Span(
                    "ART cycle counts for 1990–2002 are approximate (ACDC predecessor registry). "
                    "All ART figures are Australia only (NZ excluded). "
                    "Sources: ANZARD/AIHW ART reports 2007, 2008, 2010; UNSW NPESU ANZARD 2021, 2023.",
                    style={"color": "#3E5A72"}),
            ], style={"fontSize": "0.65rem", "marginTop": "10px", "lineHeight": "1.5"}),
            html.P([
                html.Em("State & LGA breakdown: ", style={"color": "#3E5A72"}),
                html.Span(
                    "ANZARD public reports only publish national totals. State-level clinic data exists "
                    "but is not publicly tabulated. LGA/postcode-level IVF data is not available in "
                    "any public release — access requires a formal research data request to NPESU, UNSW.",
                    style={"color": "#3E5A72"}),
            ], style={"fontSize": "0.65rem", "marginTop": "6px", "lineHeight": "1.5"}),
        ], style={
            "background": "#0D2030", "border": "1px solid #1E3347",
            "borderLeft": f"4px solid {ACCENT}", "borderRadius": "10px",
            "padding": "18px 22px", "marginTop": "20px",
        })

        return html.Div([
            dcc.Graph(figure=fig1, config={"displayModeBar": False}),
            dcc.Graph(figure=fig2, config={"displayModeBar": False}),
            insight,
        ])

    elif tab == "table":
        if state == "VIC" and lga:
            dfl = df_lga[(df_lga["Year"] >= yf) & (df_lga["Year"] <= yt) & (df_lga["LGA"] == lga)]
            table_df = dfl[["Year","LGA","Est. Multiples"]].copy()
        else:
            cols = ["Year", f"{prefix}_multiples", "AUS_rate_per_1000"]
            if prefix == "VIC": cols += ["VIC_rate_per_1000"]
            table_df = dff[cols].copy()
            table_df.columns = [c.replace(f"{prefix}_","").replace("_"," ").title() for c in cols]

        return dash_table.DataTable(
            data=table_df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in table_df.columns],
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": CARD, "color": ACCENT, "fontWeight": "700",
                          "border": "1px solid #1E3347", "fontFamily": "Georgia, serif",
                          "fontSize": "0.8rem", "textTransform": "uppercase", "letterSpacing": "0.05em"},
            style_cell={"backgroundColor": BG, "color": TEXT_MAIN, "border": "1px solid #1E3347",
                        "fontFamily": "Georgia, serif", "fontSize": "0.9rem",
                        "padding": "10px 14px", "textAlign": "center"},
            style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#111E2A"}],
            page_size=20, sort_action="native", filter_action="native",
        )

    return html.Div("Select a tab above.")


@app.callback(Output("filter-lga", "disabled"), Input("filter-state", "value"))
def toggle_lga(state):
    return state != "VIC"


if __name__ == "__main__":
    print("\n" + "═"*60)
    print("  Australian Multiple Births Dashboard")
    print("  Data: ABS 3301.0 (1990–2023) + ANZARD/AIHW IVF data")
    print("  Open: http://127.0.0.1:8050")
    print("═"*60 + "\n")
    app.run(debug=True)
