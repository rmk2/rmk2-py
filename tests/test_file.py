import datetime
import os

import pytest

import rmk2.file
from rmk2.file import WriteMode


def test_jsonify_types() -> None:
    """Check that casting types that are not supported by JSON meets expectations"""
    _types = (bool, str, int, float, None)

    rows = [
        {
            "date": datetime.date(2020, 2, 28),
            "datetime": datetime.datetime(
                2020, 2, 28, 12, 24, 48, 123456, tzinfo=datetime.timezone.utc
            ),
            "datetime_default": datetime.datetime(
                2020,
                2,
                28,
                12,
                24,
                48,
                tzinfo=datetime.timezone(datetime.timedelta(hours=1)),
            ),
            "timedelta": datetime.timedelta(days=69, hours=4, minutes=20),
            "int": 1,
            "float": 2.1,
            "str": "1",
            "bool": True,
        },
        {
            "date": "2020-02-28",
            "timedelta": "2 days",
            "int": 1,
            "float": 2.1,
            "str": "1",
            "bool": True,
        },
    ]

    rows_expected = [
        {
            "date": "2020-02-28",
            "datetime": "2020-02-28T12:24:48.123456+00:00",
            "datetime_default": "2020-02-28T12:24:48.000000+01:00",
            "timedelta": "69 days, 4:20:00",
            "int": 1,
            "float": 2.1,
            "str": "1",
            "bool": True,
        },
        {
            "date": "2020-02-28",
            "timedelta": "2 days",
            "int": 1,
            "float": 2.1,
            "str": "1",
            "bool": True,
        },
    ]

    rows_jsonified = [rmk2.file._jsonify_types(x) for x in rows]

    # Check types
    assert isinstance(rows_jsonified, list)
    assert all([isinstance(x, dict) for x in rows_jsonified])

    # Check contents
    assert all([all([type(v) in _types for _, v in x.items()]) for x in rows_jsonified])
    assert rows_jsonified == rows_expected


def test_write_jsonl_create(tmpdir) -> None:
    """Check that writing a JSONL file meets expectations"""
    filename = "test.json"

    # The function should write dicts and lists of tuples equally
    data = [
        [("a", 1), ("b", 2), ("c", 3)],
        [("d", 4), ("e", 5), ("f", 6)],
        {"g": 7, "h": 8, "i": 9},
        {"j": 10, "k": 11, "l": 12},
    ]

    rmk2.file.write_jsonl(
        data=data, prefix=tmpdir, filename=filename, mode=WriteMode.CREATE
    )

    assert os.path.exists(os.path.join(tmpdir, filename))

    with open(os.path.join(tmpdir, filename)) as infile:
        assert len([x for x in infile]) == len(data)


def test_write_jsonl_truncate(tmpdir) -> None:
    """Check that creating a JSONL file by truncating meets expectations"""
    filename = "test.json"

    data = [[("a", 1), ("b", 2), ("c", 3)], [("d", 4), ("e", 5), ("f", 6)]]

    rmk2.file.write_jsonl(
        data=data, prefix=tmpdir, filename=filename, mode=WriteMode.TRUNCATE
    )
    rmk2.file.write_jsonl(
        data=data, prefix=tmpdir, filename=filename, mode=WriteMode.TRUNCATE
    )

    assert os.path.exists(os.path.join(tmpdir, filename))

    with open(os.path.join(tmpdir, filename)) as infile:
        assert len([x for x in infile]) == len(data)


def test_write_jsonl_append(tmpdir) -> None:
    """Check that creating a JSONL file by appending meets expectations"""
    filename = "test.json"

    data = [[("a", 1), ("b", 2), ("c", 3)], [("d", 4), ("e", 5), ("f", 6)]]

    rmk2.file.write_jsonl(
        data=data, prefix=tmpdir, filename=filename, mode=WriteMode.APPEND
    )
    rmk2.file.write_jsonl(
        data=data, prefix=tmpdir, filename=filename, mode=WriteMode.APPEND
    )

    assert os.path.exists(os.path.join(tmpdir, filename))

    with open(os.path.join(tmpdir, filename)) as infile:
        assert len([x for x in infile]) == len(data) * 2


def test_write_jsonl_create_exception(tmpdir) -> None:
    """Check that writing to an existing JSONL file produces an exception"""
    filename = "test.json"

    data = [[("a", 1), ("b", 2), ("c", 3)], [("d", 4), ("e", 5), ("f", 6)]]

    with open(os.path.join(tmpdir, filename), mode="w", encoding="utf-8") as outfile:
        outfile.write("foo")
        outfile.write(os.linesep)

    with pytest.raises(FileExistsError) as e:
        rmk2.file.write_jsonl(
            data=data, prefix=tmpdir, filename=filename, mode=WriteMode.CREATE
        )

    assert e


def test_read_jsonl(tmpdir) -> None:
    """Check that reading JSONL files meets expectations"""
    filename = "test.json"

    data = [[("a", 1), ("b", 2), ("c", 3)], [("d", 4.0), ("e", True), ("f", None)]]

    # Write test data, which should work since we tested it above
    rmk2.file.write_jsonl(data=data, prefix=tmpdir, filename=filename)

    data_read = list(rmk2.file.read_jsonl(prefix=tmpdir, filename=filename))

    assert [dict(x) for x in data] == data_read
    assert data == [[(k, v) for k, v in x.items()] for x in data_read]


def test_delete_file(tmpdir) -> None:
    """Check that deleting files meets expectations"""
    filename = "test.json"

    with open(os.path.join(tmpdir, filename), mode="w", encoding="utf-8") as outfile:
        outfile.write("foo")
        outfile.write(os.linesep)

    rmk2.file.delete_file(prefix=tmpdir, filename=filename)

    assert not os.path.exists(os.path.join(tmpdir, filename))


@pytest.mark.parametrize("lines", (100, 12345, 100000))
def test_count_extract(tmpdir, lines) -> None:
    """Check that counting lines in a file meets expectations"""
    filename = "test.json"

    with open(os.path.join(tmpdir, filename), mode="x") as outfile:
        for n in range(0, lines):
            outfile.write(str(n))
            outfile.write(os.linesep)

    lines_counted = rmk2.file.count_file(prefix=tmpdir, filename=filename)

    assert lines_counted == lines
