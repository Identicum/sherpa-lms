"""
Mock LMS ("Campus Virtual") for Sherpa-IAM demos.
Runs behind IPAx, which handles OIDC authentication and passes the user in HTTP headers:
IPAx-USERNAME (required), IPAx-ROLES ('|' separated) and, optionally, IPAx-NAME and IPAx-EMAIL.
What the dashboard shows depends on the LMS_* roles; a user without any of them gets an access denied page.
"""

import os

from flask import Flask, g, render_template, request
from sherpa.utils.basics import Logger

import data

app = Flask(__name__)

log_level = os.environ.get("LOG_LEVEL", "")
# log outputs to /tmp/python-flask.log, redirected to /dev/stdout in the parent image
logger = Logger("sherpa-lms", log_level=log_level, log_path="/tmp/python-flask.log")
logger.info("Logger initialized with level: {}.", log_level)

HEADER_USERNAME = os.environ.get("HEADER_USERNAME", "IPAx-USERNAME")
HEADER_ROLES = os.environ.get("HEADER_ROLES", "IPAx-ROLES")
HEADER_NAME = os.environ.get("HEADER_NAME", "IPAx-NAME")
HEADER_EMAIL = os.environ.get("HEADER_EMAIL", "IPAx-EMAIL")
ROLES_SEPARATOR = os.environ.get("ROLES_SEPARATOR", "|")
LOGOUT_URL = os.environ.get("LOGOUT_URL", "/private/logout")
SELFSERVICE_URL = os.environ.get("SELFSERVICE_URL", "")
CAMPUS_NAME = os.environ.get("CAMPUS_NAME", "Campus Virtual")
INSTITUTION_NAME = os.environ.get("INSTITUTION_NAME", "Universidad Demo")
SHOW_TECH_DETAILS = os.environ.get("SHOW_TECH_DETAILS", "true").lower() in ("1", "true", "yes")

ROLE_STUDENT = "LMS_STUDENT"
ROLE_TEACHER = "LMS_TEACHER"
ROLE_ADMIN = "LMS_ADMIN"
# Each role unlocks one section of the dashboard. Order is the order on the page.
ROLE_SECTIONS = [
    {"role": ROLE_STUDENT, "label": "Estudiante", "section": "Mis cursos y próximas entregas", "anchor": "estudiante", "icon": "bi-journal-bookmark"},
    {"role": ROLE_TEACHER, "label": "Docente", "section": "Cursos a cargo y correcciones", "anchor": "docente", "icon": "bi-person-video3"},
    {"role": ROLE_ADMIN, "label": "Administrador", "section": "Administración del campus", "anchor": "admin", "icon": "bi-gear"},
]
LMS_ROLES = {s["role"] for s in ROLE_SECTIONS}
# Headers shown in the "Detalle técnico" panel, besides the identity headers.
CONTEXT_HEADERS = ["Host", "X-Forwarded-Host", "X-Forwarded-Proto", "X-Forwarded-For", "X-Real-IP"]


def get_roles():
    raw = request.headers.get(HEADER_ROLES, "")
    return [r.strip() for r in raw.split(ROLES_SEPARATOR) if r.strip()]


def get_tech_headers():
    identity = [HEADER_USERNAME, HEADER_NAME, HEADER_EMAIL, HEADER_ROLES]
    headers = [(h, request.headers.get(h)) for h in identity]
    # any other header injected by IPAx (IPAx-*)
    seen = {h.lower() for h in identity}
    for name, value in request.headers.items():
        if name.lower().startswith("ipax-") and name.lower() not in seen:
            headers.append((name, value))
            seen.add(name.lower())
    headers += [(h, request.headers.get(h)) for h in CONTEXT_HEADERS if request.headers.get(h)]
    return headers


@app.context_processor
def inject_globals():
    return {
        "campus_name": CAMPUS_NAME,
        "institution_name": INSTITUTION_NAME,
        "logout_url": LOGOUT_URL,
        "selfservice_url": SELFSERVICE_URL,
        "show_tech_details": SHOW_TECH_DETAILS,
        "header_roles": HEADER_ROLES,
        "roles_separator": ROLES_SEPARATOR,
        "role_sections": ROLE_SECTIONS,
    }


@app.before_request
def load_user():
    if request.endpoint in ("health", "static"):
        return None
    g.username = request.headers.get(HEADER_USERNAME, "").strip()
    g.display_name = request.headers.get(HEADER_NAME, "").strip() or g.username
    g.roles = get_roles()
    g.lms_roles = set(g.roles) & LMS_ROLES
    g.tech_headers = get_tech_headers()
    if not g.username:
        logger.warn("Request to {} without {} header.", request.path, HEADER_USERNAME)
        return render_template("unauthenticated.html", header_username=HEADER_USERNAME), 401
    if not g.lms_roles:
        logger.info("User {} has no LMS role (roles: {}), access denied.", g.username, g.roles)
        return render_template("denied.html"), 403
    return None


@app.route("/")
def dashboard():
    logger.debug("Dashboard for {} with LMS roles {}.", g.username, sorted(g.lms_roles))
    return render_template(
        "dashboard.html",
        is_student=ROLE_STUDENT in g.lms_roles,
        is_teacher=ROLE_TEACHER in g.lms_roles,
        is_admin=ROLE_ADMIN in g.lms_roles,
        student_courses=data.STUDENT_COURSES,
        deliverables=data.upcoming_deliverables(),
        teacher_courses=data.TEACHER_COURSES,
        to_grade=data.pending_grading(),
        admin_stats=data.ADMIN_STATS,
        admin_activity=data.admin_activity(),
    )


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
