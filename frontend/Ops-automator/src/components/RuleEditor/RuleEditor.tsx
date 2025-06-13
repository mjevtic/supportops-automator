import { useState, useEffect } from 'react';

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
  const [rule, setRule] = useState<Rule>({
    trigger_platform: 'zendesk',
    trigger_event: 'ticket_tag_added',
    trigger_data: JSON.stringify({ tag: '' }, null, 2),
    actions: []
  });

  const [currentAction, setCurrentAction] = useState<Action>({
    platform: 'slack',
    action: 'send_message',
  });

  const [jsonPreview, setJsonPreview] = useState<string>('');
  const [showPreview, setShowPreview] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<{ success: boolean; message: string } | null>(null);

  const platformOptions = [
    { value: 'zendesk', label: 'Zendesk' },
    { value: 'freshdesk', label: 'Freshdesk' }
  ];

  const eventOptions = {
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

  const actionTypeOptions = {
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

  const handleTriggerPlatformChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const platform = e.target.value;
    setRule({
      ...rule,
      trigger_platform: platform,
      trigger_event: eventOptions[platform as keyof typeof eventOptions][0].value
    });
  };

  const handleTriggerEventChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setRule({
      ...rule,
      trigger_event: e.target.value
    });
  };

  const handleTriggerDataChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setRule({
      ...rule,
      trigger_data: e.target.value
    });
  };

  const [availableIntegrations, setAvailableIntegrations] = useState<Array<{id: string, name: string, integration_type: string}>>([]);
  
  // Fetch available integrations on component mount
  useEffect(() => {
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
  }, []);

  const handleActionPlatformChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const platform = e.target.value;
    
    // Check if this is an integration platform
    const isIntegrationPlatform = ['zendesk', 'freshdesk', 'slack'].includes(platform);
    
    // Get available integrations of this type
    const integrationsOfType = availableIntegrations.filter(i => i.integration_type === platform);
    
    setCurrentAction({
      platform,
      action: actionTypeOptions[platform as keyof typeof actionTypeOptions][0].value,
      ...(isIntegrationPlatform && integrationsOfType.length > 0 ? { integration_id: integrationsOfType[0].id } : {})
    });
  };

  const handleActionTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCurrentAction({
      ...currentAction,
      action: e.target.value
    });
  };

  const handleActionParamsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    try {
      const params = JSON.parse(e.target.value);
      setCurrentAction({
        ...currentAction,
        ...params
      });
    } catch (error) {
      // Invalid JSON, ignore for now
    }
  };

  const addAction = () => {
    setRule({
      ...rule,
      actions: [...rule.actions, currentAction]
    });
    // Reset current action to default
    setCurrentAction({
      platform: 'slack',
      action: 'send_message',
    });
  };

  const removeAction = (index: number) => {
    const newActions = [...rule.actions];
    newActions.splice(index, 1);
    setRule({
      ...rule,
      actions: newActions
    });
  };

  const generatePreview = () => {
    try {
      // Validate trigger data is valid JSON
      JSON.parse(rule.trigger_data);
      
      const ruleJson = {
        ...rule,
        actions: JSON.stringify(rule.actions)
      };
      
      setJsonPreview(JSON.stringify(ruleJson, null, 2));
      setShowPreview(true);
    } catch (error) {
      setSubmitResult({
        success: false,
        message: 'Invalid JSON in trigger data'
      });
    }
  };

  const handleSubmit = async () => {
    try {
      // Validate trigger data is valid JSON
      JSON.parse(rule.trigger_data);
      
      setIsSubmitting(true);
      setSubmitResult(null);
      
      const API_URL = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${API_URL}/rules`, {
        method: 'POST',
        mode: 'cors',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({
          name: rule.name || 'New Rule',
          description: rule.description || '',
          trigger_platform: rule.trigger_platform,
          trigger_event: rule.trigger_event,
          trigger_data: rule.trigger_data,
          actions: rule.actions
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSubmitResult({
          success: true,
          message: 'Rule created successfully!'
        });
        // Reset form
        setRule({
          trigger_platform: 'zendesk',
          trigger_event: 'ticket_tag_added',
          trigger_data: JSON.stringify({ tag: '' }, null, 2),
          actions: []
        });
      } else {
        setSubmitResult({
          success: false,
          message: `Error: ${data.detail || 'Failed to create rule'}`
        });
      }
    } catch (error) {
      setSubmitResult({
        success: false,
        message: 'Invalid JSON in trigger data or actions'
      });
    } finally {
      setIsSubmitting(false);
      setShowPreview(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Create New Rule</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Trigger</h2>
        
        <div className="mb-4">
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
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Event</label>
          <select 
            className="shadow border rounded w-full py-2 px-3 text-gray-700"
            value={rule.trigger_event}
            onChange={handleTriggerEventChange}
          >
            {eventOptions[rule.trigger_platform as keyof typeof eventOptions]?.map(option => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Trigger Data (JSON)</label>
          <textarea 
            className="shadow border rounded w-full py-2 px-3 text-gray-700 font-mono text-sm h-32"
            value={rule.trigger_data}
            onChange={handleTriggerDataChange}
          />
          <p className="text-xs text-gray-500 mt-1">Example: {"{ \"tag\": \"urgent\" }"}</p>
        </div>
      </div>
      
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Actions</h2>
        
        {rule.actions.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-2">Current Actions</h3>
            <ul className="divide-y divide-gray-200">
              {rule.actions.map((action, index) => (
                <li key={index} className="py-3 flex justify-between">
                  <div>
                    <span className="font-medium">{action.platform}</span>: {action.action}
                  </div>
                  <button 
                    className="text-red-500 hover:text-red-700"
                    onClick={() => removeAction(index)}
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="bg-gray-50 p-4 rounded-md">
          <h3 className="text-lg font-medium mb-3">Add New Action</h3>
          
          <div className="mb-4">
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
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Action Type</label>
            <select 
              className="shadow border rounded w-full py-2 px-3 text-gray-700"
              value={currentAction.action}
              onChange={handleActionTypeChange}
            >
              {actionTypeOptions[currentAction.platform as keyof typeof actionTypeOptions]?.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
          
          {/* Show integration selector for integration platforms */}
          {['zendesk', 'freshdesk', 'slack'].includes(currentAction.platform) && (
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">Select Integration</label>
              <select
                className="shadow border rounded w-full py-2 px-3 text-gray-700"
                value={currentAction.integration_id || ''}
                onChange={(e) => setCurrentAction({
                  ...currentAction,
                  integration_id: e.target.value
                })}
              >
                {availableIntegrations
                  .filter(integration => integration.integration_type === currentAction.platform)
                  .map(integration => (
                    <option key={integration.id} value={integration.id}>{integration.name}</option>
                  ))}
              </select>
              {availableIntegrations.filter(i => i.integration_type === currentAction.platform).length === 0 && (
                <p className="text-xs text-red-500 mt-1">
                  No {currentAction.platform} integrations found. <a href="/integrations/new" className="text-blue-500 underline">Add one first</a>.
                </p>
              )}
            </div>
          )}
          
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Action Parameters (JSON)</label>
            <textarea 
              className="shadow border rounded w-full py-2 px-3 text-gray-700 font-mono text-sm h-32"
              placeholder="Enter action parameters as JSON"
              onChange={handleActionParamsChange}
            />
            <p className="text-xs text-gray-500 mt-1">
              {currentAction.platform === 'zendesk' && currentAction.action === 'create_ticket' && 
                'Example: { "subject": "New ticket from automation", "description": "This ticket was created automatically" }'
              }
              {currentAction.platform === 'freshdesk' && currentAction.action === 'create_ticket' && 
                'Example: { "subject": "New ticket from automation", "description": "This ticket was created automatically" }'
              }
              {currentAction.platform === 'slack' && 
                'Example: { "channel": "#support", "message": "New urgent ticket!" }'
              }
            </p>
          </div>
          
          <button 
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            onClick={addAction}
          >
            Add Action
          </button>
        </div>
      </div>
      
      <div className="flex justify-between">
        <button 
          className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
          onClick={generatePreview}
        >
          Preview JSON
        </button>
        
        <button 
          className={`bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
          onClick={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : 'Create Rule'}
        </button>
      </div>
      
      {showPreview && (
        <div className="mt-6 bg-gray-100 p-4 rounded-md">
          <h3 className="text-lg font-medium mb-2">JSON Preview</h3>
          <pre className="bg-gray-800 text-green-300 p-4 rounded overflow-x-auto text-sm">
            {jsonPreview}
          </pre>
        </div>
      )}
      
      {submitResult && (
        <div className={`mt-6 p-4 rounded-md ${submitResult.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {submitResult.message}
        </div>
      )}
    </div>
  );
};

export default RuleEditor;
