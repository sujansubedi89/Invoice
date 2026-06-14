"""
AI SERVICE - Google Gemini integration
Converts a free-text invoice description into structured data
matching Invoice / LineItem / PaymentDetails fields.
"""
import json
import requests
from django.conf import settings

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are an assistant that extracts structured invoice data
from a short free-text description written by a freelancer or small business.

Return ONLY valid JSON matching exactly this schema:

{
  "vendor_client": string,
  "vendor_email": string,
  "vendor_address": string,
  "service_title": string,
  "currency": one of ["NPR", "USD", "EUR", "GBP", "PKR", "INR"],
  "tax_rate": number,
  "due_date": "YYYY-MM-DD" or null,
  "notes": string,
  "line_items": [
    {
      "description": string,
      "unit_type": one of ["fixed", "hourly", "daily", "monthly"],
      "units": number,
      "unit_price": number
    }
  ],
  "payment_details": {
    "payment_type": "paypal" or "bank",
    "paypal_email": string,
    "bank_name": string,
    "account_holder": string,
    "account_number": string,
    "routing_number": string,
    "swift_code": string
  }
}

Rules:
- Use "" for any unknown string field, 0 for unknown numbers, null for unknown due_date.
- Never invent emails, account numbers, or addresses that weren't mentioned.
- tax_rate is a plain number, e.g. 13 for 13%. Default to 0 if not mentioned.
- Always return at least one line item.
- If currency isn't mentioned, infer from context (e.g. "rupees" + Nepal context -> NPR), else default "USD".
"""


class AIServiceError(Exception):
    pass


def generate_invoice_data(description: str) -> dict:
    if not settings.GROQ_API_KEY:
        raise AIServiceError("GROQ_API_KEY is not configured.")

  
    headers = {"Authorization": f"Bearer { settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
        
    }
    payload = {
        "model":settings.GROQ_MODEL,

        "messages":[
            {
                "role":"system",
                "content":SYSTEM_PROMPT,
            },
        {
         "role":"user",
         "content":description,
        },],
        "response_format":{
            "type":"json_object"
        }
        }
    try:
        resp=requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        if not resp.ok:
             raise AIServiceError(f"Grok returned {resp.status_code}: {resp.text[:300]}")
    except requests.RequestException as e:
            raise AIServiceError(f"Groq request failed: {e}")

    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise AIServiceError(f"Unexpected Gemini response: {data}")

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise AIServiceError(f"AI did not return valid JSON: {content[:300]}")