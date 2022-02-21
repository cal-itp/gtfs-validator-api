__version__ = "0.0.6"

import json
import os
import shutil
import subprocess
import warnings
from pathlib import Path
from tempfile import TemporaryDirectory

import argh
import backoff
import gcsfs
from aiohttp.client_exceptions import ClientOSError, ClientResponseError
from argh import arg

try:
    JAR_PATH = os.environ.get("GTFS_VALIDATOR_JAR")
except KeyError:
    raise Exception("Must set the environment variable GTFS_VALIDATOR_JAR")


# Utility funcs ----


def retry_on_fail(f, max_retries=2):
    for n_retries in range(max_retries + 1):
        try:
            f()
        except Exception as e:
            if n_retries < max_retries:
                n_retries += 1
                warnings.warn("Function failed, starting retry: %s" % n_retries)
            else:
                raise e


@backoff.on_exception(backoff.expo, (ClientResponseError, ClientOSError), max_tries=2)
def get_with_retry(fs: gcsfs.GCSFileSystem, *args, **kwargs):
    return fs.get(*args, **kwargs)


# API ----


@arg("gtfs_file", help="a zipped gtfs file", type=str)
def validate(gtfs_file, out_file=None, verbose=False, feed_name="us-na"):
    if not isinstance(gtfs_file, str):
        raise NotImplementedError("gtfs_file must be a string")

    # validator messages info through stderr
    stderr = subprocess.DEVNULL if not verbose else None
    stdout = subprocess.DEVNULL if not verbose else None

    with TemporaryDirectory() as tmp_out_dir:

        subprocess.check_call(
            [
                "java",
                "-jar",
                JAR_PATH,
                "--input",
                gtfs_file,
                "--output_base",
                tmp_out_dir,
                "--feed_name",
                feed_name,
            ],
            stderr=stderr,
            stdout=stdout,
        )

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


def _get_paths_from_status(f, bucket_path):
    from csv import DictReader

    tmpl_path = "{bucket_path}/{itp_id}_{url_number}"

    rows = list(DictReader(f))

    paths = []
    for row in rows:
        if row["status"] != "success":
            continue

        paths.append(tmpl_path.format(bucket_path=bucket_path, **row))

    return paths


@arg("bucket_paths", nargs="+")
def validate_gcs_bucket(
    project_id,
    token,
    bucket_paths,
    feed_name="us-na",
    recursive=False,
    out_file=None,
    verbose=False,
):
    """
    Arguments:
        project_id: name of google cloud project
        token: token argument passed to gcsfs.GCSFileSystem
        bucket_paths: list-like. paths to gcs buckets (e.g. gs://a_bucket/b/c)
        feed_name: a string of form "{iso_country}-{custom_name}"
        recursive: whether to look for a file named status.csv in bucket, and
                   use that to validate multiple gtfs data sources within.
        out_file: file path for saving json result (may be a bucket)
        verbose: whether to print out information for debugging

    Note:
        This function expects a status.csv file in the bucket with fields:
            * itp_id, url_number, status

        It will look for subfolders named {itp_id}/{url_number}.
    """
    fs = gcsfs.GCSFileSystem(project_id, token=token)

    if recursive:
        if len(bucket_paths) > 1:
            raise ValueError("recursive is True, but more than 1 path given")

        f = fs.open(bucket_paths[0] + "/status.csv", "r")
        bucket_paths = _get_paths_from_status(f, bucket_paths[0])

    results = []
    for path in bucket_paths:
        if verbose:
            print(path)

        with TemporaryDirectory() as tmp_dir:
            path_raw = tmp_dir + "/gtfs"
            path_zip = tmp_dir + "/gtfs.zip"

            get_with_retry(path, path_raw, recursive=True)
            shutil.make_archive(path_raw, "zip", path_raw)

            result = {
                "version": os.environ["GTFS_VALIDATOR_VERSION"],
                "data": validate(path_zip, verbose=verbose, feed_name=feed_name),
            }

        results.append(result)

        # optionally save result to disk
        if out_file is not None:
            bucket_out = path + "/" + out_file

            if verbose:
                print("Saving to path: %s" % bucket_out)

            # fs.pipe expects contents to be byte encoded
            retry_on_fail(lambda: fs.pipe(bucket_out, json.dumps(result).encode()), 2)

    # if not saving to disk, return results
    if out_file is None:
        return results


# Cli ----


def main():
    # TODO: make into simple CLI
    result = argh.dispatch_commands([validate, validate_many, validate_gcs_bucket])

    if result is not None:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
