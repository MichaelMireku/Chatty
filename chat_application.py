import openai
from textblob import TextBlob
from datetime import datetime
from requests import get
import tkinter as tk
from tkinter import scrolledtext, messagebox


class ChatApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Chatty")
        self.geometry("600x400")

        self.create_widgets()

        self.openai_api_key = self.get_openai_api_key()
        openai.api_key = self.openai_api_key

        self.user_profile = ""
        self.context = ""

    def create_widgets(self):
        self.chat_history = scrolledtext.ScrolledText(self, width=60, height=15, wrap=tk.WORD)
        self.chat_history.pack(pady=10)

        self.user_input = tk.Entry(self, width=50)
        self.user_input.pack(pady=10)

        send_button = tk.Button(self, text="Send", command=self.process_user_input)
        send_button.pack()

    def get_openai_api_key(self):
        api_key = tk.simpledialog.askstring("OpenAI API Key", "Enter your OpenAI API key:")
        return api_key

    def analyze_sentiment(self, text):
        analysis = TextBlob(text)
        return analysis.sentiment.polarity

    def get_knowledge_base_answer(self, query):
        search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key=AIzaSyCTY9aWr7gSmk3GXnWQskhsxMhD8ackfNc&cx=80a3ef2a621f245fb"
        response = get(search_url)

        if response.status_code == 200:
            results = response.json().get("items", [])
            return results[0]["snippet"] if results else "No relevant information found."

        return "Error retrieving knowledge base information."

    def generate_response(self, user_prompt, engine="text-davinci-003"):
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=f"{self.user_profile}\n{self.context}\n{user_prompt}",
                max_tokens=150
            )
            return response.choices[0].text.strip()
        except Exception as e:
            return f"Error generating response: {e}"

    def save_conversation(self, user_prompt, ai_response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conversation_entry = f"\n[{timestamp}]\nUser: {user_prompt}\nAI: {ai_response}\n"
        self.chat_history.insert(tk.END, conversation_entry)

    def process_user_input(self):
        user_prompt = self.user_input.get()

        if user_prompt.lower() == 'exit':
            self.destroy()
            return

        sentiment = self.analyze_sentiment(user_prompt)
        sentiment_text = f"Sentiment: {'Positive' if sentiment > 0 else 'Negative' if sentiment < 0 else 'Neutral'}"
        self.chat_history.insert(tk.END, sentiment_text + "\n")

        suggestion_text = "Suggestion: "
        if tk.messagebox.askyesno("Suggestion", "Do you want a suggestion for your next action?"):
            query = f"What should I do next after '{user_prompt}'?"
            suggestion = self.get_knowledge_base_answer(query)
            suggestion_text += suggestion
        else:
            suggestion_text += "None"
        self.chat_history.insert(tk.END, suggestion_text + "\n")

        preferred_engine = "text-davinci-003"  # Default engine
        engine_text = tk.simpledialog.askstring("Engine Selection", "Choose AI engine (default: text-davinci-003):")
        if engine_text:
            preferred_engine = engine_text.lower()

        ai_response = self.generate_response(user_prompt, preferred_engine)
        self.chat_history.insert(tk.END, "AI: " + ai_response + "\n")

        self.save_conversation(user_prompt, ai_response)

        feedback = tk.simpledialog.askstring("Feedback",
                                             "How was the AI's response? (Positive/Negative/Neutral):").lower()
        tk.messagebox.showinfo("Feedback", "Thank you for your feedback!")

        self.context += f"\nUser: {user_prompt}\nAI: {ai_response}"  # Update conversation context


if __name__ == "__main__":
    app = ChatApplication()
    app.mainloop()
