ARG LANGUAGE=koalaman/shellcheck-alpine
ARG VERSION=latest
FROM ${LANGUAGE}:${VERSION}

ARG PROJECT=test
COPY ./${PROJECT} /project

WORKDIR /project

CMD [ "/bin/sh", "./harvey.sh" ]
