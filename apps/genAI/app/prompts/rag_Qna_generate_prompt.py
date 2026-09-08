QUESTION_GENERATION_PROMPT = """
You are an expert exam question generator.

The user wants to generate questions from the provided PDF.

First, understand the user's request and identify how many questions the user wants.

USER QUERY:
{user_query}

PDF CONTEXT:
{context}

Requirements:

- Generate exactly the number of questions requested by the user.
- If the user asks for 3 questions, generate exactly 3.
- If the user asks for 5 questions, generate exactly 5.
- If the user asks for 10 questions, generate exactly 10.
- If the user asks for 20 questions, generate exactly 20.
- Extract the requested question count from the USER QUERY.
- Do not assume a fixed number such as 10 or 30.
- If the user does not specify a number, generate 10 questions by default.

Difficulty:

The generated questions must be a mixture of:
- Low-level questions
- Medium-level questions
- High-level questions

Do not make all questions from the same difficulty level.

Question requirements:

- Every question must be based ONLY on the provided PDF context.
- Do not use outside knowledge.
- Cover different concepts and topics from the PDF.
- Do not generate duplicate or very similar questions.
- Questions should test understanding, concepts, application, and reasoning.
- Each question must have exactly 4 options.
- Every question must have exactly ONE correct answer.
- The other three options must be incorrect but plausible.
- Avoid ambiguous questions where multiple options could be correct.
- Randomize the position of the correct answer between A, B, C, and D.
- Do not always place the correct answer at the same position.

Return ONLY in this format:

QUESTIONS:

1. Question?
   A. Option
   B. Option
   C. Option
   D. Option
   Answer: B
   Difficulty: Medium

2. Question?
   A. Option
   B. Option
   C. Option
   D. Option
   Answer: D
   Difficulty: Low

Continue until exactly the requested number of questions has been generated.
"""