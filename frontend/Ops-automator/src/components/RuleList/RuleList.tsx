import { useState, useEffect } from 'react';

interface Action {
  platform: string;
  action: string;
  [key: string]: any;
}

interface Rule {
  id: number;
  trigger_platform: string;
  trigger_event: string;
  trigger_data: string;
  actions: string;
  created_at: string;
}

const RuleList = () => {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState(false);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/rules');
      
      if (!response.ok) {
        throw new Error(`Error fetching rules: ${response.statusText}`);
      }
      
      const data = await response.json();
      setRules(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch rules');
    } finally {
      setLoading(false);
    }
  };

  const confirmDelete = (id: number) => {
    setDeleteId(id);
    setDeleteConfirm(true);
  };

  const cancelDelete = () => {
    setDeleteId(null);
    setDeleteConfirm(false);
  };

  const deleteRule = async () => {
    if (deleteId === null) return;
    
    try {
      const response = await fetch(`/api/rules/${deleteId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error(`Error deleting rule: ${response.statusText}`);
      }
      
      // Remove the deleted rule from the list
      setRules(rules.filter(rule => rule.id !== deleteId));
      setDeleteConfirm(false);
      setDeleteId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete rule');
    }
  };

  const formatTriggerSummary = (rule: Rule) => {
    let triggerData = {};
    try {
      triggerData = JSON.parse(rule.trigger_data);
    } catch (e) {
      // Invalid JSON, use empty object
    }
    
    if (rule.trigger_platform === 'zendesk' || rule.trigger_platform === 'freshdesk') {
      if (rule.trigger_event === 'ticket_tag_added') {
        return `When ${rule.trigger_platform} ticket is tagged with "${triggerData?.tag || 'any'}"`;
      }
    }
    
    return `${rule.trigger_platform} - ${rule.trigger_event}`;
  };

  const formatActionsSummary = (rule: Rule) => {
    let actions: Action[] = [];
    try {
      actions = JSON.parse(rule.actions);
    } catch (e) {
      return 'No actions or invalid format';
    }
    
    if (!actions.length) {
      return 'No actions';
    }
    
    return actions.map((action, index) => {
      let summary = `${action.platform}: ${action.action}`;
      
      if (action.platform === 'slack' && action.action === 'send_message') {
        summary += action.channel ? ` to ${action.channel}` : '';
      } else if (action.platform === 'trello' && action.action === 'create_card') {
        summary += action.list_name ? ` in ${action.list_name}` : '';
      }
      
      return (
        <div key={index} className="mb-1">
          {summary}
        </div>
      );
    });
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Rules</h1>
        <button 
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          onClick={() => window.location.href = '/create'}
        >
          Create New Rule
        </button>
      </div>
      
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4">Loading rules...</p>
        </div>
      ) : error ? (
        <div className="bg-red-100 text-red-800 p-4 rounded-md">
          {error}
        </div>
      ) : rules.length === 0 ? (
        <div className="bg-gray-100 p-8 rounded-md text-center">
          <p className="text-lg text-gray-600">No rules found</p>
          <p className="mt-2 text-gray-500">Create your first rule to get started</p>
        </div>
      ) : (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Trigger
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Options
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {rules.map(rule => (
                <tr key={rule.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {rule.id}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatTriggerSummary(rule)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatActionsSummary(rule)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      className="text-red-600 hover:text-red-900 ml-4"
                      onClick={() => confirmDelete(rule.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
            <h3 className="text-lg font-medium mb-4">Confirm Delete</h3>
            <p className="mb-6">Are you sure you want to delete rule #{deleteId}? This action cannot be undone.</p>
            <div className="flex justify-end space-x-3">
              <button 
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded"
                onClick={cancelDelete}
              >
                Cancel
              </button>
              <button 
                className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                onClick={deleteRule}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RuleList;
