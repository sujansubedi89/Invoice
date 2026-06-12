"""
AI SERVICE - Google Gemini integration
Converts a free-text invoice description into structured data
matching Invoice / LineItem / PaymentDetails fields.
"""
import json
import requests
from django.conf import settings

GEMINI_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

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
    if not settings.GEMINI_API_KEY:
        raise AIServiceError("GEMINI_API_KEY is not configured.")

    url = GEMINI_URL_TEMPLATE.format(model=settings.GEMINI_MODEL)
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": settings.GEMINI_API_KEY,
    }
    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": description}]}
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if not resp.ok:
            raise AIServiceError(f"Gemini returned {resp.status_code}: {resp.text[:300]}")
    except requests.RequestException as e:
        raise AIServiceError(f"Gemini request failed: {e}")

    data = resp.json()
    try:
        content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise AIServiceError(f"Unexpected Gemini response: {data}")

    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise AIServiceError(f"AI did not return valid JSON: {content[:300]}")