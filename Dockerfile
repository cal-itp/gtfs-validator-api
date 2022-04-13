FROM openjdk:11

ENV GTFS_VALIDATOR_JAR=/usr/gtfs-validator.jar
ENV GTFS_VALIDATOR_VERSION=v2.0.0

WORKDIR /

# Install python
RUN apt-get update -y \
    && apt-get install -y python3 python3-pip

# Deps, etc.
ADD requirements.txt ./requirements.txt
RUN python3 -m pip install -r requirements.txt


RUN wget \
    https://github.com/MobilityData/gtfs-validator/releases/download/${GTFS_VALIDATOR_VERSION}/gtfs-validator-${GTFS_VALIDATOR_VERSION}_cli.jar \
    -O ${GTFS_VALIDATOR_JAR}

# Install package
WORKDIR /application

ADD . ./

RUN python3 -m pip install -e .

#ENTRYPOINT ["gtfs-validator-api"]
