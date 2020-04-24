ARG LANGUAGE=koalaman/shellcheck-alpine
ARG VERSION=latest
FROM ${LANGUAGE}:${VERSION}

ARG PROJECT=
COPY ./projects/${PROJECT} /project

CMD [ "/bin/sh", "./project/harvey.sh" ]
