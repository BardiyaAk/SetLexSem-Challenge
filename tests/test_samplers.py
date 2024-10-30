import random
import string
import types
import warnings

import pytest
from nltk.corpus.reader import Synset

from setlexsem.generate.sample import (
    BasicNumberSampler,
    BasicWordSampler,
    DeceptiveWordSampler,
    OverlapSampler,
    find_hypernyms_and_hyponyms,
    make_edit_distance_queue,
    remove_similar_lemmata,
    remove_substring_lemmata,
)

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="Discarded redundant search for Synset",
)


@pytest.mark.parametrize(
    "object_type, item_len, m, overlap_fraction",
    [
        ("numbers", 1, 2, 0),
        ("numbers", 1, 2, 0.5),
        ("numbers", 1, 2, 1),
        ("numbers", 1, 4, 0.25),
        ("numbers", 1, 4, 0.75),
        ("numbers", 3, 2, 0),
        ("numbers", 3, 4, 0.75),
        ("numbers", 5, 2, 1),
        ("numbers", 5, 4, 0.75),
        ("words", 1, 2, 0),
        ("words", 1, 4, 0.25),
        ("words", 3, 2, 0.5),
        ("words", 3, 4, 0.75),
        ("words", 5, 2, 0),
        ("words", 5, 4, 1),
    ],
)
def test_overlap_number_sampler(object_type, item_len, m, overlap_fraction):
    """
    Verify that overlapping sets are sampled correctly.
    """
    if object_type == "numbers":
        sampler = BasicNumberSampler(
            n=1000,
            m=m,
            item_len=item_len,
        )
    elif object_type == "words":
        sampler = BasicWordSampler(
            n=1000,
            m=m,
            item_len=item_len,
        )
    overlap_sampler = OverlapSampler(
        sampler=sampler,
        overlap_fraction=overlap_fraction,
    )
    # create overlap sampler
    A, B = overlap_sampler()
    actual_overlap = len(A.intersection(B)) / len(A)
    assert (
        abs(actual_overlap - overlap_fraction) < 1e-5
    ), f"{A=} | {B=} ({actual_overlap=} & {overlap_fraction=})"


def test_remove_substring_lemmata():
    """
    Verify resulting list of strings contains no substrings.
    """
    input_lemmata = ["food", "foo", "thing", "farthing"]
    expected = ["food", "farthing"]
    actual = remove_substring_lemmata(input_lemmata)
    assert actual == expected


def test_edit_distance_queue():
    """
    Verify priority queue of edit distances.
    """
    input_lemmata = ["food", "foo", "thing", "farthing"]
    expected = [
        (1, [["food", "foo"]]),
        (3, [["thing", "farthing"]]),
        (5, [["food", "thing"], ["foo", "thing"]]),
        (7, [["food", "farthing"], ["foo", "farthing"]]),
    ]
    actual = make_edit_distance_queue(input_lemmata)
    assert actual == expected


def test_remove_similar_lemmata():
    """
    Verify that simiar lemmata with short edit distances are removed.
    """
    input_lemmata = ["food", "foo", "thing", "farthing"]
    expected = ["food", "farthing"]
    actual = remove_similar_lemmata(input_lemmata, random_state=42)
    assert actual == expected


def test_smoke_find_hypernyms_and_hyponyms():
    """
    Smoke test of find_hypernyms_and_hyponyms.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="Recursion", category=UserWarning
        )
        hyperhypo = find_hypernyms_and_hyponyms()
        assert isinstance(hyperhypo, types.GeneratorType)
        # Check the types of the elements of only first tuple yielded by the
        # generator, then exit the loop.
        for hyper, hypo in hyperhypo:
            assert isinstance(hyper, Synset)
            assert isinstance(hypo, set)
            break


def test_smoke_basic_word_sampler():
    """
    Smoke test of BasicWordSampler.
    """
    sampler = BasicWordSampler(n=10, m=4)
    A, B = sampler()
    assert len(A) == 4
    assert len(B) == 4


def test_smoke_basic_number_sampler():
    """
    Smoke test of BasicNumberSampler.
    """
    sampler = BasicNumberSampler(n=10, m=4)
    A, B = sampler()
    assert len(A) == 4
    assert len(B) == 4


def test_smoke_deceptive_word_sampler():
    """
    Smoke test of DeceptiveWordSampler.
    """
    # n doesn't apply to this sampler.
    sampler = DeceptiveWordSampler(n=int(10e5), m=4)
    A, B = sampler()
    assert len(A) == 4
    assert len(B) == 4


def test_basic_word_sampler_item_len():
    """
    Verify that words are of the specified length when item_len is provided.
    """
    sampler = BasicWordSampler(n=10, m=4, item_len=5)
    A, B = sampler()
    assert all(len(word) == 5 for word in A)
    assert all(len(word) == 5 for word in B)


def test_basic_number_sampler_item_len():
    """
    Verify that numbers are of the specified length when item_len is provided.
    """
    sampler = BasicNumberSampler(n=10, m=4, item_len=5)
    A, B = sampler()
    # FIXME For consistency, all samplers should return strings, even if the
    # objects are numbers. That will ensure consistency of processing if e.g.
    # we have a sampler that returns sets of words and numbers.
    assert all(len(str(num)) == 5 for num in A)
    assert all(len(str(num)) == 5 for num in B)


def test_basic_word_sampler_random_state():
    """
    Verify that behavior is the same when the same random state is provided.
    """
    sampler1 = BasicWordSampler(n=10, m=4, random_state=random.Random(17))
    A1, B1 = sampler1()
    sampler2 = BasicWordSampler(n=10, m=4, random_state=random.Random(17))
    A2, B2 = sampler2()
    assert A1 == A2
    assert B1 == B2


def test_basic_number_sampler_random_state():
    """
    Verify that behavior is the same when the same random state is provided.
    """
    sampler1 = BasicNumberSampler(n=10, m=4, random_state=random.Random(17))
    A1, B1 = sampler1()
    sampler2 = BasicNumberSampler(n=10, m=4, random_state=random.Random(17))
    A2, B2 = sampler2()
    assert A1 == A2
    assert B1 == B2


def test_deceptive_word_sampler_random_state():
    """
    Verify that behavior is the same when the same random state is provided.
    """
    sampler1 = DeceptiveWordSampler(
        n=int(10e5), m=4, random_state=random.Random(17)
    )
    A1, B1 = sampler1()
    sampler2 = DeceptiveWordSampler(
        n=int(10e5), m=4, random_state=random.Random(17)
    )
    A2, B2 = sampler2()
    assert A1 == A2
    assert B1 == B2


def test_basic_word_sampler_user_provided_words():
    """
    Verify that words are sampled from the user-provided words.
    """
    words = list(set(string.ascii_letters))
    sampler = BasicWordSampler(n=10, m=4, words=words)
    A, B = sampler()
    assert len(A) == 4
    assert len(B) == 4
    assert all(len(a) == 1 for a in A)
    assert all(len(b) == 1 for b in B)


def test_deceptive_word_sampler_mix_sets():
    """
    Verify set mixing.
    """
    A = {1, 2, 3}
    B = {4, 5, 6, 7}
    # Randomize the test.
    subset_size = random.randint(1, len(A))
    # Call mix_sets via the class to avoid constructing an instance of
    # DeceptiveWordSampler, as it takes a long time to initialize.
    A2, B2 = DeceptiveWordSampler.mix_sets(
        None, A, B, subset_size=subset_size
    )
    assert len(A2) == len(A)
    assert len(A.intersection(A2)) == len(A) - subset_size
    assert len(B2) == len(B)
    assert len(B.intersection(B2)) == len(B) - subset_size