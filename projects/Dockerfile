ARG LANGUAGE=koalaman/shellcheck-alpine
ARG VERSION=latest
FROM ${LANGUAGE}:${VERSION}

ARG PROJECT=test
COPY ./${PROJECT} /project
COPY ./.harvey /harvey/.harvey

WORKDIR /project

CMD [ "/bin/sh", "./harvey.sh" ]
