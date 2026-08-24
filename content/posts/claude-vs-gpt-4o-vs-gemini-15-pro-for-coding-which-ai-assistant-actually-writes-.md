---
title: "Claude vs GPT-4o vs Gemini 1.5 Pro for Coding: Which AI Assistant Actually Writes Better Code?"
date: 2026-08-24T17:03:09+08:00
draft: false
tags:

---

# Claude vs GPT-4o vs Gemini 1.5 Pro for Coding: Which AI Assistant Actually Writes Better Code?

In a 2024 survey by Stack Overflow, 76% of developers reported using or planning to use AI coding tools, yet only 42% said they trust the output "most of the time." That gap between adoption and confidence defines the current state of AI-assisted development. As Anthropic, OpenAI, and Google race to ship increasingly capable models, the practical question for engineers isn't which model has the flashiest benchmark scores—it's which one produces production-ready code when you're staring at a deadline.

I spent the last month running all three flagship models through a gauntlet of real-world coding tasks: refactoring legacy code, building a full-stack CRUD app, debugging a nasty concurrency issue, and writing test suites. Here’s what I found.

## The Contenders and How I Tested

Before diving into results, let’s set the baseline. All three models were tested through their respective chat interfaces with default settings:

- **Claude 3.5 Sonnet** (via claude.ai, the model behind Claude Code)
- **GPT-4o** (via ChatGPT Plus)
- **Gemini 1.5 Pro** (via Google AI Studio)

I used identical prompts for each task, set a 30-minute time cap per task, and evaluated output on four criteria: correctness, code quality (readability, structure, adherence to language idioms), completeness, and the ability to self-correct when given feedback.

The tasks were deliberately varied—not just "write a function" but messy, real-world scenarios that require context, judgment, and multi-step reasoning.

## Task 1: Refactoring a Legacy Python Module

**The setup:** A 200-line Python module with a god function that handled input validation, database calls, and response formatting. It had no tests, inconsistent naming, and a few subtle bugs hidden in nested conditionals.

**The results:**

Claude stood out immediately. It not only refactored the function into clean, single-responsibility units but also identified two actual bugs I hadn’t flagged—one involving a variable shadowing issue and another with an edge case in the validation logic. Its explanations were concise, and it offered to write tests before I asked.

GPT-4o produced a solid refactor with good structure, but it missed the bugs. The code was clean and idiomatic, but it treated the task as purely mechanical. When I pointed out the bugs, it acknowledged them and fixed them efficiently—but it required me to be the one who noticed.

Gemini 1.5 Pro was the surprise here. Its refactor was competent, and it caught one of the two bugs, but its code style felt slightly more "textbook"—correct but less thoughtful about real-world constraints like database connection handling and error recovery. It also added more comments than necessary, which is a minor annoyance but not a dealbreaker.

**Verdict:** Claude wins this round. Its ability to proactively identify latent issues is a differentiator that goes beyond code generation.

## Task 2: Building a Simple CRUD App (Node.js + Express + SQLite)

**The setup:** Build a task manager API with user authentication (JWT), CRUD endpoints, input validation, and SQLite persistence. The prompt was deliberately underspecified—no schema provided, no endpoint list, just the tech stack and feature requirements.

**The results:**

GPT-4o delivered the most complete package. It generated a well-organized project structure, wrote a sensible schema with foreign keys, included error handling middleware, and even added a basic README. The code was idiomatic Express with clean async/await patterns. It made reasonable assumptions about the JWT flow and clearly documented them.

Claude's output was comparable in quality but slightly less complete out of the box. It focused more on the core logic and assumed I'd handle certain boilerplate (like the Express app setup) myself. However, its code was marginally more readable—better variable naming, clearer separation of concerns.

Gemini 1.5 Pro produced a working app but with some notable quirks. It used a slightly outdated pattern for JWT verification, didn't include input validation on all endpoints, and its error handling was less robust. The code was functional but felt like it was written by someone who knows Express but doesn't use it daily.

**Verdict:** GPT-4o takes this one for completeness and practicality. For a developer who wants a working starting point, its output is the most copy-paste-ready.

## Task 3: Debugging a Concurrency Issue (Go)

**The setup:** A Go program with a race condition in a worker pool. Multiple goroutines were reading and writing to a shared map without synchronization, causing intermittent panics. I provided the code and a description of the symptom (random crashes under load).

**The results:**

This was the most illuminating task of the entire test.

Claude identified the race condition within seconds and, more importantly, explained *why* it was happening—the subtle interaction between the map's internal structure and concurrent reads/writes. It then provided a fix using `sync.Mutex` and also suggested a more idiomatic approach using channels, which is the Go way to handle this. It even flagged a secondary issue: a potential deadlock in the error handling path.

GPT-4o correctly identified the race condition and offered a mutex-based fix. Its explanation was accurate but more surface-level—it described what was happening but not the underlying mechanics. The fix worked, but it didn't suggest the channel-based alternative, which is the more idiomatic Go solution.

Gemini 1.5 Pro struggled here. It identified that there was a concurrency issue but initially suggested using `atomic` operations on a map, which isn't supported in Go. After I pushed back, it corrected itself and offered a mutex solution, but the back-and-forth cost time. Its explanation of the race condition was also less precise, using vague language about "potential conflicts" rather than explaining the actual memory model issues.

**Verdict:** Claude dominates. For debugging—especially concurrency—its ability to understand the underlying mechanics is unmatched in this test.

## Task 4: Writing a Test Suite (JavaScript/Vitest)

**The setup:** A utility module with functions for date formatting, string manipulation, and array operations. The module has 15 exported functions, some with edge cases that are easy to miss.

**The results:**

GPT-4o produced the most comprehensive test suite, covering all functions with a good balance of happy-path and edge-case tests. It used parameterized tests effectively and organized the file logically. Its edge-case coverage was the best of the three—it caught things like leap years, empty arrays, and unicode characters in strings.

Claude's test suite was slightly smaller but higher quality per test. It used more descriptive test names and grouped tests by function more clearly. It also wrote better assertions—using `toStrictEqual` instead of `toEqual` where appropriate, which catches more subtle bugs. However, it missed a couple of edge cases that GPT-4o caught.

Gemini 1.5 Pro wrote a functional test suite but with less thorough edge-case coverage. It also had a tendency to over-mock—testing implementation details rather than behavior, which makes tests brittle. It covered about 70% of the edge cases the other two caught.

**Verdict:** GPT-4o edges out Claude here on sheer coverage. Claude's tests were higher quality but less complete.

## The Bigger Picture: Beyond Single Tasks

After running these individual tests, I also used each tool in a simulated "work session"—a multi-hour interaction where I asked follow-up questions, requested modifications, and introduced new requirements.

This is where the differences became stark.

Claude excels at maintaining context over long conversations. It remembers constraints you mentioned earlier, applies consistent naming conventions, and doesn't contradict itself. Its code style remains uniform throughout. This makes it feel like a senior engineer who's been on the project for months.

GPT-4o is more flexible but less consistent. It sometimes "forgets" earlier decisions and regenerates code that conflicts with previous output. It's also more prone to over-engineering—adding abstractions that aren't needed for the task at hand.

Gemini 1.5 Pro has the largest context window (1 million tokens), which is useful for pasting entire codebases. But in practice, it doesn't leverage this advantage well. It tends to give more generic answers and struggles with highly specific or unusual code patterns.

## Cost and Speed Considerations

There's a practical dimension here too. In my testing:

- **GPT-4o** was the fastest to generate responses but had the most variable output quality.
- **Claude** was slightly slower but more consistent.
- **Gemini 1.5 Pro** was the slowest, especially for long-context queries.

On pricing, GPT-4o and Claude are comparable for API usage (around $5 per million input tokens and $15 per million output tokens for GPT-4o; Claude is similar). Gemini 1.5 Pro is cheaper on input tokens ($3.50 per million) but more expensive on output ($10.50 per million). For interactive coding, the differences are negligible.

## The Verdict: It Depends on Your Workflow

After a month of testing, here's my honest assessment:

**Claude is the best all-around coding assistant** if you value code quality and proactive problem-solving. Its ability to catch bugs, explain reasoning, and maintain context makes it feel like a thoughtful pair programmer. It's not always the fastest or the most complete, but it rarely produces code that makes you cringe.

**GPT-4o is the best for scaffolding and boilerplate.** If you need a complete project structure, a full test suite, or a working CRUD app quickly, GPT-4o delivers the most copy-paste-ready output. It's the best "get it done" tool, even if the code isn't always the most elegant.

**Gemini 1.5 Pro is the best for codebase analysis** thanks to its massive context window. If you need to understand a large, unfamiliar codebase, paste it all in and ask questions. But for writing code, it lags behind the other two in both quality and insight.

The practical recommendation: use all three. Keep GPT-4o for scaffolding new projects, Claude for debugging and refactoring, and Gemini for codebase comprehension. They're tools, not replacements—and knowing which tool fits which job is still the most valuable skill a developer can have.