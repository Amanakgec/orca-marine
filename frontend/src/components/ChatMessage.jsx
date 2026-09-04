import AgentReasoning from './AgentReasoning';

export default function ChatMessage({ message }) {
  const { role, content, reasoning, timestamp } = message;
  const isUser = role === 'user';

  // Basic markdown bold formatting
  const formatText = (text) => {
    if (!text) return '';
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  const formattedTime = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-bubble">
        {content.split('\n').map((line, i) => (
          <div key={i} style={{ minHeight: '1em' }}>
            {formatText(line)}
          </div>
        ))}
        {reasoning && reasoning.length > 0 && (
          <AgentReasoning steps={reasoning} />
        )}
      </div>
      <div className="message-time">{formattedTime}</div>
    </div>
  );
}
