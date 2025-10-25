from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3") 
def generate_student_summary(student):

    prompt = (
        f"Generate a short summary for this student:\n"
        f"Name: {student.name}\n"
        f"Age: {student.age}\n"
        f"Email: {student.email}\n\n"
        "The summary should be concise, grounded and written in third person.\n"
        "The summary should only use Name, Age and Email. No other non-citated stuff.\n"
        "Keep the summary fluent."
    )

    try:
        result = llm.invoke(prompt)
        return result.strip()
    except Exception as e:
        return f"Error generating summary: {e}"
