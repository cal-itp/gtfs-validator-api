__version__ = "0.0.1"

import os
import json
import subprocess

import argh
from argh import arg

from tempfile import TemporaryDirectory
from pathlib import Path


try:
    JAR_PATH = os.environ.get("GTFS_VALIDATOR_JAR")
except KeyError:
    raise Exception("Must set the environment variable GTFS_VALIDATOR_JAR")


# API ----

@arg("gtfs_file", help="a zipped gtfs file", type=str)
def validate(gtfs_file, out_file=None, verbose=False):
    if not isinstance(gtfs_file, str):
        raise NotImplementedError("gtfs_file must be a string")

    # validator messages info through stderr
    stderr = subprocess.DEVNULL if not verbose else None
    stdout = subprocess.DEVNULL if not verbose else None

    with TemporaryDirectory() as tmp_out_dir:

        subprocess.check_call([
            "java",
            "-jar", JAR_PATH,
            "--input", gtfs_file,
            "--output_base", tmp_out_dir,
            "--feed_name", "na-na",
            ], stderr=stderr, stdout=stdout)

        report = Path(tmp_out_dir) / "report.json"
        system_errors = Path(tmp_out_dir) / "system_errors.json"

        result = {
                "report": json.load(open(report)),
                "system_errors": json.load(open(system_errors)),
                }

    if out_file is not None:
        with open(out_file, "w") as f:
            json.dump(result, f)
    
    else:
        return result


@arg("gtfs_files", nargs="+")
def validate_many(gtfs_files, out_file=None, verbose=False):
    results = list(map(lambda x: validate(x, verbose), gtfs_files))

    if out_file is not None:
        with open(out_file, "w") as f:
            json.dump(results, f)

    else:
        return results


# Cli ----

def main():
    # TODO: make into simple CLI
    result = argh.dispatch_commands([validate, validate_many])

    if result is not None:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
