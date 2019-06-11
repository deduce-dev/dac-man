FROM ubuntu:18.04

ARG USER=deduce
ENV USER ${USER}

ENV DEBIAN_FRONTEND=noninteractive \
    USER_HOME=/home/${USER} \ 
    HOME=/home/${USER}

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends sudo apt-utils && \
    apt-get install -y --no-install-recommends openssh-server \
        python3-dev python3-pip redis-tools iperf vim

#### ADD DEFAULT USER ####
RUN adduser --disabled-password --gecos "" ${USER} && \
    echo "${USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN chown -R ${USER}:${USER} ${USER_HOME}

#### CREATE WORKING DIRECTORY FOR USER ####
ARG WORKDIR=/project
ENV WORKDIR ${WORKDIR}
RUN mkdir ${WORKDIR}
RUN chown -R ${USER}:${USER} ${WORKDIR}

WORKDIR ${WORKDIR}

# Copy the specified content(s) into the container at ${WORKDIR}
COPY . .

RUN pip3 install --upgrade pip
RUN pip3 install --user redis
RUN pip3 install --user numpy

RUN chown -R ${USER}:${USER} ${WORKDIR}

USER ${USER}

CMD ["/bin/bash"]