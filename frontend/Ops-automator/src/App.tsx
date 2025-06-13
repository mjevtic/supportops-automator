import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import RuleList from './components/RuleList/RuleList';
import RuleEditor from './components/RuleEditor/RuleEditor';
import WebhookConsole from './components/WebhookConsole/WebhookConsole';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<RuleList />} />
          <Route path="/create" element={<RuleEditor />} />
          <Route path="/webhook-console" element={<WebhookConsole />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
