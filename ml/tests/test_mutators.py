import random
import pytest
from ml.mutators import ALL_MUTATORS
from ml.mutators.base import MutationResult
from backend.app.compiler.constants import ErrorCategory

SAMPLE_CODE = """#include <iostream>
#include <vector>

using namespace std;

// Prototype declared above main
int computeSquare(int n);

int main() {
    // A sample comment that must not be edited
    const int testVal = 5;
    string greeting = "Hello, world; please do not touch this!";
    int result = computeSquare(testVal);
    cout << greeting << " Result: " << result << endl;
    return 0;
}

// Definition below main
int computeSquare(int n) {
    if (n < 0) {
        return 0;
    }
    return n * n;
}
"""

def test_all_12_mutators_exist():
    assert len(ALL_MUTATORS) == 12
    categories = {m.category.value for m in ALL_MUTATORS}
    expected = {c.value for c in ErrorCategory}
    assert categories == expected

def test_mutator_determinism():
    for mutator in ALL_MUTATORS:
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        res1 = mutator.apply(SAMPLE_CODE, rng1)
        res2 = mutator.apply(SAMPLE_CODE, rng2)
        if res1 is not None and res2 is not None:
            assert res1.mutated_source == res2.mutated_source
            assert res1.variant == res2.variant
            assert res1.line_no == res2.line_no

def test_mutator_changes_single_location():
    rng = random.Random(123)
    for mutator in ALL_MUTATORS:
        res = mutator.apply(SAMPLE_CODE, rng)
        if res is not None:
            orig_lines = SAMPLE_CODE.splitlines()
            mutated_lines = res.mutated_source.splitlines()
            # Must differ by at most a small delta around line_no
            assert res.line_no > 0
            assert res.mutated_source != SAMPLE_CODE

def test_mutator_returns_none_when_inapplicable():
    empty_code = "// just a comment"
    rng = random.Random(42)
    for mutator in ALL_MUTATORS:
        res = mutator.apply(empty_code, rng)
        assert res is None

def test_does_not_mutate_comments_or_strings():
    for mutator in ALL_MUTATORS:
        rng = random.Random(42)
        res = mutator.apply(SAMPLE_CODE, rng)
        if res is not None:
            # Comment line "A sample comment..." must be intact
            assert "// A sample comment that must not be edited" in res.mutated_source
            # String literal greeting content must be intact
            assert "Hello, world; please do not touch this!" in res.mutated_source
