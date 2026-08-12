# AI Feedback Analyzer & Automated Email System

An intelligent feedback processing application built with **LangChain**, **OpenRouter**, and **Resend API**. The agent analyzes incoming training feedback, extracts structured data (sentiment, highlights, lowlights, rating, participant info), and automatically generates and sends tailored HTML emails (thank-you or apology) based on the feedback sentiment.

---

## Important Resend API Limitations (Free Tier)

When using the Resend API on the **Free Tier**, keep the following key restrictions in mind:

1. **Sender Address Constraints**: 
   * Emails sent on the free tier must use the default Resend testing domain: `onboarding@resend.dev` or `*@resend.dev` (e.g., `training@resend.dev`).
   * Custom domains (e.g., `you@yourcompany.com`) require domain verification in the Resend dashboard.
2. **Recipient Email Restrictions**: 
   * On unverified free accounts, you can **only send emails to the email address used to sign up for your Resend account**.
   * Sending to external addresses (e.g., `sathya.javascript@gmail.com`) will throw a `403 Forbidden` API error unless that address matches your registered account email, or you add a verified domain.
3. **Daily / Monthly Limits**: 
   * Free tier limits apply (typically 100 emails/day or 3,000 emails/month).

---

## Key Features & Code Architecture

### 1. Structured Output (`response_format`)
The agent utilizes Pydantic's `BaseModel` (`Feedback`) passed as `response_format` to guarantee that the LLM extracts structured metadata from raw text:
* `participant_name`: Name extracted from feedback.
* `sentiment`: Binary classification (`positive` or `negative`).
* `highlights` & `lowlights`: Parsed lists of pros and cons.
* `rating`: Integer score out of 5.
* `email_address`: Target contact email.

### 2. Autonomous Tool Invocation
The AI agent (`gpt-4o-mini` via OpenRouter) is equipped with the `@tool` decorator function `send_email`. Based on its system prompt, the model reads the feedback, evaluates the sentiment, generates a dynamic HTML response, and autonomously invokes `send_email()` with the generated body.

### 3. Human-in-the-Loop Import
The script imports `HumanInTheLoopMiddleware` from `langchain.agents.middleware`, indicating support for adding approval workflows before automated emails are sent out.

---

## Setup & Installation
.env file:
OPENROUTER_API_KEY=your_openrouter_api_key_here
RESEND_API_KEY=re_123456789_your_resend_key_here

how to run?
`uv run main.py`


### What Happens When Executed:
	1.	The script feeds the user feedback to the ChatOpenRouter model.
	2.	The model extracts structured information matching the Feedback Pydantic schema.
	3.	The system prompt evaluates the sentiment:
⚬	Positive Sentiment: Drafts a thank-you HTML email.
⚬	Negative Sentiment: Drafts an apology/action-item HTML email.
	4.	The agent automatically executes the send_email tool to deliver the email via Resend API.

