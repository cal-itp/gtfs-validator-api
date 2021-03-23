# gtfs-validator-api

This python package is a thin wrapper around MobilityData/gtfs-validator.
It's has 2 jobs.

1. Handle the intermediate files produced by gtfs-validator.
2. Find gtfs-validator's output file, so it can be given a specific name, or
   returned as a string.
