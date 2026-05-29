import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ConfigurationEditor: React.FC = () => {
  const [config, setConfig] = useState<string>('');
  const [status, setStatus] = useState<string>('');

  const fetchConfig = async () => {
    try {
      const response = await axios.get('http://localhost:8080/api/config');
      setConfig(JSON.stringify(response.data, null, 4));
    } catch (err) {
      console.error('Failed to fetch configuration:', err);
    }
  };

  const saveConfig = async () => {
    try {
      await axios.post('http://localhost:8080/api/config', JSON.parse(config));
      setStatus('Configuration saved successfully!');
      setTimeout(() => setStatus(''), 3000);
    } catch (err) {
      setStatus('Error saving configuration. Ensure JSON is valid.');
      console.error(err);
    }
  };

  const triggerScan = async () => {
    try {
      const response = await axios.post('http://localhost:8080/api/arbitrage/scan');
      setStatus(response.data.message);
      setTimeout(() => setStatus(''), 5000);
    } catch (err) {
      setStatus('Failed to trigger scan.');
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  return (
    <div style={{ marginTop: '40px' }}>
      <h2>Scanner Configuration</h2>
      {status && <div style={{ color: 'blue', marginBottom: '10px' }}>{status}</div>}
      <textarea
        value={config}
        onChange={(e) => setConfig(e.target.value)}
        style={{ width: '100%', height: '300px', fontFamily: 'monospace' }}
      />
      <div style={{ marginTop: '10px' }}>
        <button onClick={saveConfig}>Save Configuration</button>
        <button onClick={triggerScan} style={{ marginLeft: '10px', backgroundColor: '#e74c3c', color: 'white' }}>
          Trigger Manual Scan
        </button>
      </div>
    </div>
  );
};

export default ConfigurationEditor;
