FROM ubuntu:18.04

ARG USER=deduce
ENV USER ${USER}

# HOME must be added for NERSC to be able to load 
# the installed packages from ~/.local
ENV DEBIAN_FRONTEND=noninteractive \
    USER_HOME=/home/${USER} \ 
    HOME=/home/${USER}

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends sudo apt-utils && \
    apt-get install -y --no-install-recommends openssh-server && \
    apt-get install -y redis-tools gcc g++ cmake iperf vim

#### ADD DEFAULT USER ####
RUN adduser --disabled-password --gecos "" ${USER} && \
    echo "${USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN chown -R ${USER}:${USER} ${USER_HOME}

#### CREATE WORKING DIRECTORY FOR USER ####
ARG WORKDIR=/project
ENV WORKDIR ${WORKDIR}
RUN mkdir ${WORKDIR}

WORKDIR ${WORKDIR}

# Installing twemproxy (nutcracker)
RUN tar -xzf nutcracker-0.4.1.tar.gz
ENV CFLAGS="-ggdb3 -O0"
RUN cd nutcracker-0.4.1 && ./configure --enable-debug=full && \
	make && make install

# Copy the specified content(s) into the container at ${WORKDIR}
COPY . .

RUN chown -R ${USER}:${USER} ${WORKDIR}

USER ${USER}

CMD ["/bin/bash"]