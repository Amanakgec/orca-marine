export default function AgentReasoning({ steps }) {
  if (!steps || steps.length === 0) return null;

  const agentColors = {
    'Data Agent': '#FF6B35',
    'Safety Agent': '#E74C3C',
    'PFZ Agent': '#2ECC71',
    'Routing Agent': '#3498DB',
    'Synthesis': '#9B59B6'
  };

  return (
    <details className="agent-reasoning">
      <summary>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="4 14 10 14 10 20"></polyline>
          <polyline points="20 10 14 10 14 4"></polyline>
          <line x1="14" y1="10" x2="21" y2="3"></line>
          <line x1="3" y1="21" x2="10" y2="14"></line>
        </svg>
        🤖 Agent Reasoning ({steps.length} steps)
      </summary>
      <div className="reasoning-steps">
        {steps.map((step, idx) => {
          const dotColor = agentColors[step.agent_name] || '#00d4ff';
          return (
            <div key={idx} className="step" style={{ '--dot-color': dotColor }}>
              <div className="step-header">
                <span className="step-agent">{step.agent_name}</span>
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
