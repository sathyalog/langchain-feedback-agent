from langchain_openrouter import ChatOpenRouter
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv
from pydantic import Field, BaseModel
from typing import Literal
import os
import resend

load_dotenv()

llm = ChatOpenRouter(
    model="gpt-4o-mini"
)

class Feedback(BaseModel):
    participant_name: str = Field(description="Name of the participant")
    summary: str = Field(description="Brief summary of the overall feedback")
    sentiment: Literal['positive', 'negative'] = Field(description="Sentiment of the feedback like positive or negative")
    highlights: list[str]=Field(description="List of positive highlights of the program described by the participant")
    lowlights: list[str]=Field(description="List of negative highlights of the program described by the participant")
    rating: int = Field(description="Rating of the program")
    email_address: str = Field("Email address of the participant")

@tool
def send_email(email_address: str, body: str):
    """
    Tool for sending an email using resend API
    """
    resend.api_key=os.getenv("RESEND_API_KEY")
    params = resend.Emails.SendParams = {
        "from": "training@resend.dev",
        "to": [email_address],
        "subject": "Reply from Training Manager",
        "html": body
    }
    email = resend.Emails.send(params)
    return email
    

agent = create_agent(
    model=llm,
    system_prompt="You are an AI assistant who analyze the customer feedback and send an email to customer based on feedback sentiment. If sentiment is positive, you send a thank you email and if sentiment is negative you send an apology email. You use tool to send email. Use html format to draft an email.",
    response_format=Feedback,
    tools=[send_email],
)
#positive feedback content - The Java Fullstack training program completely exceeded my expectations. It comprehensively covered key technologies like Core Java, Spring Boot, Hibernate, and Angular with excellent pacing. The structure allowed for plenty of hands-on practice, particularly during the Spring Boot and Angular modules, which really solidified my understanding. Furthermore, the dedicated sessions on debugging and code optimization were incredibly valuable and greatly enhanced the program’s real-world effectiveness. The trainer was highly knowledgeable, and their well-planned delivery ensured meaningful learning and immediate practical application. Overall, the program offered a perfect balance of theory and practical focus. I would confidently rate it 5 out of 5.
# Feedback given by Sathya.Email address - sathya.javascript@gmail.com
result = agent.invoke(
    {
        "messages":[
            {
            "role": "user", 
            "content": "The Java Fullstack training program did not meet expectations. Although it covered key technologies like Core Java, Spring Boot, Hibernate, and Angular, several sections were rushed—especially Spring Boot and Angular—leaving little time for hands-on practice. The lack of dedicated sessions on debugging and code optimization further reduced the program’s effectiveness. While the trainer was knowledgeable, the pace and structure limited meaningful learning and real-world application. Overall, the program requires better pacing and more practical focus. I would rate it 2 out of 5. Feedback given by Sathya. Email address - sathya.javascript@gmail.com"
            }
        ]
    }
)