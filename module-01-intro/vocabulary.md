# GenAI Vocabulary

Terms selected and explained in my own words (Module 1).

### LLM (Large Language Model)
**Definition:** A program trained on a lot of books, websites and articles. It learns statistical patterns of language and generates human-like text: it can analyze questions and answer them, but it does not truly understand like a human.
**Usage:** The base of all tools in the report — coding assistants, RAG systems and agents are built on top of an LLM.

### Attention mechanism
**Definition:** An approach that allows a model to focus on the most relevant parts of the input data and pay less attention to the rest.
**Usage:** Mentioned in the introduction as one of the technologies (together with deep learning) that made modern LLMs possible.

### Next-token prediction
**Definition:** The way an LLM generates text: it always predicts only one next token based on the previous context. By repeating this step in a loop it builds a whole answer, which looks coherent but is not guaranteed to be true.
**Usage:** Explains in the introduction why model outputs can sound convincing and still be wrong.

### Context window
**Definition:** The active workspace of a model, its short-term memory. It has a limited size in tokens — anything that does not fit is not seen by the model.
**Usage:** A key challenge for coding assistants in large codebases and for log analysis, where huge logs must be filtered before reaching the model.

### Prompt
**Definition:** A message or question (instruction) that tells a model what to do.
**Usage:** In RAG, retrieved document chunks are added to the prompt so the model answers using company data.

### AI agent
**Definition:** A program that can work intelligently and achieve a goal on its own: it plans steps and uses tools such as files, terminal, search or APIs.
**Usage:** Agents are the core of the Agentic SDLC use case — they take a ticket, edit code, run tests and open a pull request.

### Agentic platform
**Definition:** Software that lets us build and run AI agents, combine several of them and integrate them with other services.
**Usage:** EPAM AI/Run CodeMie is an example of an agentic platform from the report.

### Copilot
**Definition:** A category of AI tools where AI is added as a plugin or "companion" to existing software, for example code completion and chat inside an IDE.
**Usage:** GitHub Copilot is the best-known example in the coding assistants use case.

### AI-native IDE
**Definition:** A code editor built around AI from the start (chat, agent mode, vibe coding) instead of getting AI as a plugin.
**Usage:** Cursor and Windsurf are examples of AI-native IDEs in the report.

### Vibe coding
**Definition:** A way of developing software by talking to AI in natural language instead of writing code yourself.
**Usage:** The main interaction style of AI-native IDEs.

### Prompt injection
**Definition:** A security trick where someone hides commands in data that AI reads (a web page, an issue, a file), so the AI follows them instead of the user's instructions.
**Usage:** One of the security risks of autonomous agents with access to a repository and terminal.

### Hallucination
**Definition:** When AI produces false or misleading answers, but presents them in a confident manner.
**Usage:** A weak point in almost every use case — RAG reduces hallucinations, but does not eliminate them.
