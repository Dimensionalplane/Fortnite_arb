import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface SubmoduleStatus {
  path: string;
  status: string;
}

const SystemDashboard: React.FC = () => {
  const [statuses, setStatuses] = useState<SubmoduleStatus[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      const response = await axios.get<SubmoduleStatus[]>('http://localhost:8080/api/system/status');
      setStatuses(response.data || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch system status from Go backend.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading System Dashboard...</div>;

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>System Observability Dashboard</h1>
      {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}

      <section>
        <h2>Submodule Status</h2>
        {statuses.length === 0 ? (
          <p>No submodules detected or Git error.</p>
        ) : (
          <table border={1} cellPadding={10} style={{ width: '100%', textAlign: 'left' }}>
            <thead>
              <tr>
                <th>Path</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {statuses.map((s) => (
                <tr key={s.path}>
                  <td>{s.path}</td>
                  <td style={{
                    fontWeight: 'bold',
                    color: s.status === 'synced' ? 'green' : (s.status === 'out-of-sync' ? 'orange' : 'red')
                  }}>
                    {s.status.toUpperCase()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <button onClick={fetchStatus} style={{ marginTop: '20px' }}>Refresh Now</button>
    </div>
  );
};

export default SystemDashboard;
