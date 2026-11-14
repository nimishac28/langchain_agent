# Web Search Agent with Structured Output

A LangChain agent that answers questions by searching the web, then returns a typed response with the answer and the URLs it used. It pairs Grok-4 with Tavily search and uses a Pydantic schema so the output is structured data your code can use directly, not free text you have to parse.

## Why

LLMs can't answer questions about events after their training data ends. Ask one who won the 2026 FIFA World Cup and it will guess or refuse. Giving the model a search tool lets it look up current information. Requiring a structured response with sources makes each answer checkable: you can see where every claim came from.

## How it works

```
User question
      │
      ▼
┌──────────────────────┐    decides to search    ┌───────────────┐
│  Agent (Grok-4,      │ ──────────────────────► │ TavilySearch  │
│  temperature 0)      │ ◄────────────────────── │ (web results) │
└──────────────────────┘    results + URLs       └───────────────┘
      │
      ▼
AgentResponse (Pydantic)
  ├── answer:  str
  └── sources: [ { url: str }, ... ]
```

1. **Model:** Grok-4 is called through `ChatOpenAI`, pointed at xAI's OpenAI-compatible endpoint (`https://api.x.ai/v1`). Temperature is 0 for consistent answers.
2. **Tool:** `TavilySearch` gives the agent live web search. The agent decides on its own whether and when to call it.
3. **Agent:** `create_agent` runs the loop: the model reasons, calls the tool if needed, reads the results, and repeats until it can answer.
4. **Structured output:** `response_format=AgentResponse` makes the final answer follow a Pydantic schema, so it is validated and typed rather than free text.

### Response schema

```python
class Source(BaseModel):
    url: str = Field(description="The URL of the source")

class AgentResponse(BaseModel):
    answer: str = Field(description="The agent's answer to the query")
    sources: List[Source] = Field(default_factory=list,
                                  description="The list of sources used to generate the answer")
```

## Tech stack

| Layer | Tool |
|---|---|
| Agent framework | LangChain (`create_agent`) |
| LLM | xAI `grok-4` via `langchain-openai` (OpenAI-compatible API) |
| Web search | Tavily (`langchain-tavily`) |
| Output schema | Pydantic |
| Config | `python-dotenv` |

## Getting started

### Prerequisites

- Python 3.10+
- An [xAI](https://x.ai/api) API key
- A [Tavily](https://tavily.com/) API key

### Setup

```bash
git clone https://github.com/nimishac28/<repo-name>.git
cd <repo-name>
```

Using [uv](https://docs.astral.sh/uv/):
```bash
uv sync
```

Or with pip:
```bash
pip install langchain langchain-openai langchain-tavily pydantic python-dotenv
```

Create a `.env` file in the project root and add it to `.gitignore`:

```
XAI_API_KEY=your_xai_key
TAVILY_API_KEY=your_tavily_key
```

### Run

```bash
uv run main.py
# or
python main.py
```

To ask a different question, change the message in `main()`:

```python
response = agent.invoke({"messages": [HumanMessage(content="Your question here")]})
print(response["structured_response"])
```

## Example output

<!-- Paste a real run here, e.g.:
Question: Who won the FIFA 2026 World Cup?
answer='...' sources=[Source(url='...'), Source(url='...')]
-->

## Project structure

```
├── main.py          # schema, agent setup, entry point
├── pyproject.toml   # dependencies (uv)
├── .env             # API keys (not committed)
└── README.md
```

## Limitations

- **Single question per run.** The query is hardcoded in `main()`. There is no command-line input, loop, or conversation memory yet.
- **Sources are self-reported.** The model fills in the `sources` list itself. Nothing checks that each URL actually appeared in the Tavily results or supports the answer.
- **Only URLs are captured.** The schema stores no page titles or quoted snippets, so checking a claim means opening every link.
- **No error handling.** A missing API key, a failed search, or a response that doesn't match the schema will raise an unhandled exception.

## Next steps

- [ ] Accept the question as a command-line argument or run an input loop
- [ ] Add `title` and `snippet` fields to `Source`
- [ ] Check that every returned URL appears in the actual Tavily results
- [ ] Add conversation memory for follow-up questions
- [ ] Handle errors and missing keys with clear messages

## Author

**Nimisha** – [GitHub](https://github.com/nimishac28) <!-- add LinkedIn -->
