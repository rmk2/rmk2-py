import datetime
import hashlib

from rmk2.hash import hash_values, HashAlgorithm

import pytest


@pytest.mark.parametrize("value", [1, 42.1, "a", ""])
@pytest.mark.parametrize(
    "algorithm", [HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512]
)
def test_hash_algorithms(algorithm, value) -> None:
    """Check that hashes for different algorithms meet expectations"""

    _hash = algorithm.value(usedforsecurity=True)
    _hash.update(str(value).encode("utf-8"))
    hash_direct = _hash.hexdigest()

    hash_import = hash_values(value, algorithm=algorithm)

    assert hash_direct == hash_import


def test_hash_values_single() -> None:
    """Check that direct and computed hashes for a single value meets expectations"""
    value = 1

    _hash = hashlib.sha256()
    _hash.update(str(value).encode("utf-8"))
    hash_direct = _hash.hexdigest()

    hash_import = hash_values(value, algorithm=HashAlgorithm.SHA256)
    hash_expected = "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b"

    assert hash_direct == hash_import == hash_expected


def test_hash_values_multi() -> None:
    """Check that direct and computed hashes for multiple values meet expectations"""
    value_1 = 1
    value_2 = "a"

    _hash = hashlib.sha256()
    _hash.update(str(value_1).encode("utf-8"))
    _hash.update(str(value_2).encode("utf-8"))
    hash_direct = _hash.hexdigest()

    hash_import = hash_values(value_1, value_2, algorithm=HashAlgorithm.SHA256)
    hash_expected = "a73fcf339640929207281fb8e038884806e2eb0840f2245694dbba1d5cc89e65"

    assert hash_direct == hash_import == hash_expected


def test_hash_values_input() -> None:
    """Check that various ways to feed arguments to the hash function are equivalent"""
    value_1 = 1
    value_2 = "a"
    values = [value_1, value_2]

    hash_param = hash_values(value_1, value_2, algorithm=HashAlgorithm.SHA256)
    hash_args = hash_values(*values, algorithm=HashAlgorithm.SHA256)

    assert hash_param == hash_args


def test_hash_values_ordering() -> None:
    """Check that hashing elements in reverse order produces a different digest"""
    value_1 = 1
    value_2 = "a"

    hash_left_to_right = hash_values(value_1, value_2, algorithm=HashAlgorithm.SHA256)
    hash_right_to_left = hash_values(value_2, value_1, algorithm=HashAlgorithm.SHA256)

    assert hash_left_to_right != hash_right_to_left


def test_hash_values_types() -> None:
    """Check that hashing different types meets expectations"""
    value_str = "1"
    value_int = 1
    value_bytes = b"1"

    _hash = hashlib.sha256()
    _hash.update(value_bytes)
    hash_bytes = _hash.hexdigest()

    hash_str = hash_values(value_str, algorithm=HashAlgorithm.SHA256)
    hash_int = hash_values(value_int, algorithm=HashAlgorithm.SHA256)

    assert hash_str == hash_int == hash_bytes


def test_hash_values_timestamps() -> None:
    """Check that hashing datetime objects meets expectations"""
    value_datetime = datetime.datetime(2018, 10, 28, 21, 42, 0)
    value_current = datetime.datetime.now()

    hash_datetime = hash_values(value_datetime, algorithm=HashAlgorithm.SHA256)
    hash_current = hash_values(value_current, algorithm=HashAlgorithm.SHA256)
    hash_expected = "c75325c5ce6a222c027c21701fdff45560264dd82665c0f5e780e0748a6183d7"

    assert hash_datetime == hash_expected != hash_current


def test_hash_values_timedelta() -> None:
    """Check that hashing timedelta objects meets expectations"""
    value_hours = datetime.timedelta(hours=1)
    value_minutes = datetime.timedelta(minutes=1)

    hash_timedelta = hash_values(value_hours, algorithm=HashAlgorithm.SHA256)
    hash_minutes = hash_values(value_minutes, algorithm=HashAlgorithm.SHA256)
    hash_expected = "598a7ec1bbddc45b2c5887126af6524977adb08c1102d8564f0c427c3b321659"

    assert hash_timedelta == hash_expected != hash_minutes


def test_hash_values_default_null() -> None:
    """Check that hashing unaltered None-objects and empty string meets expectations"""
    value_none = None
    value_none_multi = [None, None, None]
    value_empty = ""
    value_empty_multi = ["", "", ""]

    hash_direct = hashlib.sha256().hexdigest()
    hash_expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    hash_default = hash_values(algorithm=HashAlgorithm.SHA256)

    hash_none = hash_values(value_none, algorithm=HashAlgorithm.SHA256, replace_null="")
    hash_empty = hash_values(
        value_empty, algorithm=HashAlgorithm.SHA256, replace_null=""
    )

    hash_multi_none = hash_values(
        *value_none_multi, algorithm=HashAlgorithm.SHA256, replace_null=""
    )
    hash_multi_empty = hash_values(
        *value_empty_multi, algorithm=HashAlgorithm.SHA256, replace_null=""
    )

    assert (
        hash_direct
        == hash_expected
        == hash_default
        == hash_none
        == hash_empty
        == hash_multi_none
        == hash_multi_empty
    )


def test_hash_values_replace_null() -> None:
    """Check that hashing altered None-objects and empty string meets expectations"""
    replace_null = "æøþð"

    value_none = None
    value_none_multi = [None, None, None]
    value_empty = ""
    value_empty_multi = ["", "", ""]

    # Since None/NULL and '' have meaning in the SQL world, make sure that multiple
    # combinations of values or NULLs still result in different hashes, rather than
    # using hashlib's normal mode of operation, where they all hash to empty string
    altered_null_value_bytes = replace_null.encode("utf-8")

    hash_direct = hashlib.sha256(altered_null_value_bytes).hexdigest()
    hash_expected = "c76377eda0abc511f403783979ee9efc026388d0e90a859aef5cdfa86e9ac942"

    hash_none = hash_values(
        value_none, algorithm=HashAlgorithm.SHA256, replace_null=replace_null
    )
    hash_empty = hash_values(
        value_empty, algorithm=HashAlgorithm.SHA256, replace_null=replace_null
    )

    hash_none_hashlib = hashlib.sha256().hexdigest()
    hash_empty_hashlib = hashlib.sha256("".encode("utf-8")).hexdigest()
    hash_expected_hashlib = (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )

    assert hash_none == hash_empty == hash_direct == hash_expected
    assert hash_none_hashlib == hash_empty_hashlib == hash_expected_hashlib
    assert hash_none == hash_expected != hash_none_hashlib == hash_expected_hashlib

    _hash = hashlib.sha256()
    _hash.update(altered_null_value_bytes)
    _hash.update(altered_null_value_bytes)
    _hash.update(altered_null_value_bytes)
    hash_multi_direct = _hash.hexdigest()
    hash_multi_expected = (
        "4b99f5923d640e18940f357f036719d6093b89c82054e344f4e613d71fe6e555"
    )

    hash_multi_none = hash_values(
        *value_none_multi, algorithm=HashAlgorithm.SHA256, replace_null=replace_null
    )
    hash_multi_empty = hash_values(
        *value_empty_multi, algorithm=HashAlgorithm.SHA256, replace_null=replace_null
    )

    assert (
        hash_multi_none == hash_multi_empty == hash_multi_direct == hash_multi_expected
    )
    assert hash_multi_none != hash_none

    # Check that the order of "NULL" values changes the generated hash
    assert (
        hash_values(1, 2, None, replace_null=replace_null)
        != hash_values(1, None, 2, replace_null=replace_null)
        != hash_values(None, 1, 2, replace_null=replace_null)
    )
