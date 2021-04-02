FROM openjdk:11

ENV GTFS_VALIDATOR_JAR=/usr/gtfs-validator.jar
ENV GTFS_VALIDATOR_VERSION=v2.0.0

RUN wget \
    https://github.com/MobilityData/gtfs-validator/releases/download/${GTFS_VALIDATOR_VERSION}/gtfs-validator-${GTFS_VALIDATOR_VERSION}_cli.jar \
    -O ${GTFS_VALIDATOR_JAR}

# Install python
RUN apt-get update -y \
    && apt-get install -y python3 python3-pip \
    && python3 -m pip install argh==0.26.2 gcsfs==0.7.2

# Install package
WORKDIR /application

ADD . ./

RUN python3 -m pip install -e .

#ENTRYPOINT ["gtfs-validator-api"]
