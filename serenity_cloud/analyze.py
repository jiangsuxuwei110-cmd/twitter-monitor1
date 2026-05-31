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
MAX_TOKENS = 8192
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

Analyze the tweets below. This is a professional investment research task — be thorough and specific.

For EACH stock mentioned:
- Identify which of the 12 principles apply (list ALL that apply, not just one)
- Determine stance (bullish/bearish/neutral) with conviction level (1-5 stars)
- Write 3-5 sentence DETAILED analysis including:
  * The specific supply chain position and competitive moat
  * What catalyst or event is driving the thesis
  * Specific price targets, valuation metrics, or timeline if mentioned
  * How this connects to other stocks or broader themes
  * Counter-arguments or risks Serenity acknowledges

For thesis changes:
- Explain what changed specifically and WHY (new data point, contract win, management comment, etc.)
- How this affects conviction level (upgraded/downgraded)
- Which stocks are impacted by this thesis change

For supply chain insights:
- Map the full BOM chain from end-customer → component → material → raw input
- Identify which node is the bottleneck and why
- Note any pricing power or monopoly dynamics

For key events:
- Provide full context: what happened, who's involved, timeline, market impact

For risk alerts:
- Be specific about the nature of risk (execution, geopolitical, dilution, competitive)
- Note Serenity's own hedging language or caveats

Output a structured JSON analysis with DETAILED, SPECIFIC content in every field.
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
  "summary": "3-4 sentence overview capturing today's major themes, market context, and the most important signal",
  "market_context": "1-2 sentence macro backdrop: sector rotation, key index moves, relevant macro events impacting AI/semiconductor space today",
  "stocks": [
    {{
      "ticker": "$SYMBOL",
      "stance": "bullish|bearish|neutral",
      "conviction": 4,
      "analysis": "3-5 sentence detailed analysis: supply chain position, catalyst, specific price targets/valuation if mentioned, connection to broader themes, acknowledged risks",
      "principles": ["Principle1", "Principle2"]
    }}
  ],
  "thesis_changes": [
    {{
      "title": "Short title",
      "description": "Detailed 3-4 sentence description: what changed, why, what specific new data triggered the change, how conviction is affected, which stocks are impacted",
      "principles": ["PrincipleName"]
    }}
  ],
  "key_events": [
    {{
      "title": "Event title",
      "description": "Detailed 3-4 sentence description: full context, who is involved, timeline, market impact, how Serenity interprets it",
      "principles": ["PrincipleName"]
    }}
  ],
  "supply_chain": [
    {{
      "title": "Supply chain insight",
      "description": "Detailed 3-5 sentence BOM mapping: full chain from end-customer → component → material, which node is the bottleneck, pricing power dynamics, monopoly considerations",
      "principles": ["PrincipleName"]
    }}
  ],
  "risk_alerts": [
    {{
      "title": "Risk title",
      "description": "2-3 sentence specific risk description: what type (execution/geopolitical/dilution/competitive), how serious, Serenity's own hedging language"
    }}
  ],
  "reference_tweets": [
    {{
      "time": "HH:MM Beijing time",
      "summary": "Tweet content summary in Chinese (50-150 characters)"
    }}
  ]
}}

For sections with no content, use empty arrays [].
Reference tweets: pick 3-5 most representative tweets with detailed summaries.
conviction: 1=speculative mention, 2=low conviction, 3=moderate, 4=high, 5=highest conviction with multi-data-source validation.
All analysis text should be in Chinese, professional tone, with specific numbers and details wherever possible.
"""
