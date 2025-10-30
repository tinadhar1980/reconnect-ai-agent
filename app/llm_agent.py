import os
import json
from dotenv import load_dotenv
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

def build_prompt(profile):
    prompt = f"""You are the 'Reconnect AI' marketing agent. Use these rules:
1) High-value guests (lifetime_spend > 1000 and average_sentiment > 0.8) => 15_percent_off
2) Loyal guests (stays_count > 3 and average_sentiment > 0.6) => free_breakfast
3) Other positive-sentiment guests (average_sentiment >= 0.5) => welcome_back
4) Negative sentiment guests (average_sentiment < 0.5) => no_offer and flag for manual_review

Return EXACTLY one JSON object and nothing else with one of:
- { "action": "send_offer", "offer_type": "15_percent_off" }
- { "action": "send_offer", "offer_type": "free_breakfast" }
- { "action": "send_offer", "offer_type": "welcome_back" }
- { "action": "flag_for_review", "offer_type": null }

Guest profile:
{json.dumps(profile)}
"""
    return prompt

def deterministic_agent(profile):
    spend = profile.get("total_lifetime_spend", 0)
    sentiment = profile.get("average_sentiment", 0)
    stays = profile.get("stays_count", 0)
    if sentiment < 0.5:
        return {"action": "flag_for_review", "offer_type": None}
    if spend > 1000 and sentiment > 0.8:
        return {"action": "send_offer", "offer_type": "15_percent_off"}
    if stays > 3 and sentiment > 0.6:
        return {"action": "send_offer", "offer_type": "free_breakfast"}
    return {"action": "send_offer", "offer_type": "welcome_back"}

def decide_offer(profile):
    if OPENAI_KEY:
        try:
            import openai
            openai.api_key = OPENAI_KEY
            prompt = build_prompt(profile)
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content":"You are a JSON-only responder."},
                          {"role":"user","content":prompt}],
                max_tokens=200,
                temperature=0.0
            )
            text = resp.choices[0].message.content.strip()
            return json.loads(text)
        except Exception as e:
            print("OpenAI failed or returned non-JSON, falling back:", e)
    return deterministic_agent(profile)
