import os
from groq import Groq
import pandas as pd
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Initialize Groq client with API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def groq_summarise_nutrition(prompt, df_food, df_drink, model="llama-3.3-70b-versatile", temperature=0.2, max_tokens=400):
    """
    Sends two dataframes as CSV plus a prompt to Groq LLM API and returns the generated summary.

    Parameters:
        prompt (str): Instruction or question for the LLM.
        df_food (pd.DataFrame): Food dataframe.
        df_drink (pd.DataFrame): Drink dataframe.
        model (str): Model identifier.
        temperature (float): Controls randomness (0-1).
        max_tokens (int): Max tokens to generate in response.

    Returns:
        str: LLM's generated summary content.
    """
    # Convert complete dataframes to CSV strings without indexes
    food_csv = df_food.to_csv(index=True)
    drink_csv = df_drink.to_csv(index=True)

    # Compose full prompt with both tables included
    full_prompt = (
        f"Analyse this nutrition data and please provide a concise nutritional insight summary based on this prompt\n\n"
        f"{prompt}\n\n"
        f"Food Data:\n{food_csv}\n\n"
        f"Drink Data:\n{drink_csv}\n\n"
        ""
    )

    # Log full prompt to console
    print("=== FULL PROMPT SENT TO GROQ LLM API ===")
    print(full_prompt)
    print("=== END PROMPT ===")

    # Call Groq chat completion API
    chat_completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": full_prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )

    # Return the content of the response
    return chat_completion.choices[0].message.content

# Example call:
if __name__ == "__main__":
    prompt_text = "Analyse this nutrition data, summarise key insights with focus on highest sugar and calorie items."
    import pandas as pd
    # Example mini data for demo purposes, replace with your loaded dataframes
    df_food_example = pd.DataFrame({
        "Name": ["Sample Food A", "Sample Food B"],
        "Calories": [250, 400],
        "Sugar": [15, 30]
    })
    df_drink_example = pd.DataFrame({
        "Name": ["Sample Drink A", "Sample Drink B"],
        "Calories": [100, 150],
        "Sugar": [20, 25]
    })

    print(groq_summarise_nutrition(prompt_text, df_food_example, df_drink_example))
