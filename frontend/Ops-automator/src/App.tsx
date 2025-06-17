import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import RuleList from './components/RuleList/RuleList';
import RuleEditor from './components/RuleEditor/RuleEditor';
import WebhookConsole from './components/WebhookConsole/WebhookConsole';
import IntegrationsList from './components/Integrations/IntegrationsList';
import IntegrationForm from './components/Integrations/IntegrationForm';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<RuleList />} />
          <Route path="/create" element={<RuleEditor />} />
          <Route path="/edit/:id" element={<RuleEditor />} />
          <Route path="/webhook-console" element={<WebhookConsole />} />
          <Route path="/integrations" element={<IntegrationsList />} />
          <Route path="/integrations/new" element={<IntegrationForm />} />
          <Route path="/integrations/edit/:id" element={<IntegrationForm />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
