/**
 * TOON Chat Type Definitions
 */

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  messages_toon: string;
  use_tools?: boolean;
  session_id?: string;
}

export interface ChatResponse {
  response_toon: string;
  history_toon: string;
  total_messages: number;
}

export interface HealthResponse {
  status: string;
  model: string;
  toon_version: string;
  api_key_configured: boolean;
  history_file_exists: boolean;
  storage_format: string;
  history_window_size: number;
  features: string[];
}
