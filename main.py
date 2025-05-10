from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import re

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)



# Load dataset
df = pd.read_csv("laptop.csv")

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preload known values
brands = df['brand'].dropna().unique().tolist()
processors = df['processor_name'].dropna().unique().tolist()
oses = df['Operating System'].dropna().unique().tolist()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "").strip().lower()

    # Greeting on empty or initial request
    if user_input in ["", "hi", "hello", "hey"]:
        return {
            "response": (
                "👋 Hello! Welcome to our HappyCore Systems.\n"
                "You can ask me anything like:\n"
                "- Suggest me a gaming laptop under ₹60000\n"
                "- I want a Dell laptop with Windows 11\n"
                "- Show me laptops with Ryzen 5 processor\n"
                "Go ahead, ask your question! 💬"
            )
        }
    
    if any(bye in user_input for bye in ["bye", "goodbye", "see you", "exit",'Thanks','Txn','THANK',]):
        return {
            "response": (
            "🙏 Thank you for visiting!\n"
            "I hope my recommendations help you choose the best laptop.\n"
            
            )
        }

    filtered_df = df.copy()

    # Filter by brand
    for brand in brands:
        if brand.lower() in user_input:
            filtered_df = filtered_df[filtered_df['brand'].str.lower() == brand.lower()]
            break

    # Filter by processor
    for proc in processors:
        if proc.lower() in user_input:
            filtered_df = filtered_df[filtered_df['processor_name'].str.lower().str.contains(proc.lower(), na=False)]
            break

    # Filter by OS
    for os in oses:
        if os.lower() in user_input:
            filtered_df = filtered_df[filtered_df['Operating System'].str.lower().str.contains(os.lower(), na=False)]
            break

    # Filter by price (e.g., under 60000)
    price_match = re.search(r"under\s*₹?\s*(\d+)", user_input)
    if price_match:
        price_limit = int(price_match.group(1))
        filtered_df = filtered_df[filtered_df['price'] <= price_limit]

    if filtered_df.empty:
        return {"response": "😕 Sorry, no laptops match your criteria. Please try different filters."}

    # Sort and take top 10
    filtered_df = filtered_df.sort_values(by="spec_score", ascending=False).head(10)

    # Format response
    response = "🔍 Here are the best matching laptops:\n"
    for i, (_, row) in enumerate(filtered_df.iterrows(), start=1):
        response += (
            f"{i}. {row['model_name']} ({row['brand']}) - ₹{row['price']}\n"
            f"   Processor: {row['processor_name']}, RAM: {row['ram(GB)']}GB, SSD: {row['ssd(GB)']}GB, "
            f"OS: {row['Operating System']}\n"
        )

    return {"response": response.strip()}
