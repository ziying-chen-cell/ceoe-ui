
from __future__ import annotations

from dash import Dash, dcc, html, Input, Output, State, dash_table, ctx
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent
COURSES = pd.read_csv(BASE / "data" / "courses.csv")
ASSIGNMENTS = pd.read_csv(BASE / "data" / "assignments.csv")

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="CEOE | Course Enrollment Optimization Engine",
)

def metric_card(title, value, subtitle=""):
    return dbc.Card(
        dbc.CardBody([
            html.Div(title, className="metric-title"),
            html.Div(value, className="metric-value"),
            html.Div(subtitle, className="metric-subtitle"),
        ]),
        className="metric-card h-100"
    )

def section_title(title, subtitle=None):
    return html.Div([
        html.H3(title, className="section-title"),
        html.P(subtitle, className="section-subtitle") if subtitle else None
    ], className="mb-3")

PAGE_PATHS = {
    "home": "/",
    "phase1-student": "/student-ranking",
    "phase1-admin": "/admin-optimization",
    "phase1-results": "/initial-results",
    "phase2-student": "/my-enrollment",
    "phase2-adjust": "/dynamic-adjustment",
}
PATH_TO_PAGE = {path: page for page, path in PAGE_PATHS.items()}

def nav_button(label, page, icon):
    return dcc.Link(
        [html.Span(icon, className="me-2"), label],
        href=PAGE_PATHS[page],
        className="nav-btn w-100 text-start d-block"
    )

sidebar = html.Div([
    html.Div([
        html.Div("CEOE", className="brand"),
        html.Div("Course Enrollment Optimization Engine", className="brand-subtitle")
    ], className="brand-block"),

    html.Div("OVERVIEW", className="nav-label"),
    nav_button("Home", "home", "⌂"),

    html.Div("PHASE 1", className="nav-label mt-4"),
    nav_button("Student Ranking", "phase1-student", "①"),
    nav_button("Admin Optimization", "phase1-admin", "⚙"),
    nav_button("Initial Results", "phase1-results", "▦"),

    html.Div("PHASE 2", className="nav-label mt-4"),
    nav_button("My Enrollment", "phase2-student", "②"),
    nav_button("Dynamic Adjustment", "phase2-adjust", "↻"),
], className="sidebar")

header = html.Div([
    html.Div([
        html.Div("Summer 2026 Prototype", className="header-kicker"),
        html.H2("IEOR Course Enrollment Optimization Engine", className="header-title")
    ]),
    html.Div([
        dbc.Badge("Phase 1 + Phase 2", color="warning", text_color="dark", className="me-2"),
        dbc.Badge("Plotly Dash", color="primary")
    ])
], className="top-header")

home_page = html.Div([
    section_title(
        "Two-Phase Enrollment Workflow",
        "The prototype separates initial global allocation from later real-time enrollment adjustments."
    ),
    dbc.Row([
        dbc.Col(metric_card("Phase 1", "Global Allocation", "Students rank preferences; admin runs MILP."), md=4),
        dbc.Col(metric_card("Phase 2", "Dynamic Adjustment", "Students add, drop, waitlist, or set smart swaps."), md=4),
        dbc.Col(metric_card("Current integration", "UI Prototype", "Backend calls are represented with demo logic."), md=4),
    ], className="g-3 mb-4"),

    dbc.Card(dbc.CardBody([
        html.Div(className="workflow", children=[
            html.Div(["Student Ranking", html.Span("→")], className="workflow-step"),
            html.Div(["Preference Store", html.Span("→")], className="workflow-step"),
            html.Div(["MILP Allocation", html.Span("→")], className="workflow-step"),
            html.Div(["Initial Roster", html.Span("→")], className="workflow-step"),
            html.Div(["Add / Drop / Waitlist", html.Span("→")], className="workflow-step"),
            html.Div(["Final Enrollment"], className="workflow-step"),
        ])
    ]), className="panel-card mb-4"),

    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div("PHASE 1", className="eyebrow"),
            html.H4("Static preference elicitation"),
            html.P("Students submit ranked preferences during a collection window. No optimization is triggered at submission time."),
            dcc.Link("Open Student Ranking", href=PAGE_PATHS["phase1-student"], className="btn btn-primary")
        ]), className="panel-card h-100"), md=6),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div("PHASE 2", className="eyebrow"),
            html.H4("Dynamic adjustment"),
            html.P("After initial assignment, students manage add/drop activity and may set conditional smart swap rules."),
            dcc.Link("Open Dynamic Adjustment", href=PAGE_PATHS["phase2-adjust"], className="btn btn-warning text-dark")
        ]), className="panel-card h-100"), md=6)
    ], className="g-3")
])

course_options = [
    {"label": f"{r.course_id} · {r.units}u · {r.time_slot}", "value": r.course_id}
    for r in COURSES.itertuples()
]

student_page = html.Div([
    section_title(
        "Phase 1 · Student Preference Ranking",
        "Students submit true ordinal preferences. This page records preference data only; optimization runs later from the admin portal."
    ),
    dbc.Row([
        dbc.Col([
            dbc.Card(dbc.CardBody([
                dbc.Label("Student ID"),
                dbc.Input(id="student-id", placeholder="e.g. 3035123456"),
                dbc.Label("Program", className="mt-3"),
                dcc.Dropdown(
                    id="program-select",
                    options=[
                        {"label": "Master of Analytics", "value": "MAnalytics"},
                        {"label": "MEng IEOR", "value": "MEng"},
                        {"label": "MS / PhD IEOR", "value": "MSPhD"},
                    ],
                    value="MAnalytics",
                    clearable=False
                ),
                dbc.Checklist(
                    id="graduating-check",
                    options=[{"label": "Graduating this academic year", "value": "yes"}],
                    value=[],
                    className="mt-3"
                )
            ]), className="panel-card"),
            dbc.Card(dbc.CardBody([
                html.Div("Submission rule", className="eyebrow"),
                html.P("Rank six unique courses. Rank 1 is your highest preference."),
                html.Div("No solver runs when you submit.", className="callout")
            ]), className="panel-card mt-3")
        ], md=4),

        dbc.Col([
            dbc.Card(dbc.CardBody([
                html.H5("Rank your elective preferences", className="mb-3"),
                html.Div([
                    dbc.Row([
                        dbc.Col(html.Div(str(i), className="rank-badge"), width="auto"),
                        dbc.Col(dcc.Dropdown(
                            id=f"rank-{i}",
                            options=course_options,
                            placeholder=f"Select Rank {i}"
                        ))
                    ], align="center", className="g-2 mb-3")
                    for i in range(1, 7)
                ]),
                dbc.Button("Submit Preferences", id="submit-preferences", color="primary", className="mt-2"),
                html.Div(id="student-submit-msg", className="mt-3")
            ]), className="panel-card")
        ], md=8)
    ], className="g-3")
])

admin_page = html.Div([
    section_title(
        "Phase 1 · Admin Optimization",
        "After the ranking window closes, administrators review configuration and trigger one cohort-wide allocation run."
    ),
    dbc.Row([
        dbc.Col(metric_card("Students", "250", "Demo cohort"), md=3),
        dbc.Col(metric_card("Courses", str(len(COURSES)), "Spring elective set"), md=3),
        dbc.Col(metric_card("Max units", "12", "Phase 1 unit budget"), md=3),
        dbc.Col(metric_card("Fairness weight", "0.25", "Blended welfare / maximin"), md=3),
    ], className="g-3 mb-4"),

    dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col([
                dbc.Label("Semester"),
                dcc.Dropdown(
                    options=[{"label": "Spring 2026", "value": "2026"}],
                    value="2026", clearable=False
                )
            ], md=3),
            dbc.Col([dbc.Label("Max Phase 1 units"), dbc.Input(id="max-units", type="number", value=12)], md=3),
            dbc.Col([dbc.Label("Minimum course load"), dbc.Input(id="min-courses", type="number", value=3)], md=3),
            dbc.Col([dbc.Label("Fairness weight"), dbc.Input(id="fairness-weight", type="number", min=0, max=1, step=0.05, value=0.25)], md=3),
        ], className="g-3"),
        html.Hr(),
        html.Div([
            html.Div([
                html.Div("Data status", className="eyebrow"),
                html.Div("Course catalog loaded", className="status-good"),
                html.Div("Student preferences loaded", className="status-good"),
                html.Div("MILP backend: demo mode", className="status-demo"),
            ]),
            dbc.Button("Execute Global Optimization", id="run-optimization", color="danger", size="lg")
        ], className="d-flex justify-content-between align-items-end"),
        html.Div(id="admin-run-msg", className="mt-3")
    ]), className="panel-card mb-4"),

    dbc.Card(dbc.CardBody([
        html.H5("Course configuration preview"),
        dash_table.DataTable(
            data=COURSES.to_dict("records"),
            columns=[{"name": c.replace("_"," ").title(), "id": c} for c in COURSES.columns],
            page_size=8,
            style_table={"overflowX": "auto"},
            style_cell={"fontFamily": "Inter, Arial", "fontSize": "13px", "padding": "10px"},
            style_header={"fontWeight": "700", "backgroundColor": "#f6f7f9"},
            sort_action="native",
            filter_action="native"
        )
    ]), className="panel-card")
])

results_page = html.Div([
    section_title(
        "Phase 1 · Initial Allocation Results",
        "Optimization output is translated into department-ready rosters and student schedules."
    ),
    dbc.Row([
        dbc.Col(metric_card("Solver status", "Optimal", "Demo output"), md=3),
        dbc.Col(metric_card("Worst-off satisfaction", "73%", "Normalized achievable utility"), md=3),
        dbc.Col(metric_card("Rank 1 received", "96.4%", "Demo model validation result"), md=3),
        dbc.Col(metric_card("Gini", "0.040", "Lower indicates more even outcomes"), md=3),
    ], className="g-3 mb-4"),

    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Course Roster"),
            dcc.Dropdown(
                id="roster-course",
                options=[{"label": c, "value": c} for c in sorted(ASSIGNMENTS.course_id.unique())],
                value=sorted(ASSIGNMENTS.course_id.unique())[0],
                clearable=False
            ),
            html.Div(id="roster-table", className="mt-3")
        ]), className="panel-card h-100"), md=6),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Student Schedule"),
            dcc.Dropdown(
                id="schedule-student",
                options=[{"label": s, "value": s} for s in sorted(ASSIGNMENTS.student_id.unique())],
                value=sorted(ASSIGNMENTS.student_id.unique())[0],
                clearable=False
            ),
            html.Div(id="student-schedule", className="mt-3")
        ]), className="panel-card h-100"), md=6),
    ], className="g-3")
])

phase2_student_page = html.Div([
    section_title(
        "Phase 2 · My Enrollment",
        "Student enrollment state after Phase 1 assignment."
    ),
    dbc.Row([
        dbc.Col(metric_card("Current units", "10 / 12", "Phase 2 demo state"), md=3),
        dbc.Col(metric_card("Enrolled courses", "3", "Current schedule"), md=3),
        dbc.Col(metric_card("Waitlisted", "1", "Pending course"), md=3),
        dbc.Col(metric_card("Active swap rules", "1", "Conditional automation"), md=3),
    ], className="g-3 mb-4"),
    dbc.Card(dbc.CardBody([
        html.H5("Current enrollment"),
        dash_table.DataTable(
            data=[
                {"course":"INDENG 230","status":"Enrolled","units":3,"time":"Tu/Th 3:30–4:59 PM"},
                {"course":"INDENG 242B","status":"Enrolled","units":4,"time":"Tu/Th 5:00–6:29 PM"},
                {"course":"INDENG 222","status":"Enrolled","units":3,"time":"We 5:00–7:59 PM"},
                {"course":"INDENG 256","status":"Waitlist","units":3,"time":"Tu/Th 12:30–1:59 PM"},
            ],
            columns=[{"name": c.title(), "id": c} for c in ["course","status","units","time"]],
            style_cell={"fontFamily":"Inter, Arial","fontSize":"13px","padding":"10px"},
            style_header={"fontWeight":"700","backgroundColor":"#f6f7f9"}
        )
    ]), className="panel-card")
])

adjust_page = html.Div([
    section_title(
        "Phase 2 · Dynamic Adjustment",
        "Every action should be checked against units, schedule conflicts, and seat availability."
    ),
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div("ADD / DROP", className="eyebrow"),
            html.H5("Course action"),
            dcc.Dropdown(id="phase2-course", options=course_options, placeholder="Choose a course"),
            dbc.ButtonGroup([
                dbc.Button("Add / Join Waitlist", id="phase2-add", color="primary"),
                dbc.Button("Drop", id="phase2-drop", color="outline-danger"),
            ], className="mt-3"),
            html.Div(id="phase2-action-msg", className="mt-3")
        ]), className="panel-card h-100"), md=6),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div("SMART SWAP", className="eyebrow"),
            html.H5("Set conditional swap"),
            dbc.Label("If admitted to"),
            dcc.Dropdown(id="swap-target", options=course_options, placeholder="Waitlisted target course"),
            dbc.Label("Automatically drop", className="mt-3"),
            dcc.Dropdown(id="swap-source", options=course_options, placeholder="Current enrolled course"),
            dbc.Button("Set Smart Swap", id="set-swap", color="warning", className="mt-3 text-dark"),
            html.Div(id="swap-msg", className="mt-3")
        ]), className="panel-card h-100"), md=6)
    ], className="g-3")
])

pages = {
    "home": home_page,
    "phase1-student": student_page,
    "phase1-admin": admin_page,
    "phase1-results": results_page,
    "phase2-student": phase2_student_page,
    "phase2-adjust": adjust_page,
}

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="submitted-preferences", data={}),
    sidebar,
    html.Div([
        header,
        html.Div(id="page-content", className="content-wrap")
    ], className="main-area")
], className="app-shell")

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page(pathname):
    page = PATH_TO_PAGE.get(pathname, "home")
    return pages.get(page, home_page)

@app.callback(
    Output("student-submit-msg", "children"),
    Output("submitted-preferences", "data"),
    Input("submit-preferences", "n_clicks"),
    State("student-id", "value"),
    State("program-select", "value"),
    State("graduating-check", "value"),
    *[State(f"rank-{i}", "value") for i in range(1, 7)],
    prevent_initial_call=True
)
def submit_preferences(n, sid, program, graduating, *ranks):
    if not sid or not sid.strip():
        return dbc.Alert("Please enter a student ID.", color="danger"), {}
    if any(r is None for r in ranks):
        return dbc.Alert("Please complete all six rankings.", color="danger"), {}
    if len(set(ranks)) != len(ranks):
        return dbc.Alert("Each course may only appear once.", color="danger"), {}
    payload = {
        "student_id": sid.strip(),
        "program": program,
        "graduating": "yes" in (graduating or []),
        "ranking": list(ranks)
    }
    return dbc.Alert(
        "Preferences recorded successfully. No optimization was executed at submission time.",
        color="success"
    ), payload

@app.callback(
    Output("admin-run-msg", "children"),
    Input("run-optimization", "n_clicks"),
    prevent_initial_call=True
)
def run_demo_optimization(n):
    return dbc.Alert(
        [html.Strong("Optimization completed. "),
         "Demo solver status: Optimal. Open “Initial Results” to review rosters and schedules."],
        color="success"
    )

@app.callback(
    Output("roster-table", "children"),
    Input("roster-course", "value")
)
def render_roster(course):
    df = ASSIGNMENTS[ASSIGNMENTS.course_id == course][["student_id","rank","utility"]]
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[
            {"name":"Student ID","id":"student_id"},
            {"name":"Submitted Rank","id":"rank"},
            {"name":"Utility","id":"utility"},
        ],
        style_cell={"fontFamily":"Inter, Arial","fontSize":"13px","padding":"9px"},
        style_header={"fontWeight":"700","backgroundColor":"#f6f7f9"}
    )

@app.callback(
    Output("student-schedule", "children"),
    Input("schedule-student", "value")
)
def render_schedule(student):
    df = ASSIGNMENTS[ASSIGNMENTS.student_id == student][["course_id","rank","utility"]]
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[
            {"name":"Course","id":"course_id"},
            {"name":"Submitted Rank","id":"rank"},
            {"name":"Utility","id":"utility"},
        ],
        style_cell={"fontFamily":"Inter, Arial","fontSize":"13px","padding":"9px"},
        style_header={"fontWeight":"700","backgroundColor":"#f6f7f9"}
    )

@app.callback(
    Output("phase2-action-msg", "children"),
    Input("phase2-add", "n_clicks"),
    Input("phase2-drop", "n_clicks"),
    State("phase2-course", "value"),
    prevent_initial_call=True
)
def phase2_action(add_clicks, drop_clicks, course):
    if not course:
        return dbc.Alert("Choose a course first.", color="danger")
    if ctx.triggered_id == "phase2-add":
        return dbc.Alert(
            f"{course}: demo validation passed. Capacity, units, and time-conflict checks will run before the production state update.",
            color="info"
        )
    return dbc.Alert(f"{course}: demo drop action recorded.", color="warning")

@app.callback(
    Output("swap-msg", "children"),
    Input("set-swap", "n_clicks"),
    State("swap-target", "value"),
    State("swap-source", "value"),
    prevent_initial_call=True
)
def set_swap_rule(n, target, source):
    if not target or not source:
        return dbc.Alert("Select both a target course and a course to drop.", color="danger")
    if target == source:
        return dbc.Alert("Target and drop course must be different.", color="danger")
    return dbc.Alert(
        f"Smart Swap set: if admitted to {target}, automatically drop {source}.",
        color="success"
    )

if __name__ == "__main__":
    app.run(debug=True, port=8050)
