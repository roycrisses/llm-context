import time
import random
import string
from llm_context.ranker import rank_files
from llm_context.scanner import FileInfo

def generate_random_content(n_tokens=1000):
    words = ["user", "auth", "login", "database", "connection", "query", "result", "error", "success"]
    words += ["".join(random.choices(string.ascii_lowercase, k=5)) for _ in range(50)]
    return " ".join(random.choices(words, k=n_tokens))

def benchmark():
    n_files = 1000
    files = []
    for i in range(n_files):
        files.append(FileInfo(
            path=f"/path/to/file_{i}.py",
            rel_path=f"file_{i}.py",
            content=generate_random_content(500),
            size=1000,
            extension="py",
            mtime=time.time()
        ))

    query = "how to handle user login and database connection"

    start = time.time()
    rank_files(files, query)
    end = time.time()

    print(f"Ranking {n_files} files took {end - start:.4f} seconds")

if __name__ == "__main__":
    benchmark()
