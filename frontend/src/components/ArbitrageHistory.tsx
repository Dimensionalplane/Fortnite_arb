import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface ArbitrageOpportunity {
  item: string;
  current_price: number;
  target_price: number;
  margin: number;
  timestamp: string;
}

const ArbitrageHistory: React.FC = () => {
  const [history, setHistory] = useState<ArbitrageOpportunity[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchHistory = async () => {
    try {
      const response = await axios.get<ArbitrageOpportunity[]>('http://localhost:8080/api/arbitrage/history');
      setHistory(response.data || []);
    } catch (err) {
      console.error('Failed to fetch arbitrage history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading Arbitrage History...</div>;

  return (
    <div style={{ marginTop: '40px' }}>
      <h2>Arbitrage Opportunity History</h2>
      {history.length === 0 ? (
        <p>No history recorded yet.</p>
      ) : (
        <table border={1} cellPadding={10} style={{ width: '100%', textAlign: 'left' }}>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Item</th>
              <th>Price</th>
              <th>Target</th>
              <th>Margin</th>
            </tr>
          </thead>
          <tbody>
            {[...history].reverse().map((opp, idx) => (
              <tr key={idx}>
                <td>{new Date(opp.timestamp).toLocaleString()}</td>
                <td>{opp.item}</td>
                <td>{opp.current_price}</td>
                <td>{opp.target_price}</td>
                <td style={{ color: 'green', fontWeight: 'bold' }}>
                  {(opp.margin * 100).toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ArbitrageHistory;
