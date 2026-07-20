import openai
import os
import streamlit as st

# Set up OpenRouter Client using the OpenAI SDK
api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

# Initialize the client pointing to OpenRouter's base URL
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    # OpenRouter recommends these headers for ranking, though they are optional
    default_headers={
        "HTTP-Referer": "https://your-streamlit-app-url.com", # Update with your actual URL
        "X-Title": "The Daily Ration",
    }
)

def get_ai_category(title, summary):
    """Uses OpenRouter's free tier to assign a single category to an article."""
    if not api_key:
        return "Uncategorized"
        
    try:
        response = client.chat.completions.create(
            model="openrouter/free", # Automatically routes to an available free model
            messages=[
                {
                    "role": "system", 
                    "content": "You are a news editor. Categorize the article into exactly ONE of these tags: Middle Eastern, Asia, Western, Uncategorised. Reply with ONLY the tag name and nothing else."
                },
                {
                    "role": "user", 
                    "content": f"Title: {title}\nSummary: {summary}"
                }
            ],
            max_tokens=10,
            temperature=0
        )
        # Clean up the output in case the free model includes extra spaces or punctuation
        category = response.choices[0].message.content.strip().replace(".", "")
        valid_categories = ["Middle Eastern", "Asia", "Western", "Uncategorised"]
        
        # Enforce strict categorization fallback if the free model disobeys instructions
        if category not in valid_categories:
            return "General"
            
        return category
        
    except Exception as e:
        # Silently fallback to Uncategorized if rate limits or errors occur
        return "Uncategorized"