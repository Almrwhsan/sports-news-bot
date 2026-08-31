import os
from google import genai


def main():
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="اكتب جملة عربية قصيرة جدًا عن كرة القدم."
    )

    print("===================================")
    print("       GEMINI TEST")
    print("===================================")
    print("Gemini response:")
    print(response.text)
    print("===================================")


if __name__ == "__main__":
    main()
