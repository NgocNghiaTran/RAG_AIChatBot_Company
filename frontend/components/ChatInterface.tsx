'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Image as ImageIcon, Sun, Moon, Menu, X, ChevronRight, Clock, ExternalLink } from 'lucide-react';
import { chatService, ChatMessage, Source } from '@/lib/api';

const SUGGESTED_QUESTIONS = [
  "Công ty Nguyễn Minh Khang hoạt động trong lĩnh vực gì?",
  "Có dự án nào tại Bình Dương không?",
  "Mời giới thiệu phong cách Japandi trong dự án của NMK",
  "Tin tức mới nhất về các dự án hoàn thành là gì?",
  "Có căn hộ mẫu phong cách Luxury nào không?",
  "Ai là đơn vị thiết kế dự án Phúc Đạt?"
];

function ClientTime() {
  const [time, setTime] = useState<string>('--:--');

  useEffect(() => {
    const update = () => {
      setTime(
        new Intl.DateTimeFormat('vi-VN', {
          hour: '2-digit',
          minute: '2-digit'
        }).format(new Date())
      );
    };
    update();
    const id = setInterval(update, 30_000);
    return () => clearInterval(id);
  }, []);

  return (
    <span className="tabular-nums">{time}</span>
  );
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleDarkMode = () => {
    setDarkMode(prev => {
      const next = !prev;
      if (next) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      return next;
    });
  };

  const toggleSource = (index: number) => {
    setExpandedSources(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage({
        query: input,
        session_id: sessionId || undefined,
      });

      if (response.session_id) {
        setSessionId(response.session_id);
      }

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (question: string) => {
    setInput(question);
  };

  // Get image URL from metadata
  const getImageUrl = (metadata: Record<string, any>): string | null => {
    return (
      metadata.image_url ||
      metadata.thumbnail_url ||
      metadata.interior_image_url ||
      metadata.architecture_type_image_url ||
      metadata.project_image_url ||
      metadata.news_image_url ||
      metadata.hero_slide_image_url ||
      null
    );
  };

  // Get title from metadata
  const getTitle = (metadata: Record<string, any>): string => {
    return (
      metadata.interior_name ||
      metadata.architecture_type_name ||
      metadata.project_title ||
      metadata.news_title ||
      metadata.hero_slide_title ||
      metadata.company_name ||
      'Hình ảnh'
    );
  };

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('vi-VN', {
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <div suppressHydrationWarning className={`flex h-screen ${darkMode ? 'dark' : ''}`}>
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 fixed md:static inset-y-0 left-0 z-50 w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transition-transform duration-300 ease-in-out flex flex-col`}>
        {/* Sidebar Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">BoluTran Chatbot</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Trợ lý thông minh</p>
            </div>
          </div>
        </div>

        {/* Suggested Questions */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
            Câu hỏi gợi ý
          </h3>
          <div className="space-y-2">
            {SUGGESTED_QUESTIONS.map((question, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(question)}
                className="w-full text-left p-3 rounded-xl bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group"
              >
                <div className="flex items-start gap-2">
                  <ChevronRight className="w-4 h-4 text-gray-400 mt-0.5 group-hover:text-blue-600 transition-colors" />
                  <span className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{question}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            © 2024 NMK Design
          </p>
        </div>
      </div>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 px-4 md:px-6 py-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <Menu className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </button>
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Trò chuyện</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {messages.length === 0 ? 'Bắt đầu trò chuyện' : `${messages.length} tin nhắn`}
                </p>
              </div>
            </div>
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {darkMode ? (
                <Sun className="w-5 h-5 text-yellow-500" />
              ) : (
                <Moon className="w-5 h-5 text-gray-600" />
              )}
            </button>
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
          <div className="max-w-4xl mx-auto px-4 py-6">
            {messages.length === 0 ? (
              /* Empty State */
              <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center mb-6 shadow-lg">
                  <Bot className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                  Xin chào! Tôi có thể giúp gì?
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md">
                  Tôi là trợ lý AI của NMK Design. Hãy hỏi tôi về dự án, kiến trúc, nội thất hoặc tin tức.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full">
                  {SUGGESTED_QUESTIONS.slice(0, 4).map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(question)}
                      className="p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-md transition-all text-left group"
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                          <ExternalLink className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        </div>
                        <span className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                          {question}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              /* Messages */
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <div key={index} className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    {message.role === 'assistant' && (
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-md">
                          <Bot className="w-6 h-6 text-white" />
                        </div>
                      </div>
                    )}
                    
                    <div className={`max-w-[80%] ${message.role === 'user' ? 'order-1' : ''}`}>
                      <div className={`rounded-2xl px-5 py-3 ${
                        message.role === 'user'
                          ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-tr-sm'
                          : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 shadow-sm border border-gray-100 dark:border-gray-700 rounded-tl-sm'
                      }`}>
                        <p className="whitespace-pre-wrap leading-relaxed text-[15px]">{message.content}</p>
                      </div>
                      
                      {/* Timestamp */}
                      <div className={`flex items-center gap-1 mt-1 text-xs text-gray-400 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <Clock className="w-3 h-3" />
                        <ClientTime />
                      </div>

                      {/* Display images from sources */}
                      {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                        <div className="mt-3 space-y-3">
                          {message.sources
                            .filter(source => {
                              const metadata = source.metadata || {};
                              return getImageUrl(metadata) !== null;
                            })
                            .slice(0, 3)
                            .map((source, idx) => {
                              const metadata = source.metadata || {};
                              const imageUrl = getImageUrl(metadata);
                              const title = getTitle(metadata);
                              const isExpanded = expandedSources.has(idx);

                              if (!imageUrl) return null;

                              return (
                                <div key={idx} className="rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                                  <img
                                    src={imageUrl}
                                    alt={title}
                                    className="w-full h-48 object-cover"
                                    loading="lazy"
                                    onError={(e) => {
                                      const target = e.target as HTMLImageElement;
                                      target.style.display = 'none';
                                    }}
                                  />
                                  <div className="p-3 flex items-center justify-between">
                                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                                      <ImageIcon className="w-4 h-4" />
                                      <span className="truncate">{title}</span>
                                    </div>
                                    <button
                                      onClick={() => toggleSource(idx)}
                                      className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm font-medium"
                                    >
                                      {isExpanded ? 'Ẩn chi tiết' : 'Xem chi tiết'}
                                    </button>
                                  </div>
                                  {isExpanded && (
                                    <div className="px-3 pb-3 text-sm text-gray-600 dark:text-gray-400 border-t border-gray-100 dark:border-gray-700 pt-2">
                                      <p className="line-clamp-3">{source.text}</p>
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                        </div>
                      )}
                    </div>

                    {message.role === 'user' && (
                      <div className="flex-shrink-0 order-2">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center shadow-md">
                          <User className="w-6 h-6 text-white" />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                
                {/* Loading Indicator */}
                {isLoading && (
                  <div className="flex gap-4 justify-start">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-md">
                        <Bot className="w-6 h-6 text-white" />
                      </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm border border-gray-100 dark:border-gray-700">
                      <div className="flex gap-1.5">
                        <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-t border-gray-200 dark:border-gray-700 px-4 md:px-6 py-4">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
            <div className="flex gap-3 items-end">
              <div className="flex-1 relative">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Nhập câu hỏi của bạn..."
                  rows={1}
                  className="w-full px-5 py-3.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 transition-all"
                  disabled={isLoading}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit(e);
                    }
                  }}
                />
              </div>
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="px-6 py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:from-blue-700 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center gap-2 font-medium"
              >
                <Send className="w-5 h-5" />
                <span className="hidden sm:inline">Gửi</span>
              </button>
            </div>
            <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-2">
              Nhấn Enter để gửi, Shift+Enter để xuống dòng
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
