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
        python3-dev python3-numpy python3-pip python3-virtualenv python3-scipy redis-tools \
        gcc gfortran libopenmpi-dev openmpi-bin openmpi-common openmpi-doc binutils iperf \
        vim iputils-ping && \
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


# ------------------------------------------------------------
# install mpi4py
# ------------------------------------------------------------

RUN pip3 install --upgrade pip

USER ${USER}

#RUN pip3 install --user -U setuptools
#RUN pip3 install --user mpi4py scipy scikit-learn redis==2.10.6 numpy
RUN pip3 install --user scipy scikit-learn redis==2.10.6 numpy

#RUN pip3 install scipy scikit-learn redis==2.10.6 numpy

ENV PYTHONPATH=${HOME}/.local/lib/python3.6/site-packages:$PYTHONPATH

#ENTRYPOINT ["python3", "stream_worker.py"]
#CMD ["blot.lbl.gov", "6378", "0", "task_queue:f5b4873137a332836e384ecbc8c9a4a876d267f2"]
CMD ["/bin/bash"]