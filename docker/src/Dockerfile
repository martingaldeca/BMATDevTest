# Get the last python image version and update all the repositories
FROM python
RUN apt-get update && apt-get install -y wget make gettext && apt-get clean
RUN apt-get autoclean

# Install dockerize to avoid startup problems (waiting for DB to start)
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz -O - | tar -C /usr/local/bin -xzv

# Prepare work directory
RUN mkdir -p src
WORKDIR src

# Load source code from the repository or local to the container
ADD src/ /src/

# Install all the requirements
RUN pip install poetry==1.2.0
RUN poetry config virtualenvs.create false && poetry install

# Load executors
ADD docker/src/post_deploy.sh /src/post_deploy.sh
ADD docker/src/run_worker.sh /src/run_worker.sh
ADD docker/src/run_beat.sh /src/run_beat.sh

# Add terminal colors
ADD docker/src/.bashrc /root/.bashrc

# Ipython config
RUN mkdir -p /root/.ipython/profile_default/
ADD docker/src/ipython-config.py /root/.ipython/profile_default/ipython_config.py
