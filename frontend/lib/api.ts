import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

export interface Source {
  text: string;
  metadata: {
    type?: string;
    chunk_type?: string;
    priority?: number;
    language?: string;
    created_at?: string;
    // Company info
    company_name?: string;
    // Project info
    project_title?: string;
    project_slug?: string;
    project_id?: string;
    // Interior style
    interior_name?: string;
    interior_slug?: string;
    // Architecture type
    architecture_type_name?: string;
    architecture_type_slug?: string;
    // News
    news_title?: string;
    news_slug?: string;
    news_id?: string;
    // Categories
    project_category_name?: string;
    news_category_name?: string;
    // Hero slide
    hero_slide_title?: string;
    // Image URLs
    image_url?: string;
    thumbnail_url?: string;
    [key: string]: any;
  };
  score: number;
}

export interface ChatRequest {
  query: string;
  session_id?: string;
}

export interface ChatResponse {
  answer: string;
  sources?: any[];
  session_id: string;
}

export const chatService = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await axios.post<ChatResponse>(
        `${API_URL}/api/chat`,
        request,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  async healthCheck(): Promise<boolean> {
    try {
      const response = await axios.get(`${API_URL}/health`);
      return response.status === 200;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  },
};
