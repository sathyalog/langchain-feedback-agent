# LangChain AI Feedback Agent & Guardrailed Workflow

An intelligent, autonomous feedback processing system built with **LangChain**, **OpenRouter**, **LangGraph**, and **Resend API**. The agent analyzes customer feedback, enforces PII privacy rules, condenses long-running context, and drafts automated response emails requiring Human-in-the-Loop (HITL) approval before dispatch.


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

So far what we build is autonomous agent with capabilities of sending emails based on sentiment.

Now we will introduce Human-In-The-Loop(HITL) where human will take the decision to approve or reject the sending email with positive/negative feedback.

for this we need HumanInTheLoopMiddleware to be added in create_agent and syntax would be like
```
middleware=[HumanInTheLoopMiddleware(
        interrupt_on = {
            "send_email": {
                "allowed_decisions": ["approve", "reject"],
            }
        }
    )]
```

## Summarization middleware
Automatically summarize conversation history when approaching token limits, preserving recent messages while compressing older context. Summarization is useful for the following:
1. Long-running conversations that exceed context windows.
2. Multi-turn dialogues with extensive history.
3. Applications where preserving full conversation context matters.
### 1. Context Optimization (`SummarizationMiddleware`)
To prevent reaching context window limits and reduce token costs during long conversations, the agent leverages `SummarizationMiddleware`. This middleware automatically intercepts message payloads and compresses older conversation threads into a summary.

* **`model=llm`**: Sets the LLM instance responsible for summarizing past conversation turns.
* **`trigger=("fraction", 0.6)`**: Dictates when summarization takes place. In this configuration, context compression triggers automatically when context length reaches **60% of the model's total context capacity**. *(Alternative configuration supported: `trigger=("tokens", 1000)`).*
* **`keep=("messages", 10)`**: Preserves the **10 most recent messages** verbatim in working memory, ensuring active conversational continuity while older history gets summarized.

### 2. State Management (`InMemorySaver`)
The agent uses LangGraph's `InMemorySaver` checkpointer to preserve conversation state and message threads locally during execution.

## PII detection
Detect and handle Personally Identifiable Information (PII) in conversations using configurable strategies. PII detection is useful for the following:

    Healthcare and financial applications with compliance requirements.
    Customer service agents that need to sanitize logs.
    Any application handling sensitive user data.

### PII Protection Strategies (`middleware=PIIMiddleware(...)`)

The agent dynamically intercepts user inputs before sending them to OpenRouter (`apply_to_input=True`), applying specific obfuscation strategies:

| Entity Type | Detection Mechanism | Protection Strategy (`strategy`) | Input Transformation Example |
| :--- | :--- | :--- | :--- |
| **Email** | Built-in email detector | **`redact`**: Fully removes or replaces the value with a placeholder tag. | `user@example.com` → `[REDACTED_EMAIL]` |
| **Credit Card** | Built-in credit card detector | **`mask`**: Obfuscates sensitive digits while preserving trailing/leading digits. | `4111 2222 3333 4444` → `4111 **** **** 4444` |
| **API Key** | Custom Regex pattern (`sk-[a-zA-Z0-9][20,]`) | **`redact`**: Completely sanitizes detected API keys matching standard formats. | `sk-abc123xyz9876543210123` → `[REDACTED_API_KEY]` |
