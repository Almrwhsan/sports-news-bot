import os
from google import genai


def main():
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=api_key)

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input="اكتب جملة عربية قصيرة جدًا عن كرة القدم."
    )

    print("===================================")
    print("          GEMINI TEST")
    print("===================================")
    print("Gemini response:")
    print(interaction.output_text)
    print("===================================")


if __name__ == "__main__":
    main()
