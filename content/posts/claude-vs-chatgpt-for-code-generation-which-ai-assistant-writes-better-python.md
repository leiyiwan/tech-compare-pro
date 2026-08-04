---
title: "Claude vs ChatGPT for Code Generation: Which AI Assistant Writes Better Python?"
date: 2026-07-01T13:04:22+08:00
draft: false
tags: ["AI", "ChatGPT", "Claude", "Python"]

---


# Claude vs ChatGPT for Code Generation: Which AI Assistant Writes Better Python?

When GitHub’s 2024 developer survey reported that 92% of programmers now use AI coding assistants, the question shifted from "should I use one?" to "which one should I use?" For Python developers, the choice often narrows to two heavyweight contenders: Anthropic's Claude and OpenAI's ChatGPT. Both are capable of generating functional code, refactoring legacy scripts, and explaining complex algorithms. But they approach the task with different philosophies—and the difference shows up in the output.

I spent two weeks stress-testing both models on a series of realistic Python challenges, ranging from data wrangling to API design. Here’s what I found.

## The Test Setup

To keep things fair, I used the same prompts for both models—Claude 3.5 Sonnet (via API) and GPT-4o (via ChatGPT Plus). Each test involved a specific coding task with clear requirements but enough ambiguity to force the model to make design decisions. I evaluated the results on four criteria:

1. **Correctness**: Does it run without errors?
2. **Readability**: Can a human easily understand it?
3. **Efficiency**: Is the algorithm sensible for the problem size?
4. **Robustness**: Does it handle edge cases gracefully?

The tasks included: a CSV data parser with error handling, a recursive file tree walker, a REST API endpoint using FastAPI, and a performance-sensitive function for processing large lists.

## Round 1: Data Parsing and Error Handling

**The prompt**: *"Write a Python function that reads a CSV file with columns 'name', 'age', 'email'. Skip malformed rows and return a list of dictionaries. Handle missing values and type errors gracefully."*

Both models produced workable solutions. But the differences were telling.

**ChatGPT** delivered a compact function using `csv.DictReader` with a `try/except` block that caught `ValueError` and `KeyError`. It skipped bad rows and filled missing ages with `None`. Clean, conventional, and about 20 lines.

**Claude** took a different route. It built a small validation layer with a custom exception class, used type hints extensively, and added a `warnings` module to log skipped rows rather than silently dropping them. The code was longer—around 45 lines—but it felt like reading a well-structured module from a production codebase.

**Verdict**: ChatGPT wins on brevity and speed of implementation. Claude wins on robustness and maintainability. For a quick script, ChatGPT is better. For code that will live in a shared repository, Claude's defensive style pays off.

## Round 2: Recursive File Tree Walker

**The prompt**: *"Write a recursive function that walks a directory tree and returns a list of all files with their sizes, sorted by size descending."*

This is a classic interview question, so both models had plenty of training data to draw from.

**ChatGPT** produced a straightforward recursive function using `os.scandir()`, collecting `(path, size)` tuples, and sorting with `sorted(..., reverse=True)`. It handled permission errors with a simple `except OSError: pass`. Functionally correct, but the bare `pass` felt like a cop-out—silent failures are a common source of debugging headaches.

**Claude** implemented the same logic but added a `PermissionError` handler that logs the inaccessible directory to `stderr`. It also used `pathlib.Path.rglob()` instead of manual recursion, which is both more Pythonic and less error-prone. The final output was 15 lines shorter than ChatGPT's version.

**Verdict**: Claude wins this round. The `pathlib` approach is idiomatic modern Python, and the error logging shows an understanding of real-world deployment where permissions vary.

## Round 3: FastAPI Endpoint

**The prompt**: *"Create a FastAPI endpoint that accepts a POST request with a JSON payload containing 'username' and 'message', validates the input, and stores it in an in-memory list. Include basic rate limiting."*

This task required more than just syntax—it demanded API design judgment.

**ChatGPT** returned a complete FastAPI app with Pydantic models for validation, a simple in-memory store, and a decorator-based rate limiter using `time.time()` and a sliding window. It worked, but the rate limiter was naive: it tracked a single global counter rather than per-user limits, which is rarely what you want in production.

**Claude** also used Pydantic but went further. It added a `UserRateLimit` class that stored timestamps per username, implemented a proper token bucket algorithm, and included a `Retry-After` header in the 429 response. The code was more complex, but it was also production-ready.

**Verdict**: Claude wins on design sophistication. ChatGPT's solution is fine for a demo; Claude's is fine for a real service. If you're building an MVP quickly, ChatGPT saves time. If you're building something that will face real traffic, Claude's extra effort pays off.

## Round 4: Performance-Critical List Processing

**The prompt**: *"Given a list of 10 million integers, write a function that returns the top 10 most frequent numbers. Optimize for speed and memory."*

This is where the models' underlying training and reasoning patterns became obvious.

**ChatGPT** suggested using `collections.Counter` with `.most_common(10)`. That's the obvious, correct answer—and it runs in O(n) time with minimal code. It also added a note about using `heapq` if the input were a stream rather than a static list.

**Claude** proposed the same `Counter` approach but added a comparison benchmark against a manual dictionary implementation. It also discussed time complexity in the comments and included a `if __name__ == "__main__"` block with sample timing code. The extra context was educational, but it added noise to what should be a simple function.

**Verdict**: ChatGPT wins this round. When the problem is well-defined and the optimal solution is standard, ChatGPT gets to the point faster. Claude's added commentary, while insightful, felt like over-engineering for a straightforward task.

## Head-to-Head Comparison

| Criterion | ChatGPT (GPT-4o) | Claude (3.5 Sonnet) |
|-----------|------------------|---------------------|
| Code correctness | Excellent | Excellent |
| Readability | Good (concise) | Very good (verbose but clear) |
| Idiomatic Python | Strong | Stronger (pathlib, type hints) |
| Error handling | Basic | Thorough |
| Design judgment | Good for quick fixes | Good for production systems |
| Response speed | Fast | Slightly slower on complex prompts |
| Explanation quality | Clear but brief | Detailed, often with rationale |

## When to Choose ChatGPT

ChatGPT is the better choice when you need **speed and brevity**. If you're prototyping, writing a one-off script, or debugging a specific error, GPT-4o gets you to a working solution with minimal friction. Its responses are more direct, and it tends to assume you want the simplest thing that works. It's also excellent for explaining code—its natural language explanations are crisp and well-structured.

## When to Choose Claude

Claude shines when you're building **production-grade code**. It consistently adds error handling, type hints, logging, and design patterns that make code easier to maintain. If you're working on a shared codebase, writing a library, or building a service that needs to handle unexpected inputs, Claude's defensive approach saves you debugging time later. It also tends to write more idiomatic modern Python, leveraging `pathlib`, dataclasses, and proper exception hierarchies.

## The Bottom Line

Neither model is universally "better." They're optimized for different stages of the development lifecycle. ChatGPT is your fast-thinking pair programmer for quick wins. Claude is your careful architect for long-term projects.

In practice, many developers I spoke with use both: ChatGPT for exploration and Claude for final implementation. That's not a cop-out—it's recognizing that AI assistants, like human colleagues, have different strengths.

As for which one writes better Python? If I had to pick one for a production codebase, I'd choose Claude. But if I had to ship a feature by end of day, I'd reach for ChatGPT first.

The smartest move isn't picking a side—it's knowing which tool fits the task at hand.