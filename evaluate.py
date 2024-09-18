from openai import OpenAI

with open("API_KEY", "r") as f:
    API_KEY = f.read().strip()

client = OpenAI(api_key=API_KEY)

def grade_text(text, solution_text):
    try:
        prompt = (
            "Grade the following assignment based on provided solution guidelines:\n\n"
            f"Assignment Text:\n{text}\n\n"
            f"Solution Text:\n{solution_text}\n\n"
            "Has this student passed or failed the assignment?"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "You will be grading assignments in the university course \"Introduction to Algorithms\". The students need to do an honest effort in order to pass the assignment. Their answers do not necessarily need to be correct. I will give you their submissions and the suggested solution, and you will reply with \"passed\" or \"failed\". "
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": prompt
                    }
                ]
                }
            ],
            temperature=0.2,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "text"
            }
        )

        # print("Grading completed successfully.")
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in grading submission: {e}")
        return None
    
def grade_code(code, solution_code):
    try:
        prompt = (
            "Grade the following assignment based on provided solution guidelines:\n\n"
            f"Assignment Code:\n{code}\n\n"
            f"Solution Code:\n{solution_code}\n\n"
            "Has this student passed or failed the assignment?"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "You will be grading assignments in the university course \"Introduction to Algorithms\". The students need to do an honest effort in order to pass the assignment. Their answers do not necessarily need to be correct. I will give you their submissions and the suggested solution, and you will reply with \"passed\" or \"failed\". "
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": prompt
                    }
                ]
                }
            ],
            temperature=0.2,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "text"
            }
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in grading submission: {e}")
        return None