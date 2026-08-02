---
title: "1. ChatGPT vs. Claude: 谁更适合写代码和生成创意内容？实测5个场景对比"
date: 2026-06-12T09:03:20+08:00
draft: false
tags:

---

## ChatGPT vs. Claude: Which One Writes Better Code and Creative Content? A 5-Scenario Test

In March 2025, Anthropic released Claude 3.7 Sonnet, claiming it was the first "hybrid reasoning" model on the market. A week later, OpenAI countered with GPT-4.5, which CEO Sam Altman described as the "last non-chain-of-thought model." The war for AI dominance has never been more intense—and for developers and writers, the question is no longer "which AI is smartest?" but "which AI should I actually pay for?"

To answer that, I ran both models through five real-world scenarios: two coding tasks, two creative writing tasks, and one hybrid task. No cherry-picking, no custom prompts designed to favor one side. Here's what happened.

## The Setup: How I Tested

I used the paid tiers of both services—ChatGPT Plus (GPT-4.5) and Claude Pro (Claude 3.7 Sonnet)—with default settings. For coding, I used each model's native interface (no external IDE plugins) to keep the comparison fair. For creative tasks, I gave identical prompts with the same level of detail.

Each scenario was scored on three criteria: **output quality**, **speed**, and **practical usability** (how much editing I'd need to do before shipping).

---

## Scenario 1: Building a React Component from Scratch

**The prompt:** "Write a reusable React component for a multi-step checkout form with validation. Include TypeScript types, error handling, and a clean API for parent components."

Both models produced functional code. But the differences were immediately visible.

**ChatGPT (GPT-4.5):** Delivered a 180-line component with a custom `useReducer` hook for state management. The TypeScript types were thorough, and it automatically included a `FormData` interface that I hadn't asked for. The error messages were human-readable, not just generic strings. It also added a `useMemo` optimization for the validation logic—something I would have done myself.

**Claude (3.7 Sonnet):** Produced a 210-line component using `useState` with a more verbose structure. The validation logic was split into separate functions, which was cleaner to read. However, it used a `window.confirm()` dialog for the final submission step—a pattern most production React apps avoid. I'd have to refactor that.

**Verdict:** ChatGPT wins on code quality. Its output was more production-ready, and the `useReducer` pattern is the industry standard for complex forms. Claude's code was readable but required more refactoring to integrate into a real codebase.

---

## Scenario 2: Debugging a Tricky Race Condition

**The prompt:** "Here's a JavaScript function that fetches user data and updates a cache. It occasionally throws 'Cannot read properties of undefined.' Can you find the bug and fix it?"

I pasted a deliberately buggy function with a race condition between two async calls.

**ChatGPT:** Identified the issue in 12 seconds—the second async call was reading `cache.users` before the first call had populated it. It rewrote the function using `Promise.allSettled()` and added a comment explaining the fix. It also flagged a secondary issue: the code wasn't handling network timeouts.

**Claude:** Took 18 seconds and initially suggested the bug was in the error handling, not the race condition. When I pushed back, it corrected itself and provided a fix using a mutex pattern. The solution worked, but it was over-engineered for the problem—a simple flag or `Promise.all` would have sufficed.

**Verdict:** ChatGPT wins decisively. It found the root cause faster and suggested a more elegant fix. Claude's initial misdiagnosis is a common issue with its "reasoning" mode—it sometimes over-thinks simple problems.

---

## Scenario 3: Writing a Product Description (E-commerce)

**The prompt:** "Write a product description for a wireless mechanical keyboard. Target audience: remote workers who value ergonomics. Tone: professional but friendly. Include 3 key selling points."

**ChatGPT:** Produced a 150-word description that opened with a pain point ("Eight hours of typing shouldn't leave your wrists aching"), followed by the three selling points (hot-swappable switches, Bluetooth multi-device pairing, and a 400-hour battery). It ended with a soft call-to-action. The tone was warm but not salesy.

**Claude:** Generated a 180-word description that was more descriptive but less focused. It spent two sentences on the aesthetic design ("brushed aluminum frame, backlit keys") before getting to the ergonomics. The selling points were buried in the middle. The tone was competent but felt more like a spec sheet than a story.

**Verdict:** ChatGPT wins. Its copy followed the classic AIDA formula (Attention, Interest, Desire, Action) more naturally. Claude's version wasn't bad—it just lacked the strategic flow that makes product copy effective.

---

## Scenario 4: Short Story with a Specific Mood

**The prompt:** "Write a 500-word short story about a lighthouse keeper who discovers a message in a bottle. Mood: melancholic but hopeful. Use second-person point of view."

**ChatGPT:** Delivered a 520-word story that nailed the second-person POV. The prose was restrained—"You've read the same logbook entry three times tonight, and the words still won't stay put." The melancholic tone was consistent, and the ending ("You fold the note, tuck it into your coat, and leave the lamp burning just a little longer") felt earned.

**Claude:** Produced a 540-word story that was more poetic but less disciplined. Some sentences were gorgeous—"The sea is a liar that tells only the truth at midnight."—but the second-person POV slipped into third-person twice, which broke immersion. The hopeful ending felt tacked on rather than organic.

**Verdict:** Claude wins on raw prose quality, but ChatGPT wins on consistency and craft. For a professional writer who can fix POV slips, Claude's draft might be more inspiring. For someone who needs a nearly-final draft, ChatGPT is safer. **I'll call this a tie.**

---

## Scenario 5: Hybrid Task—Technical Blog Post with Code Snippets

**The prompt:** "Write a blog post explaining how to use WebSockets in a React app. Include a code example, explain the common pitfalls, and keep it accessible to mid-level developers."

**ChatGPT:** Produced a 900-word post with a clear structure (introduction, setup, code walkthrough, pitfalls, conclusion). The code example was accurate and included proper cleanup in `useEffect`. The pitfalls section covered reconnection logic, memory leaks, and stale closures—all real issues mid-level devs face.

**Claude:** Generated a 1,100-word post that was more comprehensive but rambled. The code example was correct, but the explanation was dense—it assumed knowledge of `useRef` and `useCallback` without explaining them. The pitfalls section was good but buried under tangential discussion of server-side architecture.

**Verdict:** ChatGPT wins. It understood the target audience better and delivered a post that a mid-level developer could actually follow. Claude's version felt like it was written for a senior engineer, which wasn't the brief.

---

## The Scorecard and Final Takeaway

| Scenario | Winner |
|----------|--------|
| React Component | ChatGPT |
| Debugging | ChatGPT |
| Product Copy | ChatGPT |
| Short Story | Tie |
| Hybrid Blog Post | ChatGPT |

**ChatGPT won 4 out of 5 scenarios.** The margin was narrow in the creative task, but for coding and practical content creation, GPT-4.5 consistently produced output that was more production-ready and better aligned with the prompt.

That said, Claude isn't a bad tool. Its prose is often more elegant, and its "thinking" mode can be useful for complex architectural questions. But in my testing, that thinking mode led to over-engineering in simple tasks and occasional misdiagnoses.

**The practical takeaway:** If you're a developer or a content creator who needs reliable, efficient output, ChatGPT is the safer bet today. If you're a fiction writer or someone who wants more poetic language and doesn't mind editing heavily, Claude might be worth the subscription.

The AI race is far from over. Both companies are shipping updates monthly, and the gap could easily close—or reverse—by the end of 2025. For now, though, if I had to pick one tool to keep for both coding and writing, I'd pick ChatGPT. The margin isn't huge, but it's consistent—and in a production environment, consistency beats brilliance every time.