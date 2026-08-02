---
title: "1. ChatGPT vs. Claude：2024年编程助手实测，谁写代码更靠谱？"
date: 2026-06-03T13:02:24+08:00
draft: false
tags:

---

# ChatGPT vs. Claude: Which AI Writes Better Code in 2024?

In June 2024, Stack Overflow's annual developer survey dropped a bombshell: 76% of developers reported using or planning to use AI tools in their workflow, yet only 43% said they trust the output. That trust gap is exactly where the ChatGPT vs. Claude debate lives. Both models claim to be coding powerhouses, but when the rubber meets the road—or the cursor meets the terminal—they behave very differently.

I spent two weeks putting both through identical, real-world coding tasks: refactoring a messy Python script, debugging a race condition in Go, building a React component from a vague spec, and writing a SQL query for a tricky reporting problem. Here’s what actually happened.

## The Setup: Same Prompts, Same Hardware, No Cherry-Picking

Before we dive in, let’s be clear about the test parameters. I used **ChatGPT-4o** (the default model for Plus users as of late 2024) and **Claude 3.5 Sonnet** (Anthropic’s mid-tier but most capable coding model). Both were accessed via their web interfaces with default temperature settings. I did not use custom GPTs, Copilot integrations, or API-level tweaks. The goal was to simulate what a typical working developer experiences.

I also tracked three metrics for each task: **correctness** (does it run?), **efficiency** (is the code idiomatic and clean?), and **explanation quality** (can I learn from the answer?).

## Task 1: Refactoring a Legacy Python Script

The prompt: *“Refactor this 200-line Python script that scrapes a website and saves data to CSV. It works but is slow and hard to maintain. Make it modular and add error handling. Here’s the code…”* (I used a genuinely ugly script with nested loops, global variables, and no exception handling.)

**ChatGPT-4o** immediately split the code into three functions (`fetch_page`, `parse_content`, `save_to_csv`) and added a `main()` guard. It also introduced `requests.Session()` for connection reuse, which was a smart performance catch. However, its error handling was generic—it wrapped everything in `try/except Exception` without specifying what to catch. When I pushed back asking for granular exception handling, it complied but with some friction.

**Claude 3.5 Sonnet** took a different approach. It first asked a clarifying question: *“Should the CSV writing be atomic (write to temp then rename) to avoid corruption on failure?”* That level of forethought was impressive. Its refactor included custom exception classes (`NetworkError`, `ParseError`) and a retry decorator with exponential backoff. The code was longer but production-ready out of the box.

**Verdict:** Claude wins on correctness and insight; ChatGPT wins on brevity. If you need a quick cleanup, ChatGPT is fine. If you’re shipping to production, Claude’s version required zero additional edits.

## Task 2: Debugging a Go Race Condition

This is where things got interesting. I provided a small Go program with a classic data race—two goroutines writing to the same map without a mutex. The prompt: *“This crashes intermittently with ‘fatal error: concurrent map writes.’ Fix it and explain why.”*

**ChatGPT-4o** correctly identified the race and suggested a `sync.Mutex`. Its explanation was clear: “The map is not thread-safe; concurrent writes cause a panic.” It also offered an alternative using `sync.Map` for read-heavy workloads. Solid, but the explanation felt like a textbook definition.

**Claude 3.5 Sonnet** did something unexpected. It not only fixed the race with a mutex but also pointed out a secondary issue I hadn’t mentioned: the program had a potential deadlock if a third goroutine tried to acquire the lock during a long-running operation. It suggested using `sync.RWMutex` instead and explained the trade-off between reader and writer locks. Then it provided a test case that reproduced the original bug and verified the fix.

**Verdict:** Claude wins decisively. It found a bug I didn’t even ask about, which is exactly what you want from a senior reviewer. ChatGPT’s answer was correct but shallow.

## Task 3: Building a React Component from a Vague Spec

The prompt: *“Create a React component for a user profile card that shows avatar, name, bio, and a follow button. The follow button should toggle state and persist to localStorage. Style it with Tailwind.”*

**ChatGPT-4o** produced a functional component in about 30 seconds. It used `useState` for the follow state, `useEffect` to sync with localStorage, and proper Tailwind classes. The code was clean and idiomatic. However, it missed a subtle detail: it didn’t handle the case where localStorage might have an invalid value (e.g., a string “true” vs. boolean `true`). Minor, but it would cause a bug in production.

**Claude 3.5 Sonnet** asked for clarification upfront: *“Should the follow state be per-user (keyed by user ID) or global?”* This is a critical question for a profile card component. After I confirmed per-user, it implemented a custom hook (`useFollowState`) that encapsulated the localStorage logic, making the component reusable. It also added a loading state for the avatar image and a graceful fallback if the image fails to load.

**Verdict:** Claude again. ChatGPT’s answer was faster, but Claude’s was more thoughtful. The per-user keying question alone prevented a real-world bug.

## Task 4: Writing a Complex SQL Query

The prompt: *“Write a SQL query to find the top 3 customers by total revenue in the last 30 days, but exclude customers who have returned more than 10% of their orders. Use a CTE.”*

**ChatGPT-4o** wrote a correct query using two CTEs: one for revenue, one for return rates. The logic was sound, and it used `ROW_NUMBER()` for ranking. It even added a comment explaining each step. However, it assumed a specific schema (e.g., `orders` table with `customer_id`, `amount`, `order_date`, `returned` boolean) without asking. If the actual schema differed, the query would fail.

**Claude 3.5 Sonnet** also wrote a correct query but with one key difference: it provided two versions—one for a normalized schema and one for a denormalized one—and explained when to use each. It also added an index recommendation on `(customer_id, order_date)` to improve performance.

**Verdict:** Tie on correctness, Claude on usability. ChatGPT’s answer is fine if you control the schema; Claude’s is better for real-world ambiguity.

## The Bigger Picture: Strengths and Weaknesses

After all four tasks, a pattern emerged.

**ChatGPT-4o strengths:**
- **Speed:** It responds faster and with less hedging.
- **Brevity:** It gives you the minimal answer, which is often what you want for quick fixes.
- **Ecosystem:** If you use ChatGPT’s Code Interpreter or custom GPTs, it can execute code directly in the chat, which is a huge plus for testing snippets.

**ChatGPT-4o weaknesses:**
- **Shallow analysis:** It often misses edge cases or secondary bugs.
- **Overconfidence:** It rarely asks clarifying questions, which means it can generate code that looks right but fails in context.

**Claude 3.5 Sonnet strengths:**
- **Depth of understanding:** It consistently identified issues I didn’t mention.
- **Proactive clarification:** It asks relevant questions before diving in, which saves time in the long run.
- **Production-ready output:** Its code is more defensively written and better documented.

**Claude 3.5 Sonnet weaknesses:**
- **Verbosity:** Its answers are longer and can feel over-engineered for simple tasks.
- **Slower responses:** The extra thinking time is noticeable, especially on long prompts.

## Which One Should You Use?

The honest answer: **it depends on your workflow.**

If you’re a **senior developer** who wants a second pair of eyes on tricky logic, Claude 3.5 Sonnet is the stronger choice. Its ability to spot secondary issues and ask clarifying questions makes it feel like a thoughtful colleague rather than a code generator.

If you’re a **junior developer** or you’re doing **rapid prototyping**, ChatGPT-4o is more approachable. Its fast, concise answers are perfect for unblocking yourself quickly. Just be prepared to debug edge cases yourself.

If you’re **learning to code**, I’d actually recommend ChatGPT. Its explanations are more didactic and easier to follow. Claude’s answers often assume you already understand the underlying concepts.

One more note: both models are improving rapidly. As of late 2024, Claude 3.5 Sonnet has a slight edge in coding benchmarks like SWE-bench, but ChatGPT’s ecosystem advantages (plugins, DALL-E integration, Code Interpreter) make it a better all-around tool.

## The Bottom Line

Neither model is “more reliable” in absolute terms. They are reliable in different ways. ChatGPT is reliable for speed and simplicity; Claude is reliable for correctness and depth.

My recommendation: use both. Keep ChatGPT open for quick lookups and boilerplate. Use Claude for code reviews, complex debugging, and any task where a subtle bug could cost you hours. The 20 minutes it takes to learn both interfaces is an investment that pays off almost immediately.

In the words of one Reddit user on r/ClaudeAI: “ChatGPT writes code that passes tests. Claude writes code that survives production.” After two weeks of testing, I’m inclined to agree.