import datetime
import json
import logging
import os
from enum import Enum
from typing import Iterator, Union, Any

Expected = Union[bool, str, int, float, datetime.date, datetime.datetime, None]
Jsonified = Union[bool, str, int, float, None]


class WriteMode(Enum):
    APPEND = "a"
    CREATE = "x"
    TRUNCATE = "w"


def _jsonify_types(row: dict[str, Expected]) -> dict[str, Jsonified]:
    """Cast types that are not supported by JSON to more compatible types"""
    _castable_types = {
        datetime.date: lambda x: x.isoformat(),
        datetime.datetime: lambda x: x.isoformat(timespec="microseconds"),
        datetime.timedelta: lambda x: str(x),
    }

    return {k: _castable_types.get(type(v), lambda x: x)(v) for k, v in row.items()}


def write_jsonl(
    data: Union[Iterator, list[Union[list[tuple[str, Any]], dict[str, Any]]]],
    prefix: str,
    filename: str,
    mode: WriteMode = WriteMode.CREATE,
) -> None:
    """Write serialised data to a given path/file"""
    path = os.path.join(prefix, filename)

    try:
        assert isinstance(
            mode, WriteMode
        ), f"Mode needs to be one of {[x.name for x in WriteMode]}"

        with open(path, mode=mode.value, encoding="utf-8") as outfile:
            logging.debug(f"Writing serialised data, {path=}")

            for line in data:
                if isinstance(line, dict):
                    _line = line
                elif isinstance(line, list) and isinstance(line[0], tuple):
                    _line = dict(line)
                else:
                    raise ValueError("Data must be a list of key/value pairs")

                # Add OS-specific newline after each row
                outfile.write(json.dumps(dict(_jsonify_types(_line))))
                outfile.write(os.linesep)

    except (AssertionError, FileExistsError) as e:
        logging.error(str(e))
        raise e


def read_jsonl(
    prefix: str, filename: str
) -> Union[Iterator, list[list[tuple[str, Jsonified]]]]:
    """Read JSONL serialised data from a given path/file"""
    path = os.path.join(prefix, filename)

    try:
        with open(path, mode="r", encoding="utf-8") as infile:
            logging.debug(f"Reading serialised data, {path=}")

            yield from iter(json.loads(line) for line in infile)

    except FileNotFoundError as e:
        logging.error(str(e))
        raise e


def delete_file(prefix: str, filename: str) -> None:
    """Delete a given data file"""
    path = os.path.join(prefix, filename)

    try:
        logging.debug(f"Deleting serialised data, {path=}")
        os.remove(path)
    except FileNotFoundError as e:
        logging.error(str(e))
        raise e


def count_file(prefix: str, filename: str) -> int:
    """Count number of lines in a given path/file"""
    _idx = 0

    with open(os.path.join(prefix, filename), mode="rb") as infile:
        for _idx, _ in enumerate(infile, start=1):
            pass

        return _idx
