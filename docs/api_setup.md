# API Setup Guide

## Overview

Jarvis AI requires an API key from one of the supported LLM providers. Choose ONE provider and configure it.

## Supported Providers

### 1. Groq (Recommended - FREE & FAST) ⚡

**Why Groq?**
- Completely FREE
- Lightning fast responses
- Excellent quality
- Easy to set up

**Setup:**
1. Visit https://console.groq.com/
2. Sign up for a free account
3. Go to API Keys section
4. Create a new API key
5. Copy the key

**Models Available:**
- `llama-3.3-70b-versatile` (Recommended)
- `llama-3.1-70b-versatile`
- `mixtral-8x7b-32768`

---

### 2. OpenAI (Premium Quality)

**Why OpenAI?**
- Industry-leading quality
- GPT-4 Vision support
- Most capable for complex tasks

**Setup:**
1. Visit https://platform.openai.com/
2. Create account
3. Add payment method (Pay-as-you-go)
4. Go to API Keys
5. Create new secret key
6. Copy the key

**Models Available:**
- `gpt-4o` (GPT-4 Optimized)
- `gpt-4-turbo`
- `gpt-3.5-turbo` (Cheaper)

**Cost:** ~$0.01-0.03 per conversation

---

### 3. Mistral AI

**Why Mistral?**
- European alternative
- Good quality
- Competitive pricing

**Setup:**
1. Visit https://console.mistral.ai/
2. Create account
3. Go to API Keys
4. Create new key
5. Copy the key

**Models Available:**
- `mistral-large-latest`
- `mistral-medium-latest`

---

## Configuration

### Step 1: Edit `.env` file

```env
# Choose ONE provider and add its API key:

# Groq (Recommended - FREE)
GROQ_API_KEY=your_groq_key_here

# OR OpenAI
# OPENAI_API_KEY=your_openai_key_here

# OR Mistral
# MISTRAL_API_KEY=your_mistral_key_here
```

### Step 2: Edit `config.py`

Update line 13 to match your chosen provider:

```python
LLM_PROVIDER = "groq"  # or "openai" or "mistral"
```

### Step 3: Verify

Run the setup check:

```bash
python installer/doctor.py
```

You should see: ✅ API key configured

## Troubleshooting

### "No API key found"
- Check `.env` file exists in project root
- Verify the key name matches (GROQ_API_KEY, OPENAI_API_KEY, MISTRAL_API_KEY)
- No quotes around the key in `.env`

### "Invalid API key"
- Regenerate the API key from provider dashboard
- Copy the key correctly (no extra spaces)

### "Rate limit exceeded"
- Groq: Free tier has limits, wait a minute
- OpenAI: Add payment method or reduce usage
- Mistral: Check your billing

## Best Practices

1. **Never commit your `.env` file** to version control
2. **Rotate API keys** periodically for security
3. **Monitor your usage** on provider dashboards
4. **Use Groq for development** (it's free!)
5. **Use OpenAI for production** if you need maximum quality

## Provider Comparison

| Feature | Groq | OpenAI | Mistral |
|---------|------|--------|---------|
| Cost | FREE | $$$ | $$ |
| Speed | ⚡⚡⚡ | ⚡⚡ | ⚡⚡ |
| Quality | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Vision | ❌ | ✅ | ❌ |
| Setup | Easy | Medium | Easy |
