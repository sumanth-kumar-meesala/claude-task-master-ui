import React, { useState, useEffect, useRef } from 'react';

interface StreamMessage {
  type: string;
  agent?: string;
  message?: string;
  step?: number;
  total_steps?: number;
  status?: string;
  result?: string;
  error?: string;
  timestamp: string;
  requires_input?: boolean;
  input_prompt?: string;
}

interface AnalysisStreamProps {
  projectId: string;
  isOpen: boolean;
  onClose: () => void;
}

export const AnalysisStream: React.FC<AnalysisStreamProps> = ({ projectId, isOpen, onClose }) => {
  const [messages, setMessages] = useState<StreamMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [waitingForInput, setWaitingForInput] = useState(false);
  const [inputPrompt, setInputPrompt] = useState('');
  const eventSourceRef = useRef<EventSource | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!isOpen || !projectId) return;

    // Connect to the stream
    const eventSource = new EventSource(`/api/v1/projects/${projectId}/analysis/stream`);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      console.log('Connected to analysis stream');
    };

    eventSource.onmessage = (event) => {
      try {
        const data: StreamMessage = JSON.parse(event.data);
        setMessages(prev => [...prev, data]);

        // Handle user input requests
        if (data.requires_input) {
          setWaitingForInput(true);
          setInputPrompt(data.input_prompt || 'Please provide additional information:');
        }

        if (data.type === 'complete' || data.type === 'error') {
          setIsComplete(true);
          setWaitingForInput(false);
          eventSource.close();
          setIsConnected(false);
        }
      } catch (error) {
        console.error('Error parsing stream message:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('Stream error:', error);
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        setIsConnected(false);
      }
    };
  }, [isOpen, projectId]);

  const handleClose = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      setIsConnected(false);
    }
    setMessages([]);
    setIsComplete(false);
    setWaitingForInput(false);
    setUserInput('');
    setInputPrompt('');
    onClose();
  };

  const handleUserInputSubmit = async () => {
    if (!userInput.trim()) return;

    // Add user message to the stream
    const userMessage: StreamMessage = {
      type: 'user_input',
      agent: 'User',
      message: userInput,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);

    // TODO: Send user input to backend
    // For now, just simulate continuing the analysis
    setWaitingForInput(false);
    setUserInput('');
    setInputPrompt('');

    // Add a system message acknowledging the input
    const ackMessage: StreamMessage = {
      type: 'agent_communication',
      agent: 'System',
      message: 'Thank you for your input. Continuing analysis...',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, ackMessage]);
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'agent_communication':
        return '🤖';
      case 'status':
        return '📊';
      case 'result':
        return '✅';
      case 'error':
        return '❌';
      case 'complete':
        return '🎉';
      default:
        return 'ℹ️';
    }
  };

  const getAgentColor = (agent?: string) => {
    const colors: { [key: string]: string } = {
      'Solution Architect': 'text-blue-600',
      'Project Manager': 'text-green-600',
      'Technical Analyst': 'text-purple-600',
      'System': 'text-gray-600'
    };
    return colors[agent || 'System'] || 'text-gray-600';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl h-3/4 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-2">
            <h2 className="text-xl font-semibold">Project Analysis Stream</h2>
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-500">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 text-xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p>Connecting to analysis stream...</p>
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <span className="text-2xl">{getMessageIcon(message.type)}</span>
              <div className="flex-1">
                {message.agent && (
                  <div className={`font-semibold ${getAgentColor(message.agent)} mb-1`}>
                    {message.agent}
                    {message.step && message.total_steps && (
                      <span className="text-sm text-gray-500 ml-2">
                        (Step {message.step}/{message.total_steps})
                      </span>
                    )}
                  </div>
                )}
                <div className="text-gray-800">
                  {message.message && <p>{message.message}</p>}
                  {message.result && (
                    <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded">
                      <h4 className="font-semibold text-green-800 mb-2">Analysis Result:</h4>
                      <pre className="whitespace-pre-wrap text-sm text-green-700">
                        {typeof message.result === 'string' ? message.result : JSON.stringify(message.result, null, 2)}
                      </pre>
                    </div>
                  )}
                  {message.error && (
                    <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded">
                      <h4 className="font-semibold text-red-800 mb-2">Error:</h4>
                      <p className="text-red-700">{message.error}</p>
                    </div>
                  )}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* User Input Section */}
        {waitingForInput && (
          <div className="p-4 border-t bg-blue-50">
            <div className="mb-3">
              <h4 className="font-semibold text-blue-800 mb-2">🤖 Agent Request:</h4>
              <p className="text-blue-700">{inputPrompt}</p>
            </div>
            <div className="flex space-x-2">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleUserInputSubmit()}
                placeholder="Type your response here..."
                className="flex-1 px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
              <button
                onClick={handleUserInputSubmit}
                disabled={!userInput.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="p-4 border-t bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {isComplete ? (
                <span className="text-green-600 font-semibold">✅ Analysis Complete</span>
              ) : waitingForInput ? (
                <span className="text-orange-600 font-semibold">⏳ Waiting for your input...</span>
              ) : isConnected ? (
                <span className="text-blue-600">🔄 Analysis in progress...</span>
              ) : (
                <span className="text-red-600">❌ Connection lost</span>
              )}
            </div>
            <button
              onClick={handleClose}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              {isComplete ? 'Close' : 'Cancel'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisStream;
