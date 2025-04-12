import itertools
import threading
from queue import Queue

INPUT_FILE = "five_letter_words.txt"
OUTPUT_FILE = "five_word_combinations.txt"
THREAD_COUNT = 8  # Adjust based on your CPU

found_count = 0
checked_count = 0
found_count_lock = threading.Lock()

def load_words():
    with open(INPUT_FILE, "r") as f:
        return [line.strip() for line in f if len(line.strip()) == 5]

def has_all_unique_letters(words):
    return len(set(''.join(words))) == 25

def find_missing_letter(words):
    all_letters = set("abcdefghijklmnopqrstuvwxyz")
    used = set(''.join(words))
    diff = all_letters - used
    return diff.pop() if len(diff) == 1 else None

def worker(queue: Queue, lock: threading.Lock):
    global found_count, checked_count
    while True:
        combo = queue.get()
        if combo is None:
            break

        with found_count_lock:
            checked_count += 1
            if checked_count % 100000 == 0:
                print(f"Checked: {checked_count:,} | Found: {found_count:,}")

        if has_all_unique_letters(combo):
            missing = find_missing_letter(combo)
            if missing:
                line = f"{missing}: {', '.join(combo)}\n"
                with lock:
                    with open(OUTPUT_FILE, "a") as f:
                        f.write(line)
                    found_count += 1

        queue.task_done()

def main():
    global found_count, checked_count
    print("Loading words...")
    words = load_words()
    print(f"Loaded {len(words)} words.")

    print("Preparing combinations...")
    queue = Queue(maxsize=10000)
    file_lock = threading.Lock()

    print(f"Starting {THREAD_COUNT} threads...")
    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker, args=(queue, file_lock))
        t.start()
        threads.append(t)

    print("Searching for valid combinations (this may take a while)...")
    for combo in itertools.combinations(words, 5):
        queue.put(combo)

    # Signal threads to shut down
    for _ in range(THREAD_COUNT):
        queue.put(None)

    for t in threads:
        t.join()

    print(f"\nDONE! Checked {checked_count:,} combinations.")
    print(f"Found {found_count:,} valid combinations.")
    print(f"Results written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
