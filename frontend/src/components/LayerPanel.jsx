export default function LayerPanel({ layers, visibleLayers, onToggleLayer }) {
  if (!layers || layers.length === 0) return null;

  return (
    <div className="layer-panel">
      <h3>Map Layers</h3>
      {layers.map(layer => {
        const isVisible = visibleLayers.has(layer.id);
        const color = layer.style?.color || '#00d4ff';
        const featureCount = layer.data?.features?.length || 0;
        
        return (
          <div key={layer.id} className="layer-item">
            <input 
              type="checkbox" 
              checked={isVisible} 
              onChange={() => onToggleLayer(layer.id)}
              style={{ cursor: 'pointer' }}
            />
            <div className="layer-color-swatch" style={{ backgroundColor: color }}></div>
            <span style={{ flex: 1 }}>{layer.label || layer.id}</span>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>({featureCount})</span>
          </div>
        );
      })}
    </div>
  );
}
