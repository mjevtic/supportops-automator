import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

interface IntegrationFormData {
  name: string;
  integration_type: string;
  config: Record<string, any>;
}

const IntegrationForm = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditing = !!id;
  
  const [formData, setFormData] = useState<IntegrationFormData>({
    name: '',
    integration_type: 'zendesk',
    config: {}
  });
  
  const [loading, setLoading] = useState(isEditing);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Integration type options
  const integrationTypes = [
    { value: 'zendesk', label: 'Zendesk' },
    { value: 'freshdesk', label: 'Freshdesk' }
  ];

  // Config fields for each integration type
  const configFields = {
    zendesk: [
      { name: 'subdomain', label: 'Subdomain', type: 'text', placeholder: 'your-subdomain' },
      { name: 'email', label: 'Email', type: 'email', placeholder: 'email@example.com' },
      { name: 'api_token', label: 'API Token', type: 'password', placeholder: 'Enter API token' }
    ],
    freshdesk: [
      { name: 'domain', label: 'Domain', type: 'text', placeholder: 'your-domain.freshdesk.com' },
      { name: 'api_key', label: 'API Key', type: 'password', placeholder: 'Enter API key' }
    ]
  };

  useEffect(() => {
    if (isEditing) {
      fetchIntegration();
    }
  }, [id]);

  const fetchIntegration = async () => {
    try {
      setLoading(true);
      const API_URL = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${API_URL}/integrations/${id}`);
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Set form data from fetched integration
      setFormData({
        name: data.name,
        integration_type: data.integration_type,
        config: data.config || {}
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch integration');
      console.error('Error fetching integration:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name === 'integration_type') {
      // Reset config when integration type changes
      setFormData({
        ...formData,
        integration_type: value,
        config: {}
      });
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const handleConfigChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    setFormData({
      ...formData,
      config: {
        ...formData.config,
        [name]: value
      }
    });
  };

  const testConnection = async () => {
    try {
      setTesting(true);
      setTestResult(null);
      
      const API_URL = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${API_URL}/integrations/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          integration_type: formData.integration_type,
          config: formData.config
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      setTestResult({
        success: data.success,
        message: data.message || (data.success ? 'Connection successful!' : 'Connection failed. Please check your credentials.')
      });
    } catch (err) {
      setTestResult({
        success: false,
        message: err instanceof Error ? err.message : 'Connection test failed'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setSubmitting(true);
      setError(null);
      
      const API_URL = import.meta.env.VITE_API_URL || '';
      const url = isEditing 
        ? `${API_URL}/integrations/${id}` 
        : `${API_URL}/integrations`;
      
      // For demo purposes, we're using a fixed user ID
      // In a real app, this would come from authentication
      const dataToSubmit = {
        ...formData,
        user_id: 1 // Adding user_id for the API
      };
      
      const response = await fetch(url, {
        method: isEditing ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSubmit)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
      }
      
      // Navigate back to integrations list on success
      navigate('/integrations');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save integration');
      console.error('Error saving integration:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">
        {isEditing ? 'Edit Integration' : 'Add New Integration'}
      </h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6">
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name">
            Integration Name
          </label>
          <input
            id="name"
            name="name"
            type="text"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={formData.name}
            onChange={handleInputChange}
            placeholder="My Zendesk Integration"
            required
          />
        </div>
        
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="integration_type">
            Integration Type
          </label>
          <select
            id="integration_type"
            name="integration_type"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={formData.integration_type}
            onChange={handleInputChange}
            disabled={isEditing} // Can't change type when editing
          >
            {integrationTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
          {isEditing && (
            <p className="text-xs text-gray-500 mt-1">Integration type cannot be changed after creation.</p>
          )}
        </div>
        
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-4">Configuration</h3>
          
          {configFields[formData.integration_type as keyof typeof configFields]?.map(field => (
            <div className="mb-4" key={field.name}>
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor={field.name}>
                {field.label}
              </label>
              <input
                id={field.name}
                name={field.name}
                type={field.type}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                value={formData.config[field.name] || ''}
                onChange={handleConfigChange}
                placeholder={field.placeholder}
                required
              />
            </div>
          ))}
        </div>
        
        <div className="flex items-center justify-between mb-4">
          <button
            type="button"
            className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${testing ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={testConnection}
            disabled={testing}
          >
            {testing ? 'Testing...' : 'Test Connection'}
          </button>
          
          <button
            type="submit"
            className={`bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${submitting ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={submitting}
          >
            {submitting ? 'Saving...' : 'Save Integration'}
          </button>
        </div>
        
        {testResult && (
          <div className={`mt-4 p-4 rounded-md ${testResult.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {testResult.message}
          </div>
        )}
      </form>
    </div>
  );
};

export default IntegrationForm;
