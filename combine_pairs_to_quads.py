import os
from itertools import islice
from concurrent.futures import ProcessPoolExecutor, as_completed

PAIRS_FILE = "valid_pairs.txt"
OUTPUT_FILE = "valid_quads.txt"
CHUNK_SIZE = 1000
CPU_COUNT = os.cpu_count()


def word_to_bitmask(word):
    mask = 0
    for ch in word:
        mask |= 1 << (ord(ch) - ord('a'))
    return mask


def pair_to_data(pair_line):
    words = pair_line.strip().split()
    mask = word_to_bitmask(words[0]) | word_to_bitmask(words[1])
    return words, mask


def load_pairs():
    with open(PAIRS_FILE, "r") as f:
        return [pair_to_data(line) for line in f if len(line.strip().split()) == 2]


def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield (i, iterable[i:i + size])


def process_chunk(start_idx, chunk, all_pairs):
    pid = os.getpid()
    print(f"🚀 Worker PID {pid} started chunk at index {start_idx}")
    results = []

    for i, (words1, mask1) in enumerate(chunk):
        for j in range(start_idx + i + 1, len(all_pairs)):
            words2, mask2 = all_pairs[j]
            if mask1 & mask2 != 0:
                continue
            combined_words = words1 + words2
            if len(set(combined_words)) < 4:
                continue
            if bin(mask1 | mask2).count("1") == 20:
                results.append(" ".join(sorted(combined_words)))

    print(f"✅ Worker PID {pid} finished chunk at index {start_idx} with {len(results)} results")
    return results


def main():
    print("🚀 Loading valid pairs...")
    all_pairs = load_pairs()
    print(f"📘 Loaded {len(all_pairs):,} pairs.\n")

    seen_quads = set()
    written_total = 0
    found_total = 0

    futures = []

    print(f"🧠 Submitting work to {CPU_COUNT} processes...\n")
    with ProcessPoolExecutor(max_workers=CPU_COUNT) as executor:
        for start_idx, chunk in chunked(all_pairs, CHUNK_SIZE):
            futures.append(executor.submit(process_chunk, start_idx, chunk, all_pairs))
            if len(futures) % 50 == 0:
                print(f"📦 Submitted {len(futures):,} jobs...")

        print("⏳ Waiting for jobs to finish...\n")
        with open(OUTPUT_FILE, "w") as f:
            for i, future in enumerate(as_completed(futures)):
                try:
                    results = future.result()
                    for quad in results:
                        if quad not in seen_quads:
                            seen_quads.add(quad)
                            f.write(quad + "\n")
                            written_total += 1
                    found_total += len(results)
                except Exception as e:
                    print(f"❌ Error in job {i}: {e}")

                if i % 10 == 0:
                    print(f"🔄 Completed {i:,}/{len(futures):,} jobs | Found: {found_total:,} | Written: {written_total:,}")

    print(f"\n✅ ALL DONE! Total found: {found_total:,} | Unique written: {written_total:,}")
    print(f"📝 Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
