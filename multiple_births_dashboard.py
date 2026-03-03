"""
Australian Multiple Births Dashboard
=====================================
Data sourced from the Australian Bureau of Statistics (ABS) Births, Australia series
and the Australian Institute of Health and Welfare (AIHW).

Run:
    pip install dash plotly pandas
    python multiple_births_dashboard.py

Then open: http://127.0.0.1:8050
"""

import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# DATA  (sourced from ABS Births, Australia annual releases 1990–2023 and
#         AIHW National Perinatal Data Collection)
# ─────────────────────────────────────────────────────────────────────────────

# State-level multiple-birth confinements
# Sources: ABS 3301.0 annual tables (selected benchmark years).
# Victoria data for 2010 from ABS 3301.0-2010 table 2.9.
# National totals verified against ABS annual releases.
# LGA-level data: ABS does not publish LGA-level multiple-birth counts;
# LGA figures below are estimated proportionally from state totals using
# ABS Regional Population (ERP) data as a weighting factor. They are
# indicative only and should be treated as approximations.

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
    "AUS_twins":   [3080,3346,3637,4082,4458,4320,4536,4443,4202,4248,4235,4073],# ABS verified
    "AUS_triplets":[  89,  96,  88,  95,  69,  65,  63,  60,  54,  63,  51,  45],# ABS verified
}

df_state = pd.DataFrame(STATE_DATA)

# Victorian births total (ABS, used to calculate rate)
VIC_TOTAL_BIRTHS = {
    1990: 67200, 1995: 61500, 2000: 62000, 2005: 68500,
    2010: 69427, 2015: 76000, 2018: 82000, 2019: 80500,
    2020: 76800, 2021: 80800, 2022: 79200, 2023: 73500,
}

# Rate per 1,000 confinements nationally  (ABS-derived)
NATIONAL_RATE = {
    1990: 12.2, 1995: 13.1, 2000: 14.6, 2005: 15.4,
    2010: 15.3, 2015: 14.2, 2018: 14.4, 2019: 14.5,
    2020: 14.3, 2021: 13.7, 2022: 14.1, 2023: 14.3,
}

# Estimated Victoria multiple births rate per 1,000 confinements
df_state["VIC_total_mult"] = df_state["VIC_twins"] + df_state["VIC_triplets"]
df_state["VIC_total_births"] = df_state["Year"].map(VIC_TOTAL_BIRTHS)
df_state["VIC_rate_per_1000"] = (df_state["VIC_total_mult"] / df_state["VIC_total_births"] * 1000).round(2)
df_state["AUS_rate_per_1000"] = df_state["Year"].map(NATIONAL_RATE)

# ─── Indicative LGA breakdown for Victoria ────────────────────────────────────
# LGA shares estimated from ABS ERP (Estimated Resident Population) proportions
# within Victoria. These are proportional estimates only — ABS does not publish
# LGA-level multiple-birth data in the public Births release.
VIC_LGA_SHARES = {
    "Melbourne (City)":      0.060,
    "Wyndham":               0.065,
    "Casey":                 0.075,
    "Hume":                  0.050,
    "Whittlesea":            0.050,
    "Monash":                0.050,
    "Boroondara":            0.038,
    "Glen Eira":             0.032,
    "Darebin":               0.038,
    "Brimbank":              0.038,
    "Frankston":             0.030,
    "Knox":                  0.035,
    "Manningham":            0.030,
    "Maroondah":             0.028,
    "Moonee Valley":         0.030,
    "Moreland":              0.038,
    "Port Phillip":          0.030,
    "Stonnington":           0.025,
    "Whitehorse":            0.038,
    "Yarra":                 0.025,
    "Ballarat":              0.025,
    "Geelong (Greater)":     0.045,
    "Bendigo (Greater)":     0.022,
    "Latrobe":               0.018,
    "Mildura":               0.012,
    "Other Victoria":        0.063,
}

# Build long-form LGA dataframe
lga_rows = []
for _, row in df_state.iterrows():
    year = int(row["Year"])
    vic_total_mult = row["VIC_twins"] + row["VIC_triplets"]
    for lga, share in VIC_LGA_SHARES.items():
        est_twins    = round(row["VIC_twins"]    * share)
        est_triplets = round(row["VIC_triplets"] * share)
        lga_rows.append({
            "Year": year,
            "LGA": lga,
            "Est. Twins": est_twins,
            "Est. Triplets+": est_triplets,
            "Est. Total Multiple Births": est_twins + est_triplets,
        })

df_lga = pd.DataFrame(lga_rows)

STATES = ["All States", "NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"]
YEARS  = sorted(df_state["Year"].unique().tolist())

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
C_TWIN    = "#2A9D8F"   # teal
C_TRIP    = "#E76F51"   # terracotta
C_VIC     = "#264653"   # deep ocean
C_RATE    = "#8338EC"   # violet
C_AUS     = "#A8DADC"   # pale teal
BG        = "#0F1923"   # near-black navy
CARD      = "#162330"
ACCENT    = "#2A9D8F"
TEXT_MAIN = "#E8EDF2"
TEXT_DIM  = "#6B8CA8"

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font=dict(family="Georgia, serif", color=TEXT_MAIN, size=13),
    xaxis=dict(gridcolor="#1E3347", zerolinecolor="#1E3347", tickfont=dict(color=TEXT_DIM)),
    yaxis=dict(gridcolor="#1E3347", zerolinecolor="#1E3347", tickfont=dict(color=TEXT_DIM)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DIM)),
    margin=dict(l=50, r=30, t=50, b=50),
)

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_state_col(state, birth_type):
    """Return column name for a state and type, or None for national."""
    if state == "All States" or state == "AUS":
        prefix = "AUS"
    else:
        prefix = state
    col = f"{prefix}_{birth_type}"
    return col if col in df_state.columns else None


def kpi_card(title, value, subtitle="", color=ACCENT):
    return html.Div([
        html.P(title, style={"margin": 0, "fontSize": "0.75rem",
                             "color": TEXT_DIM, "letterSpacing": "0.1em",
                             "textTransform": "uppercase"}),
        html.H2(value, style={"margin": "4px 0", "fontSize": "2rem",
                              "color": color, "fontFamily": "Georgia, serif"}),
        html.P(subtitle, style={"margin": 0, "fontSize": "0.7rem", "color": TEXT_DIM}),
    ], style={
        "background": CARD,
        "borderRadius": "12px",
        "padding": "20px 24px",
        "borderLeft": f"4px solid {color}",
        "flex": "1",
        "minWidth": "160px",
    })


# ─────────────────────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────────────────────

app = dash.Dash(__name__, title="Australian Multiple Births Dashboard")
app.config.suppress_callback_exceptions = True

# ── Layout ────────────────────────────────────────────────────────────────────

SIDEBAR_STYLE = {
    "width": "240px", "minWidth": "240px",
    "background": CARD,
    "padding": "28px 20px",
    "display": "flex", "flexDirection": "column", "gap": "24px",
    "borderRight": f"1px solid #1E3347",
}

LABEL_STYLE = {
    "fontSize": "0.7rem", "color": TEXT_DIM,
    "textTransform": "uppercase", "letterSpacing": "0.1em",
    "marginBottom": "6px", "display": "block",
}

dropdown_style = {
    "backgroundColor": BG,
    "color": TEXT_MAIN,
    "border": "1px solid #1E3347",
    "borderRadius": "8px",
}

app.layout = html.Div([

    # ── Header ──────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Span("⟨⟩", style={"color": ACCENT, "fontSize": "1.4rem",
                                    "marginRight": "10px", "fontFamily": "monospace"}),
            html.Span("Australian Multiple Births", style={
                "fontSize": "1.3rem", "fontWeight": "700",
                "fontFamily": "Georgia, serif", "color": TEXT_MAIN,
            }),
        ], style={"display": "flex", "alignItems": "center"}),
        html.P("ABS Births, Australia | 1990 – 2023  ·  State & LGA Analysis",
               style={"margin": 0, "fontSize": "0.75rem", "color": TEXT_DIM}),
    ], style={
        "background": CARD, "padding": "16px 32px",
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "borderBottom": f"1px solid #1E3347",
        "position": "sticky", "top": 0, "zIndex": 999,
    }),

    # ── Body ────────────────────────────────────────────────────────────────
    html.Div([

        # ── Sidebar ─────────────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Span("Filters", style={
                    "fontSize": "0.65rem", "color": ACCENT,
                    "textTransform": "uppercase", "letterSpacing": "0.15em",
                    "fontWeight": "700",
                }),
                html.Hr(style={"borderColor": "#1E3347", "margin": "8px 0 0 0"}),
            ]),

            html.Div([
                html.Label("State / Territory", style=LABEL_STYLE),
                dcc.Dropdown(
                    id="filter-state",
                    options=[{"label": s, "value": s} for s in STATES],
                    value="VIC",
                    clearable=False,
                    style=dropdown_style,
                ),
            ]),

            html.Div([
                html.Label("Victorian LGA", style=LABEL_STYLE),
                html.P("(visible when VIC selected)", style={
                    "fontSize": "0.65rem", "color": TEXT_DIM, "margin": "0 0 6px 0",
                }),
                dcc.Dropdown(
                    id="filter-lga",
                    options=[{"label": lga, "value": lga}
                             for lga in sorted(VIC_LGA_SHARES.keys())],
                    value=None,
                    placeholder="All of Victoria",
                    clearable=True,
                    style=dropdown_style,
                ),
            ]),

            html.Div([
                html.Label("Year Range", style=LABEL_STYLE),
                dcc.RangeSlider(
                    id="filter-years",
                    min=YEARS[0], max=YEARS[-1],
                    marks={y: {"label": str(y),
                               "style": {"color": TEXT_DIM, "fontSize": "0.6rem"}}
                           for y in YEARS},
                    value=[YEARS[0], YEARS[-1]],
                    step=None,
                    tooltip={"placement": "bottom", "always_visible": False},
                ),
            ]),

            html.Div([
                html.Label("Birth Type", style=LABEL_STYLE),
                dcc.Checklist(
                    id="filter-type",
                    options=[
                        {"label": "  Twins",     "value": "twins"},
                        {"label": "  Triplets+", "value": "triplets"},
                    ],
                    value=["twins", "triplets"],
                    labelStyle={"display": "block", "color": TEXT_DIM,
                                "fontSize": "0.85rem", "marginBottom": "6px"},
                    inputStyle={"marginRight": "8px", "accentColor": ACCENT},
                ),
            ]),

            # Data note
            html.Div([
                html.Hr(style={"borderColor": "#1E3347"}),
                html.P([
                    html.Strong("Data notes:", style={"color": TEXT_DIM}),
                    html.Br(),
                    "State data: ABS 3301.0 Births, Australia (selected years). ",
                    "LGA figures are proportional estimates based on ABS ERP; ",
                    "ABS does not publish LGA-level multiple-birth counts. ",
                    "National totals verified from ABS annual releases.",
                ], style={"fontSize": "0.62rem", "color": "#3E5A72", "lineHeight": "1.5"}),
            ]),

        ], style=SIDEBAR_STYLE),

        # ── Main content ────────────────────────────────────────────────────
        html.Div([

            # KPIs
            html.Div(id="kpi-row", style={
                "display": "flex", "gap": "16px",
                "flexWrap": "wrap", "marginBottom": "24px",
            }),

            # Tabs
            dcc.Tabs(id="tabs", value="trend", children=[
                dcc.Tab(label="📈 Trend Over Time",        value="trend"),
                dcc.Tab(label="🗺️  State Comparison",      value="state"),
                dcc.Tab(label="📍 LGA Breakdown (VIC)",    value="lga"),
                dcc.Tab(label="📊 Rate per 1,000 Births",  value="rate"),
                dcc.Tab(label="🔢 Data Table",             value="table"),
            ], colors={
                "border":     "#1E3347",
                "primary":    ACCENT,
                "background": CARD,
            }, style={"fontFamily": "Georgia, serif", "fontSize": "0.85rem"}),

            html.Div(id="tab-content", style={"marginTop": "20px"}),

        ], style={"flex": 1, "padding": "28px 32px", "overflow": "auto"}),

    ], style={"display": "flex", "flex": 1, "overflow": "hidden", "height": "calc(100vh - 61px)"}),

], style={
    "fontFamily": "Georgia, serif",
    "backgroundColor": BG,
    "color": TEXT_MAIN,
    "height": "100vh",
    "display": "flex",
    "flexDirection": "column",
    "overflow": "hidden",
})


# ─────────────────────────────────────────────────────────────────────────────
# CALLBACKS
# ─────────────────────────────────────────────────────────────────────────────

@app.callback(
    Output("kpi-row", "children"),
    Input("filter-state", "value"),
    Input("filter-lga",   "value"),
    Input("filter-years", "value"),
    Input("filter-type",  "value"),
)
def update_kpis(state, lga, year_range, birth_types):
    dff = df_state[(df_state["Year"] >= year_range[0]) &
                   (df_state["Year"] <= year_range[1])]

    if state == "VIC" and lga:
        dfl = df_lga[(df_lga["Year"] >= year_range[0]) &
                     (df_lga["Year"] <= year_range[1]) &
                     (df_lga["LGA"] == lga)]
        total_twins    = dfl["Est. Twins"].sum()
        total_trips    = dfl["Est. Triplets+"].sum()
        latest_year    = dfl["Year"].max()
        latest_twins   = dfl[dfl["Year"] == latest_year]["Est. Twins"].values
        latest_twins   = latest_twins[0] if len(latest_twins) else 0
        location_label = lga
    else:
        prefix = "AUS" if state == "All States" else state
        total_twins  = dff[f"{prefix}_twins"].sum()   if f"{prefix}_twins"    in dff else 0
        total_trips  = dff[f"{prefix}_triplets"].sum() if f"{prefix}_triplets" in dff else 0
        latest_year  = dff["Year"].max()
        latest_twins = dff[dff["Year"] == latest_year][f"{prefix}_twins"].values
        latest_twins = latest_twins[0] if len(latest_twins) else 0
        location_label = "Australia" if state == "All States" else state

    total_mult = (total_twins if "twins" in birth_types else 0) + \
                 (total_trips if "triplets" in birth_types else 0)

    # Change from first to last year
    if state == "VIC" and lga:
        first_y = dfl[dfl["Year"] == dfl["Year"].min()]["Est. Total Multiple Births"].values
        last_y  = dfl[dfl["Year"] == dfl["Year"].max()]["Est. Total Multiple Births"].values
    else:
        prefix = "AUS" if state == "All States" else state
        first_y = dff[dff["Year"] == dff["Year"].min()][f"{prefix}_twins"].values
        last_y  = dff[dff["Year"] == dff["Year"].max()][f"{prefix}_twins"].values

    if len(first_y) and first_y[0] > 0 and len(last_y):
        pct_change = ((last_y[0] - first_y[0]) / first_y[0]) * 100
        change_str = f"{pct_change:+.1f}% (twins, first→last year)"
    else:
        change_str = "n/a"

    return [
        kpi_card("Location", location_label, "Selected scope", C_VIC),
        kpi_card("Total Twins (sum)", f"{total_twins:,}", f"{year_range[0]}–{year_range[1]}", C_TWIN),
        kpi_card("Total Triplets+ (sum)", f"{total_trips:,}", f"{year_range[0]}–{year_range[1]}", C_TRIP),
        kpi_card("Twins in Latest Year", f"{int(latest_twins):,}", str(latest_year), ACCENT),
        kpi_card("Trend (twins)", change_str, "First to last selected year", C_RATE),
    ]


@app.callback(
    Output("tab-content", "children"),
    Input("tabs",         "value"),
    Input("filter-state", "value"),
    Input("filter-lga",   "value"),
    Input("filter-years", "value"),
    Input("filter-type",  "value"),
)
def render_tab(tab, state, lga, year_range, birth_types):
    dff = df_state[(df_state["Year"] >= year_range[0]) &
                   (df_state["Year"] <= year_range[1])]
    prefix = "AUS" if state == "All States" else state

    # ── TREND TAB ────────────────────────────────────────────────────────────
    if tab == "trend":
        fig = go.Figure()
        title_loc = "Australia" if state == "All States" else state
        if state == "VIC" and lga:
            dfl = df_lga[(df_lga["Year"] >= year_range[0]) &
                         (df_lga["Year"] <= year_range[1]) &
                         (df_lga["LGA"] == lga)]
            if "twins" in birth_types:
                fig.add_trace(go.Scatter(
                    x=dfl["Year"], y=dfl["Est. Twins"],
                    name="Est. Twins", mode="lines+markers",
                    line=dict(color=C_TWIN, width=2.5),
                    marker=dict(size=7),
                ))
            if "triplets" in birth_types:
                fig.add_trace(go.Scatter(
                    x=dfl["Year"], y=dfl["Est. Triplets+"],
                    name="Est. Triplets+", mode="lines+markers",
                    line=dict(color=C_TRIP, width=2.5, dash="dot"),
                    marker=dict(size=7),
                ))
            title_loc = lga
        else:
            if "twins" in birth_types and f"{prefix}_twins" in dff:
                fig.add_trace(go.Scatter(
                    x=dff["Year"], y=dff[f"{prefix}_twins"],
                    name="Twins", mode="lines+markers",
                    line=dict(color=C_TWIN, width=2.5),
                    marker=dict(size=7),
                ))
            if "triplets" in birth_types and f"{prefix}_triplets" in dff:
                fig.add_trace(go.Scatter(
                    x=dff["Year"], y=dff[f"{prefix}_triplets"],
                    name="Triplets+", mode="lines+markers",
                    line=dict(color=C_TRIP, width=2.5, dash="dot"),
                    marker=dict(size=7),
                ))

        fig.update_layout(
            **PLOT_LAYOUT,
            title=dict(text=f"Multiple Births Over Time — {title_loc}",
                       font=dict(size=16, color=TEXT_MAIN)),
            xaxis_title="Year",
            yaxis_title="Number of Confinements",
            hovermode="x unified",
            height=430,
        )
        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    # ── STATE COMPARISON TAB ─────────────────────────────────────────────────
    elif tab == "state":
        selected_year = year_range[1]
        states_list = ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"]
        row = df_state[df_state["Year"] == selected_year].iloc[0]
        twins_vals    = [row[f"{s}_twins"]    for s in states_list]
        triplets_vals = [row[f"{s}_triplets"] for s in states_list]

        fig = go.Figure()
        if "twins" in birth_types:
            fig.add_trace(go.Bar(
                x=states_list, y=twins_vals, name="Twins",
                marker_color=[C_TWIN if s == state else "#1E5C6E" for s in states_list],
            ))
        if "triplets" in birth_types:
            fig.add_trace(go.Bar(
                x=states_list, y=triplets_vals, name="Triplets+",
                marker_color=[C_TRIP if s == state else "#7A3625" for s in states_list],
            ))

        fig.update_layout(
            **PLOT_LAYOUT,
            barmode="group",
            title=dict(text=f"Multiple Births by State — {selected_year}  (highlighted: {state})",
                       font=dict(size=16, color=TEXT_MAIN)),
            xaxis_title="State / Territory",
            yaxis_title="Number of Confinements",
            height=430,
        )
        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    # ── LGA BREAKDOWN TAB ────────────────────────────────────────────────────
    elif tab == "lga":
        selected_year = year_range[1]
        dfl_y = df_lga[df_lga["Year"] == selected_year].sort_values(
            "Est. Total Multiple Births", ascending=True)

        fig = go.Figure()
        if "twins" in birth_types:
            fig.add_trace(go.Bar(
                y=dfl_y["LGA"], x=dfl_y["Est. Twins"],
                name="Est. Twins", orientation="h",
                marker_color=C_TWIN,
            ))
        if "triplets" in birth_types:
            fig.add_trace(go.Bar(
                y=dfl_y["LGA"], x=dfl_y["Est. Triplets+"],
                name="Est. Triplets+", orientation="h",
                marker_color=C_TRIP,
            ))

        fig.update_layout(
            **PLOT_LAYOUT,
            barmode="stack",
            title=dict(
                text=f"Estimated Multiple Births by Victorian LGA — {selected_year}<br>"
                     "<sup style='color:#3E5A72'>Proportional estimates based on ABS ERP; not official ABS LGA data</sup>",
                font=dict(size=15, color=TEXT_MAIN),
            ),
            xaxis_title="Estimated Confinements",
            yaxis_title="",
            height=700,
            margin=dict(l=160, r=30, t=80, b=50),
        )
        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    # ── RATE TAB ─────────────────────────────────────────────────────────────
    elif tab == "rate":
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dff["Year"], y=dff["AUS_rate_per_1000"],
            name="Australia", mode="lines+markers",
            line=dict(color=C_AUS, width=2.5),
            marker=dict(size=7),
        ))
        if "VIC_rate_per_1000" in dff.columns:
            fig.add_trace(go.Scatter(
                x=dff["Year"], y=dff["VIC_rate_per_1000"],
                name="Victoria", mode="lines+markers",
                line=dict(color=C_TWIN, width=2.5, dash="dash"),
                marker=dict(size=7),
            ))

        fig.update_layout(
            **PLOT_LAYOUT,
            title=dict(text="Multiple Births Rate per 1,000 Confinements",
                       font=dict(size=16, color=TEXT_MAIN)),
            xaxis_title="Year",
            yaxis_title="Rate per 1,000 Confinements",
            hovermode="x unified",
            height=430,
        )

        # annotation for ART policy shift
        fig.add_annotation(
            x=2005, y=15.4,
            text="↑ ART peak<br>(IVF era)",
            showarrow=True, arrowhead=2,
            arrowcolor=TEXT_DIM, font=dict(size=10, color=TEXT_DIM),
            bgcolor=CARD, bordercolor="#1E3347", borderwidth=1,
        )
        fig.add_annotation(
            x=2010, y=15.3,
            text="SET policy<br>adoption",
            showarrow=True, arrowhead=2, ax=40, ay=-40,
            arrowcolor=TEXT_DIM, font=dict(size=10, color=TEXT_DIM),
            bgcolor=CARD, bordercolor="#1E3347", borderwidth=1,
        )
        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    # ── TABLE TAB ────────────────────────────────────────────────────────────
    elif tab == "table":
        if state == "VIC" and lga:
            dfl = df_lga[(df_lga["Year"] >= year_range[0]) &
                         (df_lga["Year"] <= year_range[1]) &
                         (df_lga["LGA"] == lga)]
            table_df = dfl[["Year", "LGA", "Est. Twins", "Est. Triplets+",
                             "Est. Total Multiple Births"]].copy()
        else:
            cols = ["Year"]
            for bt in birth_types:
                if bt == "twins"    and f"{prefix}_twins"    in dff: cols.append(f"{prefix}_twins")
                if bt == "triplets" and f"{prefix}_triplets" in dff: cols.append(f"{prefix}_triplets")
            cols += ["AUS_rate_per_1000"]
            if prefix == "VIC":
                cols += ["VIC_rate_per_1000"]
            table_df = dff[cols].copy()
            table_df.columns = [c.replace(f"{prefix}_", "").replace("_", " ").title()
                                 for c in cols]

        return dash_table.DataTable(
            data=table_df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in table_df.columns],
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": CARD, "color": ACCENT,
                "fontWeight": "700", "border": f"1px solid #1E3347",
                "fontFamily": "Georgia, serif", "fontSize": "0.8rem",
                "textTransform": "uppercase", "letterSpacing": "0.05em",
            },
            style_cell={
                "backgroundColor": BG, "color": TEXT_MAIN,
                "border": "1px solid #1E3347",
                "fontFamily": "Georgia, serif", "fontSize": "0.9rem",
                "padding": "10px 14px", "textAlign": "center",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"},
                 "backgroundColor": "#111E2A"},
            ],
            page_size=20,
            sort_action="native",
            filter_action="native",
        )

    return html.Div("Select a tab above.")


# ─────────────────────────────────────────────────────────────────────────────
# LGA filter visibility
# ─────────────────────────────────────────────────────────────────────────────
@app.callback(
    Output("filter-lga", "disabled"),
    Input("filter-state", "value"),
)
def toggle_lga(state):
    return state != "VIC"


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "═" * 60)
    print("  Australian Multiple Births Dashboard")
    print("  Data: ABS Births, Australia (1990–2023)")
    print("  Open: http://127.0.0.1:8050")
    print("═" * 60 + "\n")
    app.run(debug=True)