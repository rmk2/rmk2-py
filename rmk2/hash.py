import datetime
import hashlib
import logging
from enum import Enum
from typing import Any


class HashAlgorithm(Enum):
    SHA256 = hashlib.sha256
    SHA384 = hashlib.sha384
    SHA512 = hashlib.sha512


def hash_values(
    *args: Any,
    algorithm: HashAlgorithm = HashAlgorithm.SHA256,
    replace_null: str = "",
) -> str:
    """Hash various items to create consistent digests for a given value

    Casts its input(s) to str, encodes it as UTF-8 bytes, then hashes it"""
    _types = (
        int,
        float,
        str,
        bool,
        datetime.datetime,
        datetime.date,
        datetime.timedelta,
    )

    assert (
        algorithm in HashAlgorithm
    ), f"Algorithm needs to be one of {[x.name for x in HashAlgorithm]}"

    try:
        _hash = algorithm.value(usedforsecurity=True)

        for value in args:
            # If replace_null is defined, replace NULL values with an unlikely string
            # to ensure that (1, None) and (None, 1) are different hashes
            if value is None or value == "":
                value = replace_null
            else:
                assert (
                    type(value) in _types
                ), f"Cannot cast to string, type={type(value)}"

            _hash.update(str(value).encode(encoding="utf-8"))

        return _hash.hexdigest()

    except AssertionError as e:
        logging.error(str(e))
        raise e
