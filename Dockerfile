FROM ghcr.io/identicum/python-flask:latest

COPY ./app/ /app

ENV LOG_LEVEL="INFO" \
    LOGOUT_URL="/private/logout" \
    SELFSERVICE_URL="" \
    CAMPUS_NAME="Campus Virtual" \
    INSTITUTION_NAME="Universidad Demo" \
    SHOW_TECH_DETAILS="true"
