import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple, Set

# File paths
WORDS_FILE = "five_letter_words.txt"
QUADS_FILE = "valid_quads.txt"
OUTPUT_FILE = "valid_quintuples.txt"
CHUNK_SIZE = 1000
CPU_COUNT = os.cpu_count()

def word_to_bitmask(word: str) -> int:
    """
    Converts a 5-letter word into a 26-bit integer bitmask.
    Each bit represents a letter from 'a' to 'z'.
    """
    mask = 0
    for ch in word:
        mask |= 1 << (ord(ch) - ord('a'))
    return mask

def load_words(filepath: str) -> List[Tuple[str, int]]:
    """
    Loads five-letter words from file and returns a list of tuples:
    (word, bitmask). Skips words with repeating letters.
    """
    words = []
    with open(filepath, "r") as f:
        for line in f:
            word = line.strip()
            if len(word) == 5 and len(set(word)) == 5:
                words.append((word, word_to_bitmask(word)))
    print(f"✅ Loaded {len(words):,} valid 5-letter words.")
    return words

def load_quads(filepath: str) -> List[Tuple[List[str], int]]:
    """
    Loads 4-word combinations (quads) from file and returns a list of:
    ([word1, word2, word3, word4], combined_bitmask)
    """
    quads = []
    with open(filepath, "r") as f:
        for line in f:
            words = line.strip().split()
            if len(words) != 4:
                continue
            combined_mask = 0
            for word in words:
                combined_mask |= word_to_bitmask(word)
            quads.append((words, combined_mask))
    print(f"✅ Loaded {len(quads):,} valid quads.")
    return quads

def chunked(data: List, size: int):
    """
    Splits the data into chunks of given size for parallel processing.
    """
    for i in range(0, len(data), size):
        yield i, data[i:i + size]

def process_chunk(start_idx: int, chunk: List[Tuple[List[str], int]], all_words: List[Tuple[str, int]]) -> List[List[str]]:
    """
    Processes a chunk of quads. For each quad, checks each word to find
    a 5th word that brings the total to at least 20 unique letters.
    Returns a list of valid quintuples.
    """
    pid = os.getpid()
    print(f"🚀 Worker PID {pid} starting chunk at index {start_idx} with {len(chunk)} quads")

    results = []
    for quad_words, quad_mask in chunk:
        for word, word_mask in all_words:
            if word in quad_words:
                continue  # Skip if the word is already in the quad

            total_mask = quad_mask | word_mask
            total_unique_letters = bin(total_mask).count("1")

            if total_unique_letters >= 24:
                quintuple = quad_words + [word]
                results.append(quintuple)

    print(f"✅ Worker PID {pid} finished chunk at index {start_idx} with {len(results)} results")
    return results

def main():
    print("📂 Loading data...")
    all_words = load_words(WORDS_FILE)
    all_quads = load_quads(QUADS_FILE)

    seen_quintuples: Set[frozenset] = set()
    total_found = 0
    total_written = 0

    futures = []

    print(f"🧠 Submitting jobs to {CPU_COUNT} worker processes...")
    with ProcessPoolExecutor(max_workers=CPU_COUNT) as executor:
        for start_idx, chunk in chunked(all_quads, CHUNK_SIZE):
            futures.append(executor.submit(process_chunk, start_idx, chunk, all_words))
            if len(futures) % 50 == 0:
                print(f"📦 Submitted {len(futures):,} chunks...")

        print("⏳ Collecting results as jobs complete...")
        with open(OUTPUT_FILE, "w") as f:
            for i, future in enumerate(as_completed(futures)):
                try:
                    results = future.result()
                    print(f"📥 Received results from job {i} with {len(results)} quintuples")
                    for quintuple in results:
                        key = frozenset(quintuple)
                        if key not in seen_quintuples:
                            seen_quintuples.add(key)
                            f.write(" ".join(quintuple) + "\n")
                            total_written += 1
                    total_found += len(results)
                except Exception as e:
                    print(f"❌ Error in job {i}: {e}")

                if i % 10 == 0:
                    print(f"🔄 {i:,}/{len(futures):,} jobs done | Found: {total_found:,} | Written: {total_written:,}")

    print(f"\n✅ COMPLETE! Found {total_found:,} total | Written {total_written:,} unique quintuples")
    print(f"📝 Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
