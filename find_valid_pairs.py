import itertools

INPUT_FILE = "five_letter_words.txt"
OUTPUT_FILE = "valid_pairs.txt"

def word_to_bitmask(word):
    mask = 0
    for ch in word:
        mask |= 1 << (ord(ch) - ord('a'))
    return mask

def load_words():
    with open(INPUT_FILE, "r") as f:
        words = [line.strip() for line in f if len(line.strip()) == 5]
    return [(word, word_to_bitmask(word)) for word in words]

def main():
    words = load_words()
    print(f"Loaded {len(words)} words.")
    valid_pairs = 0
    checked = 0

    with open(OUTPUT_FILE, "w") as out:
        for i, (word1, mask1) in enumerate(words):
            for word2, mask2 in words[i + 1:]:
                checked += 1
                if mask1 & mask2 == 0:
                    out.write(f"{word1} {word2}\n")
                    valid_pairs += 1

            if i % 100 == 0:
                print(f"Checked: {checked:,} pairs | Found: {valid_pairs:,} valid pairs")

    print(f"\n✅ Done! {valid_pairs:,} valid 2-word pairs written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
