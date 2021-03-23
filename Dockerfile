FROM ghcr.io/mobilitydata/gtfs-validator:v1.4.0

ENV GTFS_VALIDATOR_JAR=/usr/gtfs-validator/cli-app/gtfs-validator-v1.4.0_cli.jar

# Install python
RUN apt-get update -y \
    && apt-get install -y python3 python3-pip

# Install package
WORKDIR /application

ADD . ./

RUN python3 -m pip install -e .

#ENTRYPOINT ["gtfs-validator-api"]
