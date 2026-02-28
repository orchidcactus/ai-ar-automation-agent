import pandas as pd
import os
from dotenv import load_dotenv
from groq import Groq

# Load API key from .env
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -----------------------
# LLM CALL FUNCTION
# -----------------------
def ask_llm(prompt):

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()


# -----------------------
# STEP 1 — CLASSIFY SEVERITY
# -----------------------
def classify(invoice):

    prompt = f"""
You are assisting a corporate finance accounts receivable team.

Classify the overdue invoice severity.

Return EXACTLY:

Severity: <LOW/MEDIUM/HIGH>
Reason: <one short sentence>

Customer: {invoice['customer']}
Amount: {invoice['amount']}
Days overdue: {invoice['days_overdue']}
Days since last contact: {invoice['last_contact']}
Payment history: {invoice['payment_history']}
"""

    return ask_llm(prompt)


# -----------------------
# STEP 2 — DECIDE ACTION
# -----------------------
def decide_action(severity, days):

    prompt = f"""
Choose the best collections action.

Return EXACTLY:

Action: <action>
Reason: <short explanation>

Severity: {severity}
Days overdue: {days}

Options:
- Gentle reminder email
- Firm payment request
- Escalation notice
- Suggest payment plan
"""

    return ask_llm(prompt)


# -----------------------
# STEP 3 — GENERATE EMAIL
# -----------------------
def generate_email(invoice, action):

    prompt = f"""
Generate a professional corporate payment follow-up email.

Rules:
- polite
- concise
- professional
- no threats

Customer: {invoice['customer']}
Invoice amount: {invoice['amount']}
Days overdue: {invoice['days_overdue']}
Chosen action: {action}

Return ONLY the email text.
"""

    return ask_llm(prompt)


# -----------------------
# MAIN PIPELINE
# -----------------------
df = pd.read_csv("invoices.csv")

for _, row in df.iterrows():

    severity_output = classify(row)
    severity = severity_output.split("\n")[0].replace("Severity:", "").strip()

    action_output = decide_action(severity, row["days_overdue"])
    action = action_output.split("\n")[0].replace("Action:", "").strip()

    email = generate_email(row, action)

    print("\n========================")
    print("Customer:", row["customer"])
    print(severity_output)
    print(action_output)
    print("\nEMAIL:\n", email)
