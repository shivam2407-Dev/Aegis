import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def enhance_prompt_with_groq(initial_prompt):
    system_message = """
    You are an expert prompt engineer.
    Improve the given prompt to make it:
    - More clear
    - More structured
    - Context-rich
    - Specific about output format
    - Optimized for best LLM performance
    
    Only return the enhanced prompt.
    """

    completion = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": initial_prompt}
        ],
        temperature=0.5,
    )

    return completion.choices[0].message.content.strip()


def get_chatgpt_response(prompt):
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    return completion.choices[0].message.content.strip()


@app.route("/process", methods=["POST"])
def process_prompt():
    data = request.json
    initial_prompt = data.get("prompt")

    if not initial_prompt:
        return jsonify({"error": "Prompt is required"}), 400

    enhanced_prompt = enhance_prompt_with_groq(initial_prompt)

    response_initial = get_chatgpt_response(initial_prompt)
    response_enhanced = get_chatgpt_response(enhanced_prompt)

    return jsonify({
        "initial_prompt": initial_prompt,
        "enhanced_prompt": enhanced_prompt,
        "response_initial": response_initial,
        "response_enhanced": response_enhanced
    })


if __name__ == "__main__":
    app.run(debug=True)