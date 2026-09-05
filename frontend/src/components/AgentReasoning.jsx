export default function AgentReasoning({ steps }) {
  if (!steps || steps.length === 0) return null;

  const agentColors = {
    'Data Discovery Agent': '#FF6B35',
    'Data Agent': '#FF6B35',
    'Safety & Risk Agent': '#E74C3C',
    'Safety Agent': '#E74C3C',
    'PFZ Reasoning Agent': '#2ECC71',
    'PFZ Agent': '#2ECC71',
    'Route Optimization Agent': '#00D4FF',
    'Routing Agent': '#00D4FF',
    'Weather & Tide Agent': '#3498DB',
    'Weather Intelligence Agent': '#3498DB',
    'Hydrographic Agent': '#00E5FF',
    'Severe Weather Agent': '#900C3F',
    'Disaster Management Agent': '#FF1744',
    'Ecological Analytics Agent': '#E67E22',
    'Marine Ecology Agent': '#E67E22',
    'Geofencing & Compliance Agent': '#F39C12',
    'Geofencing Agent': '#F39C12',
    'Compliance Agent': '#F39C12',
    'Satellite Earth Observation Agent': '#16A085',
    'Ocean Analytics Agent': '#27AE60',
    'Geospatial Reasoning Agent': '#2980B9',
    'Synthesis Agent': '#9B59B6',
    'Synthesis': '#9B59B6'
  };

  return (
    <details className="agent-reasoning" open>
      <summary>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="4 14 10 14 10 20"></polyline>
          <polyline points="20 10 14 10 14 4"></polyline>
          <line x1="14" y1="10" x2="21" y2="3"></line>
          <line x1="3" y1="21" x2="10" y2="14"></line>
        </svg>
        🤖 Agent Swarm Collaboration ({steps.length} steps)
      </summary>
      <div className="reasoning-steps">
        {steps.map((step, idx) => {
          const dotColor = agentColors[step.agent_name] || '#00d4ff';
          return (
            <div key={idx} className="step" style={{ '--dot-color': dotColor }}>
              <div className="step-header">
                <span className="step-agent" style={{ color: dotColor }}>{step.agent_name}</span>
                <span className="step-action">[{step.action}]</span>
              </div>
              <div className="step-summary">{step.result_summary}</div>
            </div>
          );
        })}
      </div>
    </details>
  );
}
