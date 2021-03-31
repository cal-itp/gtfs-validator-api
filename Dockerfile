#FROM ghcr.io/mobilitydata/gtfs-validator:v2.0.0
FROM openjdk:11

RUN wget \
    https://github.com/MobilityData/gtfs-validator/releases/download/v2.0.0/gtfs-validator-v2.0.0_cli.jar \
    -O /usr/gtfs-validator.jar

ENV GTFS_VALIDATOR_JAR=/usr/gtfs-validator.jar

# Install python
RUN apt-get update -y \
    && apt-get install -y python3 python3-pip \
    && python3 -m pip install argh==0.26.2 gcsfs==0.7.2

# Install package
WORKDIR /application

ADD . ./

RUN python3 -m pip install -e .

#ENTRYPOINT ["gtfs-validator-api"]
