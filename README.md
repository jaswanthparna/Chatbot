🧠 AI Chatbot with Prebuilt & Custom Tool Integration

Tech Stack: Streamlit | LangGraph | Gemini API | LangSmith | SQLite

🚀 Overview

This project is an AI-powered conversational assistant built using Streamlit and LangGraph, featuring persistent memory, multi-threaded chat sessions, and tool-based intelligence.
It enables dynamic interactions by combining prebuilt tools (for web search and monitoring) and custom tools (for real-time data and computations).

✨ Features
🧩 Core Functionalities

Conversational AI: Powered by Gemini API and LangGraph for intelligent, context-aware responses.

Persistent Memory: Chats are stored in SQLite, allowing users to resume previous conversations seamlessly.

Multi-Threaded Chat Management: Supports multiple chat sessions, each maintaining its own conversation history.

Dynamic Chat Titles: Automatically generates chat titles based on user input.

Streaming Responses: Real-time answer generation for a more interactive experience.

🔧 Integrated Tools
🧰 Prebuilt Tools

DuckDuckGoSearchRun: For real-time web search and content summarization.

LangSmith: For LLM tracing, debugging, and performance monitoring of conversations.

⚙️ Custom Tools

Stock Price Retrieval Tool: Fetches real-time stock market data using APIs.

Arithmetic Calculator Tool: Performs basic arithmetic computations directly within chat.


⚙️ Installation & Setup

1️⃣ Clone the Repository

git clone https://github.com/yourusername/ai-chatbot-langgraph.git

cd ai-chatbot-langgraph

2️⃣ Install Dependencies

pip install -r requirements.txt

3️⃣ Run the Streamlit App

streamlit run app.py

![alt text](<Screenshot 2025-11-04 213301.png>) ![alt text](<Screenshot 2025-11-04 213823.png>) ![alt text](<Screenshot 2025-11-04 212545.png>) ![alt text](<Screenshot 2025-11-04 212646.png>) ![alt text](<Screenshot 2025-11-04 212951.png>)