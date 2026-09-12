# _______________________________________ISSUES______________________________________

## (1)First Issue

#### ```Race Condition```
#### -> Check the route in /apps/http-server/routes
 ```bash
 /api/v1/quizzes/:quizId/generate-access-code
 ```

*In this route, we have to tackle race-condition while generating unique-access code for joining quiz.
*If two user say A & B. If they request at the same time and accidently get the same code...

*Request - A
  ```bash
  generateCode → AC123A
  ```

*Request - B
  ```bash
  generateCode → AC123A
  ```

 -> SO this may give some concurrency  issues.

#### ***Final Command***
 -> See the route   and analyze the prisma queries and try to optimise the code to stop these concurrency issues


 ## (2)Second Issue (Functionality Add on)

  -> Backend route `/apps/http-server/routes/quiz.ts`

 #### -> Check the page in frontend `/apps/frontend/src/screens/QuizBuilder.tsx`
        *This is the page where we can create question
        *But in this page after creating Questions there is no option of deleting Questions.
        *Therefore, you have to implement the functionalty of deleting the created questions

#### ***Final Command***
 -> See and use the page and after understanding the codebase, Implementing this Feature in frontend and backend both.


 ## (3) Third Issue (Functionality Add on)

   -> Backend route `/apps/http-server/routes/quiz.ts`
  #### -> Check the page in frontend `/apps/frontend/src/screens/QuizBuilder.tsx`
        *This is the page where we can create question
        *But in this page after creating Questions there is no option of editing or updating Questions.
        *Therefore, you have to implement the functionalty of updating the created questions



 ## (4) Fourth Issue (GenAI - Functionality Add on)

   -> GenAI service `/apps/genAI/app/main.py`
  #### -> Check the component in frontend `/apps/frontend/src/components/AiQuizGenerator.tsx`
        *This is the panel where a host uploads a PDF and generates questions with AI
        *Right now if the AI writes one bad question, the host can only delete it
        *There is no way to say "regenerate just this one question"
        *Therefore, implement a re-generate option for a single question

#### ***Final Command***
 -> Add an endpoint that regenerates one question from the same PDF context,
    and wire a small re-roll button into the review list in the frontend


 ## (5) Fifth Issue (GenAI - Performance)

   -> RAG code `/apps/genAI/app/rag/rag_system.py`
        *Every request re-reads the PDF, re-chunks it and rebuilds the vector store
        *So asking two questions about the same PDF does all the work twice
        *The vector store is `InMemoryVectorStore`, so nothing survives a restart

#### ***Final Command***
 -> Cache the built vector store per PDF (hash the file contents as the key)
    so repeat requests on the same document skip the embedding step


 ## (6) Sixth Issue (Good First Issue - Frontend)

   -> Frontend `/apps/frontend/src`
        *`pnpm run lint` currently reports around 20 eslint errors
        *Mostly `@typescript-eslint/no-explicit-any` and unused variables
        *Because of this, the lint step in CI is set to report without blocking
        *Files affected: `Dashboard.tsx`, `JoinQuiz.tsx`, `LiveQuiz.tsx`,
          `Login.tsx`, `Signup.tsx`, `InviteAccept.tsx`, `QuizBuilder.tsx`

#### ***Final Command***
 -> Replace the `any` types with real types (the Prisma types from `@repo/db`
    are a good starting point) and remove unused variables. Once `pnpm run lint`
    passes, remove `continue-on-error: true` from the Lint step in
    `.github/workflows/ci.yml` so lint becomes a real merge gate
