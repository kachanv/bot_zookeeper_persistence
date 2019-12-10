FROM python:3.6-alpine
ADD requirements.txt .
RUN BUILD_DEPS='gcc musl-dev' \
    && RUNTIME_DEPS='libffi-dev openssl-dev' \
    && apk add --no-cache $BUILD_DEPS $RUNTIME_DEPS \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del --no-cache $BUILD_DEPS \
    && rm -rf /tmp/*
