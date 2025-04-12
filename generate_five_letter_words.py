import requests

# Source: https://github.com/tabatkins/wordle-list/blob/main/words
WORDLE_WORD_LIST_URL = "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words"
OUTPUT_FILE = "five_letter_words.txt"

def is_valid(word):
    word = word.lower()
    return len(word) == 5 and word.isalpha() and len(set(word)) == 5

def main():
    print("🌐 Downloading Wordle word list...")
    response = requests.get(WORDLE_WORD_LIST_URL)
    if response.status_code != 200:
        print(f"❌ Failed to download word list (status code {response.status_code})")
        return

    raw_words = response.text.strip().split("\n")
    valid_words = [word for word in raw_words if is_valid(word)]

    with open(OUTPUT_FILE, "w") as f:
        for word in valid_words:
            f.write(word + "\n")

    print(f"✅ Saved {len(valid_words):,} valid 5-letter Wordle words with no repeating letters to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    main()
