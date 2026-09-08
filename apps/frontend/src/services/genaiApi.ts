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
