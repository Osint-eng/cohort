# Cohort AI Agent (Hugging Face)

Structured task extraction and board agent via **Hugging Face Inference API**.

## Setup

1. Create a token: https://huggingface.co/settings/tokens  
2. Set it **locally only** (never commit):

```bash
export HF_TOKEN=hf_your_new_token_here
```

Or `.env` in repo root (gitignored):

```
HF_TOKEN=hf_your_new_token_here
```

3. Install:

```bash
pip install huggingface_hub pydantic python-dotenv
```

4. Run:

```bash
python examples/run_extraction.py
python examples/run_agent.py
```

Optional:

```bash
export COHORT_HF_MODEL=Qwen/Qwen2.5-7B-Instruct
```

## Security

If a token was pasted in chat or a public place, **revoke it** and create a new one.
Never commit tokens to GitHub.
