import axios from 'axios';

const genaiHost =
    import.meta.env.VITE_GENAI_URL || 'http://localhost:8000';

// LLM calls (RAG, question generation) are slow, so this client uses a
// much longer timeout than the main api client.
export const genaiApi = axios.create({
    baseURL: genaiHost,
    timeout: 120000,
});

export interface ChatResponse {
    response: string;
}

export const chat = async (userQuery: string) => {
    const { data } = await genaiApi.post<ChatResponse>('/chat', {
        user_query: userQuery,
    });

    return data.response;
};

export interface GenerateQuestionsResponse {
    message: string;
    filename: string;
    questions: string;
}

export const generateQuestions = async (file: File, userQuery: string) => {
    const form = new FormData();
    form.append('file', file);
    form.append('user_query', userQuery);

    const { data } = await genaiApi.post<GenerateQuestionsResponse>(
        '/generate-questions',
        form
    );

    return data;
};

export interface AskPdfResponse {
    message: string;
    filename: string;
    question: string;
    answer: string;
}

export const askPdf = async (file: File, userQuery: string) => {
    const form = new FormData();
    form.append('file', file);
    form.append('user_query', userQuery);

    const { data } = await genaiApi.post<AskPdfResponse>('/ask-pdf', form);

    return data;
};

export interface GeneratedOption {
    text: string;
    isCorrect: boolean;
}

export interface GeneratedQuestion {
    text: string;
    difficulty: 'Low' | 'Medium' | 'High';
    options: GeneratedOption[];
}

export interface GenerateQuizResponse {
    message: string;
    filename: string;
    count: number;
    questions: GeneratedQuestion[];
}

// Structured counterpart to generateQuestions: returns data the quiz
// builder can render and save, rather than a formatted text blob.
export const generateQuiz = async (file: File, userQuery: string) => {
    const form = new FormData();
    form.append('file', file);
    form.append('user_query', userQuery);

    const { data } = await genaiApi.post<GenerateQuizResponse>(
        '/generate-quiz',
        form
    );

    return data.questions;
};

// Surfaces the FastAPI "detail" field, which carries the actionable
// message (missing API key, unusable PDF, and so on).
export const genaiErrorMessage = (err: unknown, fallback: string) => {
    if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;

        if (typeof detail === 'string') return detail;

        if (err.code === 'ECONNABORTED') {
            return 'The request timed out. Try asking for fewer questions.';
        }

        if (!err.response) {
            return 'Could not reach the AI service. Is it running on port 8000?';
        }
    }

    return fallback;
};
