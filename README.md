# DEPRECATED: this repo/image are replaced by https://github.com/cal-itp/data-infra/tree/main/jobs/gtfs-schedule-validator

# gtfs-validator-api

This python package is a thin wrapper around MobilityData/gtfs-validator.
It's has 2 jobs.

1. Handle the intermediate files produced by gtfs-validator.
2. Find gtfs-validator's output file, so it can be given a specific name, or
   returned as a string.

## Example

Note that this package requires `GTFS_VALIDATOR_JAR` to be set to the `gtfs-validator`
CLI jar file. See their [releases page](https://github.com/MobilityData/gtfs-validator/releases).

```python
from gtfs_validator_api import validate
validate("tests/sample.zip")
```

## Development

```
docker-compose run gtfs-validator /bin/bash

# then, run example script in container
gtfs-validator-api validate tests/sample.zip
gtfs-validator-api validate --help
gtfs-validator-api validate-gcs-bucket \
    -v -r \
    -o validation.json \
    cal-itp-data-infra \
    google_default \
    gs://gtfs-data-test/schedule/2021-03-28T00:00:00+00:00

```
