"""
Serenity Daily - AI Analyzer (Cloud Version)
Calls DeepSeek API (OpenAI-compatible) with Serenity's 12 principles
to analyze @aleabitoreddit's daily tweets.

Requires DEEPSEEK_API_KEY env var.
"""
import json
import os
import urllib.request

# --- Config ---
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"  # or "deepseek-reasoner" for deeper reasoning
MAX_TOKENS = 4096
TEMPERATURE = 0.3  # Low temp for structured analysis


# --- Serenity's 12 Core Principles (condensed for prompt) ---
SERENITY_METHODOLOGY = """
You are analyzing tweets from Serenity (@aleabitoreddit), an AI/semiconductor supply-chain analyst.
Apply his 12 core principles when analyzing:

1. **Bottleneck Hunting** — Find the narrowest point in AI supply chain where demand >> supply.
   Upstream (materials/substrates) > Midstream (lasers/modules) > Downstream (systems).

2. **Multi-hop BOM Mapping** — Trace bills of materials through multiple tiers.
   Hyperscaler capex → Equipment → Components → Raw materials → Specialty chemicals.

3. **Small-cap Asymmetry** — Smaller market cap + upstream positioning = higher alpha potential.
   The more obscure the bottleneck, the more undervalued.

4. **Institutional Lag** — Institutions discover supply chain bottlenecks 4-6 weeks after retail analysts.
   Media coverage is a leading indicator of institutional inflow.

5. **TAM Expansion** — Total addressable market for photonics/specialty semis grows with each new AI data center generation.
   Each node shrink / bandwidth jump creates new bottlenecks.

6. **Geopolitical Supply Chain** — CHIPS Act, export controls, rare earth dependencies.
   Non-China supply chains command premium valuation.

7. **Power & Cooling** — AI data centers face power constraints.
   Power infrastructure (grid, cooling, backup) is an underappreciated bottleneck.

8. **Counterparty / Funding Quality** — Who is funding the company? Strategic vs financial investors.
   Government/CHIPS Act backing = higher quality. PE/hedge fund short attacks = noise.

9. **Short Squeeze Dynamics** — Small-cap shorts create asymmetric upside.
   Look for high short interest + positive catalyst convergence.

10. **Earnings Qualification** — Revenue growth is the ultimate validator.
    "Qualification cycle" = design win → pilot → qualification → volume production → revenue.

11. **Media/Research Validation** — When mainstream media or sell-side research "discovers" what Serenity found months ago.
    This is a bullish signal - institutional money follows.

12. **Bayesian Updating** — Constantly update thesis with new evidence.
    Initial research (prior) → Position sizing → New data (likelihood) → Updated conviction (posterior).

---

Analyze the tweets below. For each tweet, identify:
- Which of the 12 principles it relates to
- Specific stock tickers mentioned and their stance (bullish/bearish/neutral)
- Supply chain connections or BOM insights
- Key events (earnings, contracts, media coverage, conferences)
- Any thesis changes or updates
- Risk warnings

Output a structured JSON analysis.
"""


def call_deepseek(prompt: str, api_key: str) -> dict:
    """Call DeepSeek chat API with given prompt. Returns parsed JSON response."""
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a semiconductor supply chain analyst. You output ONLY valid JSON, no markdown, no commentary outside the JSON structure."},
            {"role": "user", "content": prompt},
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")

    req = urllib.request.Request(DEEPSEEK_API_URL, data=payload, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    })

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    content = result["choices"][0]["message"]["content"]
    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
    return json.loads(content)


def build_analysis_prompt(tweets: list[dict]) -> str:
    """Build the analysis prompt with today's tweets and Serenity methodology."""
    tweets_json = []
    for t in tweets:
        tweets_json.append({
            "id": t["id"],
            "time_beijing": t["time_beijing"],
            "text": t["text"],
            "has_images": len(t.get("images", [])) > 0,
        })

    return f"""{SERENITY_METHODOLOGY}

=== TODAY'S TWEETS (Beijing Time) ===
{json.dumps(tweets_json, ensure_ascii=False, indent=2)}

=== OUTPUT FORMAT ===
Return EXACTLY this JSON structure (no extra fields, no markdown):

{{
  "summary": "1-2 sentence overview of today's major themes",
  "stocks": [
    {{
      "ticker": "$SYMBOL",
      "stance": "bullish|bearish|neutral",
      "analysis": "1-2 sentence analysis applying which principle(s)",
      "principles": ["PrincipleName"]
    }}
  ],
  "thesis_changes": [
    {{
      "title": "Short title",
      "description": "Detailed description of thesis change or update",
      "principles": ["PrincipleName"]
    }}
  ],
  "key_events": [
    {{
      "title": "Event title",
      "description": "Detailed description",
      "principles": ["PrincipleName"]
    }}
  ],
  "supply_chain": [
    {{
      "title": "Supply chain insight",
      "description": "Detailed BOM mapping or supply chain connection",
      "principles": ["PrincipleName"]
    }}
  ],
  "risk_alerts": [
    {{
      "title": "Risk title",
      "description": "Risk description with Serenity framework context"
    }}
  ],
  "reference_tweets": [
    {{
      "time": "HH:MM Beijing time",
      "summary": "Tweet summary (under 100 Chinese characters)"
    }}
  ]
}}

For sections with no content, use empty arrays [].
Reference tweets: pick 3-5 most representative tweets.
All analysis text should be in Chinese.
"""
