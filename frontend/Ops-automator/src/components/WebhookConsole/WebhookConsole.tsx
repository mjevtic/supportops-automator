import { useState, useEffect } from 'react';

const samplePayloads = {
  zendesk: {
    ticket: {
      id: 12345,
      subject: "Help needed with integration",
      description: "I'm having trouble connecting your API",
      status: "open",
      priority: "urgent",
      tags: ["urgent", "integration", "api"]
    },
    current_user: {
      id: 67890,
      name: "Support Agent",
      email: "agent@example.com"
    },
    timestamp: new Date().toISOString()
  },
  freshdesk: {
    freshdesk_webhook: {
      ticket_id: 54321,
      ticket_subject: "Cannot access my account",
      ticket_description: "I'm getting an error when trying to login",
      ticket_status: "Open",
      ticket_priority: 2,
      ticket_tags: ["urgent", "login", "account"]
    },
    ticket: {
      id: 54321,
      tags: ["urgent", "login", "account"]
    },
    timestamp: new Date().toISOString()
  }
};

const WebhookConsole = () => {
  const [platform, setPlatform] = useState('zendesk');
  const [payload, setPayload] = useState(JSON.stringify(samplePayloads.zendesk, null, 2));
  
  // Update payload when platform changes
  useEffect(() => {
    setPayload(JSON.stringify(samplePayloads[platform as keyof typeof samplePayloads], null, 2));
  }, [platform]);
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  const platformOptions = [
    { value: 'zendesk', label: 'Zendesk' },
    { value: 'freshdesk', label: 'Freshdesk' }
  ];

  const sendWebhook = async () => {
    try {
      setLoading(true);
      setError(null);
      setResponse(null);
      
      // Add log entry
      const timestamp = new Date().toISOString();
      setLogs(prev => [...prev, `[${timestamp}] Sending ${platform} webhook...`]);
      
      try {
        // Validate JSON is parsable
        JSON.parse(payload);
      } catch (e) {
        throw new Error('Invalid JSON payload');
      }
      
      const API_URL = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${API_URL}/trigger/${platform}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: payload
      });
      
      const data = await response.json();
      
      // Add log entry for response
      const responseTimestamp = new Date().toISOString();
      setLogs(prev => [...prev, `[${responseTimestamp}] Received response: ${JSON.stringify(data)}`]);
      
      setResponse(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send webhook';
      setError(errorMessage);
      
      // Add log entry for error
      const errorTimestamp = new Date().toISOString();
      setLogs(prev => [...prev, `[${errorTimestamp}] ERROR: ${errorMessage}`]);
    } finally {
      setLoading(false);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Webhook Test Console</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Send Test Webhook</h2>
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Platform</label>
          <select 
            className="shadow border rounded w-full py-2 px-3 text-gray-700"
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
          >
            {platformOptions.map(option => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Payload (JSON)</label>
          <div className="flex justify-end mb-2">
            <button 
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 text-xs font-bold py-1 px-2 rounded"
              onClick={() => setPayload(JSON.stringify(samplePayloads[platform as keyof typeof samplePayloads], null, 2))}
            >
              Load Sample Payload
            </button>
          </div>
          <textarea 
            className="shadow border rounded w-full py-2 px-3 text-gray-700 font-mono text-sm h-64"
            value={payload}
            onChange={(e) => setPayload(e.target.value)}
          />
          <p className="text-xs text-gray-500 mt-1">
            {platform === 'zendesk' ? 
              'Zendesk payload should include ticket tags for rule matching.' : 
              'Freshdesk payload should include ticket tags for rule matching.'}
          </p>
        </div>
        
        <button 
          className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={sendWebhook}
          disabled={loading}
        >
          {loading ? 'Sending...' : 'Send Webhook'}
        </button>
      </div>
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Console Logs</h2>
          <button 
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-1 px-3 rounded text-sm"
            onClick={clearLogs}
          >
            Clear Logs
          </button>
        </div>
        
        <div className="bg-gray-900 text-green-300 p-4 rounded-md font-mono text-sm h-64 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-gray-500">No logs yet. Send a webhook to see results.</p>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="mb-1">{log}</div>
            ))
          )}
        </div>
      </div>
      
      {response && (
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Response</h2>
          <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 text-red-800 p-4 rounded-md mt-6">
          {error}
        </div>
      )}
    </div>
  );
};

export default WebhookConsole;
