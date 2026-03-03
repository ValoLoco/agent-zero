# Perplexity Search Integration

## Overview

Agent Zero supports two search engines:
- **SearXNG** (default) - Self-hosted, privacy-focused metasearch
- **Perplexity** (optional) - AI-powered search with natural language responses

## Why Perplexity?

Perplexity provides:
- Natural language answers instead of raw search results
- Real-time web data with citations
- Superior reasoning for complex queries
- No self-hosting required

SearXNG remains default for:
- Privacy (self-hosted)
- No API costs
- Traditional search result format
- Offline capability

## Configuration

### 1. Get Perplexity API Key

Sign up at [perplexity.ai](https://www.perplexity.ai) and get your API key from settings.

### 2. Set Environment Variables

Add to your `.env` file:

```bash
# Choose search engine
SEARCH_ENGINE=perplexity

# Your Perplexity API key
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxx
```

### 3. Docker Configuration

Update `docker-compose.yml` environment section:

```yaml
environment:
  - SEARCH_ENGINE=perplexity
  - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
```

### 4. Restart Agent Zero

```bash
docker-compose down
docker-compose up -d
```

## Usage

Once configured, Agent Zero will automatically use Perplexity for all search queries.

```
User: "What are the latest developments in quantum computing?"

Agent Zero: *uses Perplexity to get comprehensive, up-to-date answer*
```

## Switching Between Search Engines

### Use Perplexity
```bash
SEARCH_ENGINE=perplexity
```

### Use SearXNG (default)
```bash
SEARCH_ENGINE=searxng
# or simply omit the variable
```

## Cost Considerations

Perplexity API pricing (as of 2026):
- **Sonar Small**: ~$0.20 per 1M tokens
- **Sonar Large**: ~$1.00 per 1M tokens
- **Free tier**: 5 searches per day

SearXNG is completely free (self-hosted).

## Model Selection

Default model: `llama-3.1-sonar-large-128k-online`

To customize, modify `python/helpers/perplexity_search.py`:

```python
def perplexity_search(
    query: str, 
    model_name="llama-3.1-sonar-small-128k-online",  # Change here
    api_key=None,
    base_url="https://api.perplexity.ai"
):
```

## Troubleshooting

### "Perplexity API key not found"

Check:
1. `.env` file has `PERPLEXITY_API_KEY=pplx-xxx`
2. Docker container restarted after `.env` change
3. Environment variable passed in docker-compose.yml

```bash
# Verify inside container
docker exec agent-zero-unified printenv | grep PERPLEXITY
```

### "Perplexity search failed"

Possible causes:
- Invalid API key
- Rate limit exceeded
- Network connectivity issue

Check logs:
```bash
docker exec agent-zero-unified tail -f /var/log/agent-zero.out.log
```

### Fallback to SearXNG

If Perplexity fails, temporarily switch:

```bash
# In .env
SEARCH_ENGINE=searxng

# Restart
docker-compose restart
```

## Carbon Fiber Principle

This implementation:
- ✓ Minimal code changes (single if/else in search_engine.py)
- ✓ Backward compatible (SearXNG remains default)
- ✓ No breaking changes to existing functionality
- ✓ Reuses existing perplexity_search.py helper
- ✓ Environment-driven configuration

## Performance Comparison

| Metric | SearXNG | Perplexity |
|--------|---------|------------|
| Response Time | ~2-5s | ~3-8s |
| Answer Quality | Raw results | Natural language |
| Privacy | High (self-hosted) | Lower (API) |
| Cost | Free | Paid (free tier available) |
| Offline | Yes | No |
| Setup | Complex | Simple |

## Example Output

### SearXNG Output
```
Search Engine Results:

Quantum Computing Breakthroughs 2026
https://example.com/quantum-news
Recent advances in quantum error correction...

IBM Announces 1000-Qubit Processor
https://ibm.com/news
IBM unveils new quantum processor...
```

### Perplexity Output
```
Perplexity Results:

Quantum computing has seen several major developments in 2026:

1. Error Correction: Researchers at Google achieved fault-tolerant
   quantum computation using surface codes with 99.9% fidelity.

2. Commercial Systems: IBM launched its 1000-qubit Condor processor,
   marking a milestone in scalable quantum hardware.

3. Applications: Financial institutions are now using quantum algorithms
   for portfolio optimization, showing 10x speedups over classical methods.

These advances bring practical quantum advantage closer to reality.
```

## Further Customization

For advanced users, you can modify search behavior in:
- `python/tools/search_engine.py` - Main search logic
- `python/helpers/perplexity_search.py` - Perplexity API calls
- `python/helpers/searxng.py` - SearXNG integration
