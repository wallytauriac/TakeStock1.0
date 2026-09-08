"""
Random Number Distribution Tester
----------------------------------
Two generators are included:

1. run_test()          - pure random.randint draws (duplicates and gaps
                          both possible, like rolling dice repeatedly).

2. guaranteed_coverage() - allows duplicates anywhere, but guarantees every
                          number in the range appears at least once by the
                          end of the run. It does this by seeding the result
                          with one shuffled copy of every number, then
                          filling the rest of the iterations with pure
                          random draws, then shuffling the whole combined
                          list so the "guaranteed" ones aren't predictably
                          at the start.

Usage:
    python random_distribution_test.py
    (or import either function and call it with your own parameters)
"""

import random
from collections import Counter


def guaranteed_coverage(low: int = 1, high: int = 50, iterations: int = 100, seed: int = None):
    """
    Generate `iterations` random integers in [low, high], guaranteeing every
    number in the range appears at least once. Duplicates are allowed and
    can appear anywhere in the sequence (order is fully shuffled at the end).

    Requires iterations >= (high - low + 1).

    Args:
        low: smallest possible value (inclusive)
        high: largest possible value (inclusive)
        iterations: how many numbers to produce total
        seed: optional seed for reproducible results (None = fully random)

    Returns:
        list of `iterations` integers, in random order
    """
    if low > high:
        raise ValueError("low must be <= high")

    total_possible = high - low + 1
    if iterations < total_possible:
        raise ValueError(
            f"iterations ({iterations}) must be >= range size ({total_possible}) "
            "to guarantee every number appears at least once"
        )

    rng = random.Random(seed)

    # One guaranteed copy of every number in the range
    guaranteed = list(range(low, high + 1))

    # Fill the remaining slots with pure random draws
    extra_needed = iterations - total_possible
    extra = [rng.randint(low, high) for _ in range(extra_needed)]

    results = guaranteed + extra
    rng.shuffle(results)  # so the guaranteed ones aren't bunched at the start
    return results


def run_test(low: int = 1, high: int = 50, iterations: int = 100, seed: int = None):
    """
    Generate `iterations` random integers in [low, high] and report coverage.

    Args:
        low: smallest possible value (inclusive)
        high: largest possible value (inclusive)
        iterations: how many random draws to perform
        seed: optional seed for reproducible results (None = fully random)

    Returns:
        Counter mapping each drawn number -> how many times it appeared
    """
    if low > high:
        raise ValueError("low must be <= high")

    rng = random.Random(seed)  # local RNG so we don't disturb global random state
    results = [rng.randint(low, high) for _ in range(iterations)]
    counts = Counter(results)

    total_possible = high - low + 1
    hit_numbers = set(counts.keys())
    missed_numbers = sorted(set(range(low, high + 1)) - hit_numbers)

    print(f"Range: {low}-{high}  ({total_possible} possible values)")
    print(f"Iterations: {iterations}")
    print(f"Unique numbers hit: {len(hit_numbers)} / {total_possible} "
          f"({len(hit_numbers) / total_possible:.1%} coverage)")

    if missed_numbers:
        print(f"Numbers never drawn ({len(missed_numbers)}): {missed_numbers}")
    else:
        print("All numbers in range were drawn at least once!")

    # Show distribution counts, sorted by number
    print("\nDraw counts per number:")
    for n in range(low, high + 1):
        bar = "#" * counts.get(n, 0)
        print(f"{n:>3}: {counts.get(n, 0):>2} {bar}")

    return counts


if __name__ == "__main__":
    print("=== Pure random draws (gaps and repeats both possible) ===")
    run_test(low=1, high=50, iterations=50)

    print("\n=== Guaranteed coverage (repeats allowed, no gaps) ===")
    numbers = guaranteed_coverage(low=1, high=50, iterations=100)
    counts = Counter(numbers)
    missing = sorted(set(range(1, 51)) - set(numbers))
    print(f"Missing numbers: {missing if missing else 'none'}")
    print(f"Total draws: {len(numbers)}  |  Unique numbers used: {len(counts)}")
    print(f"First 20 draws (order is shuffled): {numbers[:20]}")