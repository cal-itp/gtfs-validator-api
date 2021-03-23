__version__ = "0.0.1"

import os

from tempfile import TemporaryDirectory
from subprocess import check_call
from pathlib import Path


try:
    JAR_PATH = os.environ.get("GTFS_VALIDATOR_JAR")
except KeyError:
    raise Exception("Must set the environment variable GTFS_VALIDATOR_JAR")


# API ----

def validate(gtfs_file, out_file=None):
    if not isinstance(gtfs_file, str):
        raise NotImplementedError("gtfs_file must be a string")

    with TemporaryDirectory() as tmp_out_dir:
        extract_dir = Path(tmp_out_dir) / "extract"

        print(extract_dir)
        os.mkdir(extract_dir)

        check_call([
            "java",
            "-jar", JAR_PATH,
            "--input", gtfs_file,
            "--output", tmp_out_dir,
            "--extract", extract_dir,
            ])

        results = list(Path(tmp_out_dir).glob("*.json"))

        n_res = len(results)
        if n_res != 1:
            raise ValueError(
                    "Need one result, but received %s: %s" % (n_res, results)
                    )

        json_output = open(results[0]).read()

    if out_file is not None:
        with open(out_file, "w") as f:
            f.write(json_output)

    return json_output


# Cli ----

def main():
    # TODO: make into simple CLI
    import sys
    validate(sys.argv[1])


if __name__ == "__main__":
    main()
