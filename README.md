# Multi-Agent Business Analysis with AutoGen + Gemini

A multi-agent pipeline built with **AutoGen (AG2)** and **Google Gemini**. Four specialised agents work in sequence on a business description and produce an analysis, a SWOT, growth strategies and a critique of those strategies.

## How it works

```
Business description
        │
        ▼
  AnalystBot      → key strengths and challenges
        │
        ▼
   SWOTBot        → detailed SWOT analysis
        │
        ▼
 StrategistBot    → 3 business growth strategies
        │
        ▼
   CriticBot      → critique and improvements
```

Each agent is a custom `GeminiAgent` (subclass of AutoGen's `ConversableAgent`). Its replies come from Gemini instead of OpenAI, and each agent's output is passed as input to the next one.

## Features

- Custom Gemini-powered AutoGen agents
- Sequential agent chaining with shared context
- Automatic retries with exponential backoff on 503 / 429 errors
- Fallback models, configurable from `.env`
- API key kept out of the code via `.env`

## Tech stack

- Python 3.10+
- [AG2 (AutoGen)](https://github.com/ag2ai/ag2)
- [google-genai](https://pypi.org/project/google-genai/)
- python-dotenv

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/sourabhbagda24/Multi_Agents-by-Autogen.git
   cd Multi_Agents-by-Autogen
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Mac / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Add your API key**

   Copy `.env.example` to `.env` and fill in your values:
   ```
   GEMINI_API_KEY=your_key_here
   GEMINI_MODEL=gemini-3.5-flash
   GEMINI_FALLBACKS=gemini-3.7-flash,gemini-3.5-flash-lite
   ```
   Get a free key from [Google AI Studio](https://aistudio.google.com/). Model names change over time. To see which models your key can use, run:
   ```bash
   python -c "from google import genai; import os; from dotenv import load_dotenv; load_dotenv(); c=genai.Client(api_key=os.getenv('GEMINI_API_KEY')); [print(m.name) for m in c.models.list()]"
   ```

## Usage

```bash
python main.py
```

To analyse your own business, edit the `business_description` string in `main.py`.

## Project structure

```
.
├── main.py            # agents + pipeline
├── requirements.txt   # dependencies
├── .env.example       # sample environment file
└── README.md
```

## Configuration

| Variable | Description | Default |
| --- | --- | --- |
| `GEMINI_API_KEY` | Your Gemini API key (required) | none |
| `GEMINI_MODEL` | Primary model to use | `gemini-3.8-flash` |
| `GEMINI_FALLBACKS` | Comma-separated backup models tried if the primary keeps failing | empty |

## Troubleshooting

- **`404 NOT_FOUND` for a model:** that model is not available to your key. Pick another from the model list command above.
- **`503 UNAVAILABLE`:** Google's servers are busy. The code retries automatically. Try a fallback model or run again after a few minutes.
- **`No module named 'autogen'`:** run `python -m pip install ag2` inside the active virtual environment.
- **Push to GitHub rejected:** make sure `.env` and `.venv/` are in `.gitignore`.

## Security

Never commit your `.env` file or API key. If a key was ever exposed, revoke it in Google AI Studio and create a new one.

## License

MIT
