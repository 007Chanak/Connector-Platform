from groq import Groq
import os

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_testing(number,cont):

    prompt = f"""
 You are LinkedIn Post Writter. 
 You have to make these many posts {number},
 The content of the posts are these {cont},
 You need to be creative with the writings but the facts or details need to be facts.

 IMPORTANT:
 -The facts need to be true, not invented.
 -The writing style can be creative.
 -When creating each posts give the title and then the content.

 CRITICAL:
 -Maximum post you can generate is close to 10.

"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content

    content = content.replace(
        "```",
        ""
    )

    contents=content.strip()

    print("Output:")
    print(contents)

    return contents