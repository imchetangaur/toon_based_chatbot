'use client';

import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, ChatResponse } from '@/types/toon';
import { encodeToon, decodeToon, decodeToonResponse, formatContent } from '@/lib/toonParser';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState('default');
  const [isInitialized, setIsInitialized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load chat history on mount
  useEffect(() => {
    if (!isInitialized) {
      loadHistory();
      setIsInitialized(true);
    }
  }, [isInitialized]);

  const loadHistory = async () => {
    try {
      console.log('Loading chat history...');
      const response = await fetch(`${API_URL}/api/history/${sessionId}`);

      if (!response.ok) {
        console.warn('Failed to load history, starting fresh');
        return;
      }

      const data = await response.json();

      if (data.history_toon) {
        const history = decodeToon(data.history_toon);
        console.log(`Loaded ${history.length} messages from history`);
        setMessages(history);
      }
    } catch (err) {
      console.error('Error loading history:', err);
      // Don't show error to user, just start fresh
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
    };

    // Add user message to UI immediately
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      console.log('Sending message to backend...');

      // Encode current conversation to TOON
      const toonEncoded = encodeToon(updatedMessages);
      console.log('Encoded to TOON:', toonEncoded.substring(0, 100) + '...');

      // Send to backend
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages_toon: toonEncoded,
          use_tools: false,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      console.log('Received response from backend');

      // Decode TOON response
      const assistantResponse = decodeToonResponse(data.response_toon);

      if (assistantResponse && assistantResponse.content) {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: assistantResponse.content,
        };

        // Update with full history from backend (includes timestamps)
        if (data.history_toon) {
          const fullHistory = decodeToon(data.history_toon);
          if (fullHistory.length > 0) {
            console.log(`Updated history: ${fullHistory.length} messages`);
            setMessages(fullHistory);
          } else {
            setMessages([...updatedMessages, assistantMessage]);
          }
        } else {
          setMessages([...updatedMessages, assistantMessage]);
        }
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      console.error('Error sending message:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);

      // Remove the user message that failed
      setMessages(messages);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearHistory = async () => {
    if (!confirm('Are you sure you want to clear the chat history?')) return;

    try {
      const response = await fetch(`${API_URL}/api/history/${sessionId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to clear history');
      }

      setMessages([]);
      setError(null);
      console.log('History cleared successfully');
    } catch (err) {
      console.error('Error clearing history:', err);
      setError('Failed to clear history');
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-t-lg shadow-lg p-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
            TOON Chat
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Token-efficient AI chat • {messages.length} messages
          </p>
        </div>
        <button
          onClick={clearHistory}
          className="px-4 py-2 text-sm bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={messages.length === 0 || isLoading}
          aria-label="Clear chat history"
        >
          Clear History
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 bg-white dark:bg-gray-800 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-20">
            <h2 className="text-xl font-semibold mb-2">Welcome to TOON Chat!</h2>
            <p className="text-sm">
              This chat uses TOON format for 30-60% token reduction.
            </p>
            <p className="text-xs mt-2">Start a conversation below.</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={`msg-${idx}-${msg.role}`}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  msg.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-white'
                }`}
              >
                <div className="text-xs font-semibold mb-1 opacity-70">
                  {msg.role === 'user' ? 'You' : 'Assistant'}
                </div>
                <div className="whitespace-pre-wrap break-words">
                  {formatContent(msg.content)}
                </div>
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
              <div className="flex space-x-2" aria-label="Loading">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"
                  style={{ animationDelay: '0.2s' }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"
                  style={{ animationDelay: '0.4s' }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div
            className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded"
            role="alert"
          >
            <strong className="font-bold">Error: </strong>
            <span>{error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white dark:bg-gray-800 rounded-b-lg shadow-lg p-4">
        <div className="flex space-x-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
            className="flex-1 resize-none rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-white p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
            disabled={isLoading}
            aria-label="Message input"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors"
            aria-label="Send message"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
          Powered by TOON format • Connected to {API_URL}
        </div>
      </div>
    </div>
  );
}
