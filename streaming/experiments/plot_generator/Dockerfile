FROM ubuntu:18.04

ARG USER=mpi
ENV USER ${USER}

# HOME must be added for NERSC to be able to load 
# the installed packages from ~/.local
ENV DEBIAN_FRONTEND=noninteractive \
    USER_HOME=/home/${USER} \ 
    HOME=/home/${USER}


RUN apt-get update -y && \
    apt-get install -y --no-install-recommends sudo apt-utils && \
    apt-get install -y --no-install-recommends openssh-server \
        python3-dev python3-numpy python3-pip python3-virtualenv \
        vim && \
    apt-get clean && apt-get purge && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


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

USER ${USER}

RUN pip3 install --user numpy matplotlib

CMD ["python3", "main.py", "-e", "/data/streaming_eval_measurements", "-f", "0"]