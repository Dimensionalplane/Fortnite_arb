import SystemDashboard from './components/SystemDashboard';
import ArbitrageHistory from './components/ArbitrageHistory';
import ConfigurationEditor from './components/ConfigurationEditor';

function App() {
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <h1>Steam Market Arbitrage Bot</h1>
      <SystemDashboard />
      <hr />
      <ConfigurationEditor />
      <hr />
      <ArbitrageHistory />
    </div>
  );
}

export default App;
