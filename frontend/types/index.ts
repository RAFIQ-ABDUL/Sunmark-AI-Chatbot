export interface ModelResponse {
  model: string;
  answer: string;
  status: 'success' | 'error';
}

export interface ApiResponse {
  query: string;
  responses: {
    groq: ModelResponse;
    openrouter: ModelResponse;
  };
}