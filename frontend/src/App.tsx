import SystemDashboard from './components/SystemDashboard';
import ArbitrageHistory from './components/ArbitrageHistory';

function App() {
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <SystemDashboard />
      <hr />
      <ArbitrageHistory />
    </div>
  );
}

export default App;
