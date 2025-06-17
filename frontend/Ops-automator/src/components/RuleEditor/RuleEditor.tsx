import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

interface Action {
  platform: string;
  action: string;
  [key: string]: any;
}

interface Rule {
  name?: string;
  description?: string;
  trigger_platform: string;
  trigger_event: string;
  trigger_data: string;
  actions: Action[];
}

const RuleEditor = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [rule, setRule] = useState<Rule>({
    name: '',
    description: '',
    trigger_platform: 'zendesk',
    trigger_event: 'ticket_tag_added',
    trigger_data: JSON.stringify({ tag: '' }, null, 2),
    actions: []
  });

  const [currentAction, setCurrentAction] = useState<Action>({
    platform: 'slack',
    action: 'send_message',
  });

  const [actionParams, setActionParams] = useState('{}');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<{ success: boolean; message: string } | null>(null);

  const platformOptions = [
    { value: 'zendesk', label: 'Zendesk' },
    { value: 'freshdesk', label: 'Freshdesk' }
  ];

  const eventOptions: { [key: string]: { value: string; label: string }[] } = {
    zendesk: [
      { value: 'ticket_tag_added', label: 'Ticket Tag Added' }
    ],
    freshdesk: [
      { value: 'ticket_tag_added', label: 'Ticket Tag Added' }
    ]
  };

  const actionPlatformOptions = [
    { value: 'zendesk', label: 'Zendesk' },
    { value: 'freshdesk', label: 'Freshdesk' },
    { value: 'slack', label: 'Slack' },
    { value: 'trello', label: 'Trello' },
    { value: 'google_sheets', label: 'Google Sheets' },
    { value: 'notion', label: 'Notion' },
    { value: 'linear', label: 'Linear' },
    { value: 'discord', label: 'Discord' }
  ];

  const actionTypeOptions: { [key: string]: { value: string; label: string }[] } = {
    zendesk: [
      { value: 'create_ticket', label: 'Create Ticket' },
      { value: 'update_ticket', label: 'Update Ticket' },
      { value: 'add_comment', label: 'Add Comment' }
    ],
    freshdesk: [
      { value: 'create_ticket', label: 'Create Ticket' },
      { value: 'update_ticket', label: 'Update Ticket' },
      { value: 'add_note', label: 'Add Note' }
    ],
    slack: [{ value: 'send_message', label: 'Send Message' }],
    trello: [{ value: 'create_card', label: 'Create Card' }],
    google_sheets: [{ value: 'append_row', label: 'Append Row' }],
    notion: [{ value: 'create_database_item', label: 'Create Database Item' }],
    linear: [{ value: 'create_issue', label: 'Create Issue' }],
    discord: [{ value: 'send_message', label: 'Send Message' }]
  };

  const [availableIntegrations, setAvailableIntegrations] = useState<Array<{id: string, name: string, integration_type: string}>>([]);

  useEffect(() => {
    if (isEditing) {
      const fetchRule = async () => {
        try {
          const API_URL = import.meta.env.VITE_API_URL || '';
          const response = await fetch(`${API_URL}/rules/${id}`);
          if (response.ok) {
            const data = await response.json();
            if (typeof data.actions === 'string') {
              try {
                data.actions = JSON.parse(data.actions);
              } catch (e) {
                console.error("Failed to parse actions string:", e);
                data.actions = [];
              }
            }
            setRule(data);
          } else {
            console.error('Failed to fetch rule for editing');
          }
        } catch (error) {
          console.error('Error fetching rule:', error);
        }
      };
      fetchRule();
    }

    const fetchIntegrations = async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL || '';
        const response = await fetch(`${API_URL}/integrations`);
        if (response.ok) {
          const data = await response.json();
          setAvailableIntegrations(data);
        }
      } catch (error) {
        console.error('Failed to fetch integrations:', error);
      }
    };
    
    fetchIntegrations();
  }, [id, isEditing]);

  const handleTriggerPlatformChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const platform = e.target.value;
    setRule({
      ...rule,
      trigger_platform: platform,
      trigger_event: eventOptions[platform][0].value
    });
  };

  const handleTriggerEventChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setRule({ ...rule, trigger_event: e.target.value });
  };

  const handleTriggerDataChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setRule({ ...rule, trigger_data: e.target.value });
  };

  const handleActionPlatformChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const platform = e.target.value;
    const isIntegrationPlatform = ['zendesk', 'freshdesk', 'slack'].includes(platform);
    const integrationsOfType = availableIntegrations.filter(i => i.integration_type === platform);
    
    setCurrentAction({
      platform,
      action: actionTypeOptions[platform][0].value,
      ...(isIntegrationPlatform && integrationsOfType.length > 0 ? { integration_id: integrationsOfType[0].id } : {})
    });
    setActionParams('{}');
  };

  const handleActionTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCurrentAction({ ...currentAction, action: e.target.value });
    setActionParams('{}');
  };

  const handleActionParamsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setActionParams(e.target.value);
  };

  const addAction = () => {
    try {
      const params = JSON.parse(actionParams || '{}');
      const newAction = { ...currentAction, ...params };
      setRule({ ...rule, actions: [...rule.actions, newAction] });
      setCurrentAction({ platform: 'slack', action: 'send_message' });
      setActionParams('{}');
    } catch (error) {
      alert('Invalid JSON in action parameters.');
    }
  };

  const removeAction = (index: number) => {
    const newActions = [...rule.actions];
    newActions.splice(index, 1);
    setRule({ ...rule, actions: newActions });
  };

  const handleSubmit = async () => {
    const API_URL = import.meta.env.VITE_API_URL || '';
    const url = isEditing ? `${API_URL}/rules/${id}` : `${API_URL}/rules/`;
    const method = isEditing ? 'PUT' : 'POST';

    try {
      JSON.parse(rule.trigger_data);
    } catch (error) {
      setSubmitResult({ success: false, message: 'Invalid JSON in trigger data.' });
      return;
    }

    setIsSubmitting(true);
    setSubmitResult(null);

    try {
      const response = await fetch(url, {
        method,
        mode: 'cors',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({
          user_id: 1,
          name: rule.name || 'New Rule',
          description: rule.description || '',
          trigger_platform: rule.trigger_platform,
          trigger_event: rule.trigger_event,
          trigger_data: rule.trigger_data,
          actions: Array.isArray(rule.actions) ? rule.actions : []
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSubmitResult({ success: true, message: `Rule ${isEditing ? 'updated' : 'created'} successfully!` });
        setTimeout(() => navigate('/'), 2000);
      } else {
        setSubmitResult({ success: false, message: `Error: ${data.detail || `Failed to ${isEditing ? 'update' : 'create'} rule`}` });
      }
    } catch (error) {
      setSubmitResult({ success: false, message: 'An unexpected error occurred.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">{isEditing ? 'Edit Rule' : 'Create New Rule'}</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Rule Name</label>
          <input 
            type="text"
            className="shadow border rounded w-full py-2 px-3 text-gray-700"
            value={rule.name || ''}
            onChange={(e) => setRule({...rule, name: e.target.value})}
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Description</label>
          <input 
            type="text"
            className="shadow border rounded w-full py-2 px-3 text-gray-700"
            value={rule.description || ''}
            onChange={(e) => setRule({...rule, description: e.target.value})}
          />
        </div>

        <h2 className="text-xl font-semibold mb-4">Trigger</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">Platform</label>
            <select 
              className="shadow border rounded w-full py-2 px-3 text-gray-700"
              value={rule.trigger_platform}
              onChange={handleTriggerPlatformChange}
            >
              {platformOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">Event</label>
            <select 
              className="shadow border rounded w-full py-2 px-3 text-gray-700"
              value={rule.trigger_event}
              onChange={handleTriggerEventChange}
            >
              {eventOptions[rule.trigger_platform]?.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Trigger Data (JSON)</label>
          <textarea 
            className="shadow border rounded w-full py-2 px-3 text-gray-700 font-mono text-sm h-32"
            value={rule.trigger_data}
            onChange={handleTriggerDataChange}
          />
          <p className="text-xs text-gray-500 mt-1">Example: {`{ "tag": "urgent" }`}</p>
        </div>
      </div>
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Actions</h2>
        
        {rule.actions.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-2">Current Actions</h3>
            <ul className="divide-y divide-gray-200">
              {rule.actions.map((action, index) => (
                <li key={index} className="py-3 flex justify-between items-center">
                  <div>
                    <p><span className="font-medium">{action.platform}</span>: {action.action}</p>
                    <p className="text-xs text-gray-500 font-mono">{JSON.stringify(action, null, 2)}</p>
                  </div>
                  <button 
                    className="text-red-500 hover:text-red-700 font-semibold py-1 px-3 rounded"
                    onClick={() => removeAction(index)}
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="bg-gray-50 p-4 rounded-md border border-gray-200">
          <h3 className="text-lg font-medium mb-3">Add New Action</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2">Platform</label>
              <select 
                className="shadow border rounded w-full py-2 px-3 text-gray-700"
                value={currentAction.platform}
                onChange={handleActionPlatformChange}
              >
                {actionPlatformOptions.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2">Action Type</label>
              <select 
                className="shadow border rounded w-full py-2 px-3 text-gray-700"
                value={currentAction.action}
                onChange={handleActionTypeChange}
              >
                {actionTypeOptions[currentAction.platform]?.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Action Parameters (JSON)</label>
            <textarea 
              className="shadow border rounded w-full py-2 px-3 text-gray-700 font-mono text-sm h-24"
              placeholder='e.g., { "channel": "#general", "text": "Hello" }'
              value={actionParams}
              onChange={handleActionParamsChange}
            />
          </div>

          <button 
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            onClick={addAction}
          >
            Add Action
          </button>
        </div>
      </div>

      {submitResult && (
        <div className={`p-4 mb-4 rounded ${submitResult.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {submitResult.message}
        </div>
      )}

      <div className="flex justify-end">
        <button 
          className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
          onClick={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Saving...' : (isEditing ? 'Update Rule' : 'Create Rule')}
        </button>
      </div>
    </div>
  );
};

export default RuleEditor;
