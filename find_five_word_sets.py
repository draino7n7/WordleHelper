import os
import itertools
import sys
from multiprocessing import Pool, cpu_count
from typing import List, Set

WORD_LIST_FILE = "five_letter_words.txt"
OUTPUT_FILE = "five_word_sets.txt"
MAX_RESULTS = None  # Find all valid sets

# Convert each word to a 26-bit bitmask for fast overlap checks
def word_to_bitmask(word: str) -> int:
    mask = 0
    for ch in word:
        mask |= 1 << (ord(ch) - ord('a'))
    return mask

def load_words() -> List[str]:
    with open(WORD_LIST_FILE, "r") as f:
        words = [line.strip() for line in f if len(line.strip()) == 5]
    print(f"✅ Loaded {len(words):,} words from file.")
    return words

def search_from_root(index: int, total: int, root_word: str, word_list: List[str], word_masks: List[int]) -> List[List[str]]:
    root_mask = word_to_bitmask(root_word)
    results = []
    total_paths = 0
    seen_paths = set()

    def dfs(path: List[str], used_mask: int, depth: int, start_index: int):
        nonlocal total_paths
        if len(path) == 5:
            if bin(used_mask).count("1") == 25:
                key = tuple(sorted(path))
                if key not in seen_paths:
                    seen_paths.add(key)
                    results.append(path)
                    print(f"🎯 Found valid set from '{root_word}': {path}")
            return

        for i in range(start_index, len(word_list)):
            word = word_list[i]
            mask = word_masks[i]
            if word in path:
                continue
            if used_mask & mask == 0:
                total_paths += 1
                if total_paths % 10000 == 0:
                    print(f"🔄 [{root_word}] Explored {total_paths} paths...")
                dfs(path + [word], used_mask | mask, depth + 1, i + 1)

    print(f"🔍 ({index + 1}/{total}) Starting DFS for root word: {root_word}")
    dfs([root_word], root_mask, 1, 0)
    print(f"✅ Finished DFS for '{root_word}' — Found {len(results)} sets after {total_paths} paths")
    return results

def worker_task(args):
    index, total, root_word, word_list, word_masks = args
    return search_from_root(index, total, root_word, word_list, word_masks)

def main():
    words = load_words()
    masks = [word_to_bitmask(word) for word in words]

    print(f"🚀 Launching multiprocessing search on {cpu_count()} cores...")
    total_words = len(words)
    with Pool(cpu_count()) as pool:
        args = [(i, total_words, word, words, masks) for i, word in enumerate(words)]
        result_sets = []
        for i, result in enumerate(pool.imap_unordered(worker_task, args, chunksize=1)):
            if result:
                result_sets.extend(result)
                print(f"\n✅ Batch {i}: Found {len(result)} sets (Total so far: {len(result_sets)})")

    with open(OUTPUT_FILE, "w") as f:
        for result in result_sets:
            f.write(", ".join(result) + "\n")

    print(f"\n✅ DONE. Total valid sets found: {len(result_sets)}")
    print(f"📝 Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
