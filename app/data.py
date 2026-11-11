"""
Static mock data for the dashboard. Dates are relative to today, so the demo never looks stale.
"""

from datetime import date, timedelta

MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
WEEKDAYS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]


def _due(days):
    d = date.today() + timedelta(days=days)
    if days == 0:
        when = "hoy"
    elif days == 1:
        when = "mañana"
    elif days == -1:
        when = "ayer"
    elif days > 0:
        when = f"en {days} días"
    else:
        when = f"hace {-days} días"
    return {"date": f"{WEEKDAYS[d.weekday()]} {d.day} {MONTHS[d.month - 1]}", "when": when, "urgent": 0 <= days <= 2}


# LMS_STUDENT
STUDENT_COURSES = [
    {"code": "MAT101", "name": "Análisis Matemático I", "teacher": "Dra. Laura Méndez", "progress": 72, "color": "primary"},
    {"code": "PRG201", "name": "Programación II", "teacher": "Ing. Martín Rossi", "progress": 45, "color": "success"},
    {"code": "BDD210", "name": "Bases de Datos", "teacher": "Lic. Carla Suárez", "progress": 88, "color": "info"},
    {"code": "ING105", "name": "Inglés Técnico", "teacher": "Prof. Daniel Ortiz", "progress": 20, "color": "warning"},
]


def upcoming_deliverables():
    items = [
        (1, "PRG201", "TP 3 - Listas enlazadas", "Trabajo práctico"),
        (3, "MAT101", "Cuestionario: Límites y continuidad", "Cuestionario"),
        (6, "BDD210", "Modelo entidad-relación del caso de estudio", "Entrega grupal"),
        (10, "ING105", "Reading comprehension - Unit 2", "Tarea"),
    ]
    return [dict(_due(days), course=course, title=title, kind=kind) for days, course, title, kind in items]


# LMS_TEACHER
TEACHER_COURSES = [
    {"code": "PRG201", "name": "Programación II", "commission": "Comisión A - Turno mañana", "students": 48, "to_grade": 17},
    {"code": "PRG305", "name": "Algoritmos Avanzados", "commission": "Comisión única - Turno noche", "students": 31, "to_grade": 6},
]


def pending_grading():
    items = [
        (-2, "PRG201", "TP 2 - Recursividad", 12, 48),
        (-1, "PRG305", "Parcial 1 - Grafos", 6, 31),
        (1, "PRG201", "TP 3 - Listas enlazadas", 5, 48),
    ]
    return [dict(_due(days), course=course, title=title, pending=pending, total=total) for days, course, title, pending, total in items]


# LMS_ADMIN
ADMIN_STATS = [
    {"label": "Usuarios activos", "value": "3.482", "icon": "bi-people"},
    {"label": "Cursos publicados", "value": "126", "icon": "bi-collection"},
    {"label": "Inscripciones del cuatrimestre", "value": "9.215", "icon": "bi-person-check"},
    {"label": "Docentes", "value": "214", "icon": "bi-person-badge"},
]


def admin_activity():
    return [
        {"when": "hace 12 min", "text": "Se sincronizaron 37 usuarios nuevos desde el sistema académico."},
        {"when": "hace 1 h", "text": "Se creó el curso \"Seguridad Informática\" (SEG401)."},
        {"when": "hace 3 h", "text": "Se asignó el rol Docente a 2 usuarios."},
        {"when": "ayer", "text": "Cierre de inscripciones del cuatrimestre."},
    ]
