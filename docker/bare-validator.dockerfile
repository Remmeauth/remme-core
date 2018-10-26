FROM remme/sawtooth-bare-validator:latest
ARG SAWTOOTH_REPO_GIT_REF
RUN echo $SAWTOOTH_REPO_GIT_REF
RUN echo $SAWTOOTH_REPO_GIT_REF > /git-ref
