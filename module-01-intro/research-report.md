# Research on Generative AI Applications in Software Development

**Author:** Yergazy Nurmaganbetov
**Course:** Generative AI for Software Development — Module 1 (Course Introduction)
**Date:** November 2026

## Introduction

Generative AI (GenAI) is built on artificial neural networks (ANN) trained with deep learning and the attention mechanism. A large language model (LLM) works by next-token prediction: it statistically continues a sequence of tokens using associations learned from training data and the short context provided in a prompt. The model can be described as lossy compression of its training data — it cannot reproduce the data exactly, so outputs may sound convincing and still be wrong (hallucinations).

Modern GenAI systems are multimodal (text, code, images, speech, documents) and agentic: an AI agent plans a task, calls tools (file system, terminal, search, APIs) and coordinates smaller specialized steps. In software development this ranges from simple copilots inside an IDE to agentic harnesses and platforms that take a ticket and deliver a pull request.

This report reviews seven use cases. For each one it describes business value, technical challenges, weak points and existing implementations. Weak points always include three cross-cutting risks: **cost** (tokenomics), **security / data protection** and **over-dependence on automation**.

## Contents

1. [AI coding assistants](#1-ai-coding-assistants)
2. [AI-assisted test generation](#2-ai-assisted-test-generation)
3. [Log analysis, debugging and incident investigation](#3-log-analysis-debugging-and-incident-investigation)
4. [RAG over internal knowledge and data](#4-rag-over-internal-knowledge-and-data)
5. [Agentic SDLC: from ticket to pull request](#5-agentic-sdlc-from-ticket-to-pull-request)
6. [Small and local LLMs](#6-small-and-local-llms)
7. [Multimodal document and speech processing](#7-multimodal-document-and-speech-processing)

---

## 1. AI coding assistants

**Business value.** Coding assistants are the most widely adopted GenAI tool in software development. They work in two forms: the *copilot* approach adds code completion and chat to an existing IDE, while *AI-native* IDEs are built around natural-language interaction ("vibe coding") and agent mode from the start. Typical tasks — boilerplate, refactoring, updating third-party dependencies, explaining unfamiliar code — become much faster, which shortens onboarding and lets developers spend more time on design and review.

**Technical challenges and weak points.** The assistant only sees what fits into its context window, so in large codebases it may miss project conventions or suggest code that compiles but breaks a hidden contract. Hallucinated APIs, outdated library versions and insecure patterns are common, so every suggestion still needs code review and tests. Costs grow with premium models and agent mode usage (more tokens per request). Sending source code to an external LLM provider raises intellectual-property and compliance questions. Finally, over-dependence is a real risk: developers who accept suggestions without understanding them lose skills and produce code that nobody on the team fully owns.

**Existing implementations:**
- [GitHub Copilot](https://github.com/features/copilot) — AI pair programmer for VS Code, JetBrains and other IDEs with completion, chat, agent mode and a cloud coding agent.
- [Cursor](https://cursor.com) — AI-native code editor (VS Code fork) with codebase-aware chat and agent mode.
- [Windsurf](https://windsurf.com) — AI-native IDE with the Cascade agent; acquired by Cognition (the company behind Devin), its editor now continues as Devin Desktop.
- [JetBrains Junie](https://www.jetbrains.com/junie/) — JetBrains coding agent that works together with AI Assistant inside IntelliJ IDEA, PyCharm, WebStorm and other IDEs.

---

## 2. AI-assisted test generation

**Business value.** Writing and maintaining tests is time-consuming, and coverage is usually the first thing cut under deadline pressure. GenAI can generate unit and integration tests for existing code, propose edge cases, create test data and keep tests up to date after refactoring. This makes approaches like TDD and DDD easier to apply, gives legacy code a safety net before modernization, and lets QA engineers focus on test design and exploratory testing instead of boilerplate.

**Technical challenges and weak points.** A generated test usually asserts what the code *currently does*, not what it *should do* — if the code has a bug, the AI can lock that bug in as "expected behavior" and the green test suite creates false confidence. Generating good tests requires enough context about requirements, which is often missing from the code itself. Mocks for complex dependencies, flaky integration tests and test data with personal information are additional challenges. Generated suites can also grow large and expensive to maintain, so coverage numbers must not replace review of the assertions.

**Existing implementations:**
- [Qodo](https://www.qodo.ai) (formerly CodiumAI) — code-quality platform combining AI test generation in the IDE with multi-agent pull-request review.
- [Diffblue Cover](https://www.diffblue.com/cover) — autonomous agent that writes and maintains JUnit/TestNG unit tests for Java and Kotlin projects.
- [Keploy](https://keploy.io) — open-source testing agent that generates API tests and dependency mocks from real traffic, OpenAPI specs or Postman collections.
- [GitHub Copilot](https://github.com/features/copilot) — can generate tests from chat or as part of agent-mode tasks inside the IDE.

---

## 3. Log analysis, debugging and incident investigation

**Business value.** Reading huge logs, traces and stack traces is slow, especially during an incident when every minute of downtime costs money. AI debugging agents correlate errors, telemetry, recent commits and runbooks, form root-cause hypotheses and in some cases propose a code fix as a pull request. This reduces mean time to resolution (MTTR), lowers the cognitive load on on-call engineers and helps less experienced team members investigate problems they have never seen before.

**Technical challenges and weak points.** The quality of the analysis depends entirely on the quality of telemetry: poor logging and missing traces lead to confident but wrong conclusions. Logs are noisy and very large, so tools must filter and summarize before the data reaches the model's context window. Logs often contain personal data, tokens and secrets, which creates data-protection risks when they are sent to an LLM. Commercial tools are usually tied to a specific observability platform and priced per user or per data volume. Engineers still need to verify the root cause instead of blindly merging the suggested fix.

**Existing implementations:**
- [Sentry Seer](https://sentry.io/product/seer/) — AI debugging agent that uses Sentry errors, traces, logs and commit history to find root causes and open fix PRs.
- [Datadog Bits AI SRE](https://www.datadoghq.com/product/platform/bits-ai) — on-call agent that autonomously investigates alerts using telemetry and runbooks and surfaces likely root causes.

---

## 4. RAG over internal knowledge and data

**Business value.** A general-purpose LLM does not know a company's internal documentation, tickets, code or customer data. Retrieval-augmented generation (RAG) solves this: documents are split into chunks, converted into embeddings and stored in a vector database; at question time the most relevant chunks are retrieved and added to the prompt. Employees get answers grounded in company sources with links to the original documents, which reduces time spent searching, speeds up onboarding and allows analysis of customer data and feedback.

**Technical challenges and weak points.** Answer quality depends on retrieval quality — wrong chunking, outdated documents or poor ranking give the LLM the wrong context, and it will still produce a fluent answer. Access control is critical: a RAG system must respect document permissions, otherwise it leaks confidential data to the wrong people. Indexing large data sets and keeping them fresh costs compute and storage, and evaluation of RAG quality (faithfulness, relevance, recall) is hard to automate. Hallucinations are reduced but not eliminated.

**Existing implementations:**
- [Glean](https://www.glean.com) — enterprise AI search and assistant that applies permission-aware RAG across company SaaS apps.
- [LlamaIndex](https://www.llamaindex.ai) — open-source framework for building RAG pipelines and document agents over private data.
- [LangChain](https://www.langchain.com) — open-source framework and SDK for building LLM applications, including retrieval chains and agents.

---

## 5. Agentic SDLC: from ticket to pull request

**Business value.** Agentic harnesses run an AI agent in a loop with access to files, a terminal and tools: the agent studies the project, plans the change, edits code, runs tests and opens a pull request. Agentic platforms go further and orchestrate several specialized agents and integrations (Jira, Git, CI) across the whole software development life cycle (SDLC). Routine tickets, documentation updates, dependency upgrades and small bug fixes can be delegated, and developers move from writing code to reviewing it and defining tasks precisely.

**Technical challenges and weak points.** Agents need a well-described task, clear acceptance criteria and a reproducible environment; vague tickets produce large, wrong pull requests. Long agent sessions consume many tokens, so costs are less predictable than with chat. An agent with terminal and repository access is a security risk (prompt injection through issues or dependencies, accidental deletion, leaked secrets), so permissions, sandboxing and human review are required. Reviewing many AI-generated pull requests becomes the new bottleneck, and teams risk losing understanding of their own codebase.

**Existing implementations:**
- [Claude Code](https://code.claude.com) — Anthropic's agentic coding harness for the terminal, IDE, desktop and web that reads the codebase, edits files, runs commands and works with Git.
- [OpenAI Codex](https://chatgpt.com/codex/) — OpenAI coding agent available as an open-source CLI, IDE extension, desktop app and cloud service for delegated tasks.
- [GitHub Copilot coding agent](https://docs.github.com/en/copilot/using-github-copilot/coding-agent/using-copilot-to-work-on-an-issue) — an issue assigned to Copilot is implemented in a GitHub Actions environment and returned as a pull request.
- [EPAM AI/Run CodeMie](https://codemie-ai.github.io/docs/) — EPAM agentic platform with pre-built assistants and workflows for SDLC roles, plus CodeMie CLI.
- [Devin](https://devin.ai) — autonomous AI software engineer by Cognition for delegated end-to-end tasks.

---

## 6. Small and local LLMs

**Business value.** Not every task needs a frontier model. Small language models (SLM) and open-weight models such as Qwen, NVIDIA Nemotron, DeepSeek and GLM are cheaper per token, faster, and can run on-premises, on a developer laptop or on edge devices. Local deployment keeps source code and sensitive data inside the company, works offline and avoids vendor lock-in. Small models are a good fit for narrow tasks — classification, extraction, routing, code completion — and as cheap sub-agents inside a larger multi-agent system.

**Technical challenges and weak points.** Running a model locally depends on GPU memory (VRAM), model size and quantization: even small models need several gigabytes of video memory, and larger ones require server GPUs. Small models reason worse, have shorter context windows and hallucinate more on complex tasks. The team becomes responsible for inference infrastructure, updates, monitoring and security of the model itself. Licenses differ between open-weight models, and some organizations restrict models from certain vendors for compliance reasons.

**Existing implementations:**
- [Ollama](https://ollama.com) — tool for downloading and running open-weight LLMs locally with a simple CLI and REST API.
- [LM Studio](https://lmstudio.ai) — desktop application for discovering, running and serving local models through an OpenAI-compatible API.
- [NVIDIA Nemotron 3 Nano](https://huggingface.co/blog/nvidia/nemotron-3-nano-efficient-open-intelligent-models) — family of efficient open models for agentic tasks, including edge-ready small variants.
- [Hugging Face Models](https://huggingface.co/models) — catalog of open models for text generation, OCR, speech recognition, text-to-image and other tasks, with links to inference providers.

---

## 7. Multimodal document and speech processing

**Business value.** A large share of project knowledge is stored outside clean text: scanned specifications, PDFs with tables and diagrams, screenshots, recorded meetings. Multimodal models and specialized modules — OCR, speech recognition (speech-to-text), image understanding — convert this content into structured text (for example Markdown) that LLMs and RAG systems can use. Practical results include searchable requirement documents, automatic meeting transcripts and summaries, bug reports built from screenshots and accessibility features such as hands-free interfaces.

**Technical challenges and weak points.** Recognition quality drops on poor scans, handwriting, complex tables, mixed languages and accents; errors at this stage propagate to every later step. Transcripts can lose or garble meaning (for example a broken language detection in a recording), so important content needs human checking. Images, audio and video are expensive to process and contain personal data (faces, voices, documents), which raises privacy and compliance requirements. Multimodal outputs are also harder to evaluate automatically than plain text.

**Existing implementations:**
- [Mistral OCR](https://mistral.ai/news/mistral-ocr) — OCR / document-understanding API that converts PDFs and images, including tables and formulas, into Markdown for RAG.
- [OpenAI Whisper](https://github.com/openai/whisper) — open-source speech recognition model for multilingual transcription and translation that can run locally.
- [Google Gemini](https://gemini.google.com) — multimodal assistant and model family that works with text, images, audio, video and documents.

---

## Summary

| # | Use case | Main business value | Key weak point |
|---|----------|---------------------|----------------|
| 1 | AI coding assistants | Faster routine coding and onboarding | Hallucinated or insecure code, skill loss |
| 2 | Test generation | Higher coverage with less manual effort | Tests may lock in existing bugs |
| 3 | Log analysis and debugging | Lower MTTR during incidents | Depends on telemetry quality; sensitive data in logs |
| 4 | RAG over internal data | Answers grounded in company knowledge | Retrieval errors, access-control leaks |
| 5 | Agentic SDLC | Delegation of whole tickets to agents | Security of autonomous agents, review bottleneck |
| 6 | Small and local LLMs | Low cost, privacy, offline work | Hardware (VRAM) limits, weaker reasoning |
| 7 | Multimodal processing | Unlocks knowledge in documents and audio | Recognition errors propagate downstream |

Across all cases the same pattern applies: GenAI output quality depends on data and context prepared by humans, and every use case needs a human in the loop to verify results, control costs and protect data. The right tool should match the complexity and readiness of the specific task — from a simple chat question to a fully agentic workflow.
