import { useEffect, useRef, useState, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import LayerPanel from './LayerPanel';

export default function MapView({ layers }) {
  const mapContainer = useRef(null);
  const mapRef = useRef(null);
  const [visibleLayers, setVisibleLayers] = useState(new Set());

  // Initialize Map
  useEffect(() => {
    if (mapRef.current) return; // initialize map only once

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
      center: [80.2, 10.5], // Tamil Nadu coast
      zoom: 6,
      attributionControl: false
    });

    map.addControl(new maplibregl.NavigationControl(), 'bottom-right');
    map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right');

    map.on('load', () => {
      mapRef.current = map;
    });

    return () => {
      map.remove();
    };
  }, []);

  // Sync Layers
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return; // Wait for map to load fully

    // Optional: wait for 'load' if called before style loads
    const syncLayers = () => {
      // 1. Remove old layers not in props
      const currentIds = layers.map(l => l.id);
      const existingSources = map.getStyle().sources;
      
      Object.keys(existingSources).forEach(sourceId => {
        if (sourceId.startsWith('orca-') && !currentIds.includes(sourceId.replace('orca-', ''))) {
          if (map.getLayer(sourceId)) map.removeLayer(sourceId);
          map.removeSource(sourceId);
        }
      });

      // 2. Add or update new layers
      layers.forEach(layer => {
        const sourceId = `orca-${layer.id}`;
        if (!map.getSource(sourceId)) {
          map.addSource(sourceId, {
            type: 'geojson',
            data: layer.data
          });
        } else {
          map.getSource(sourceId).setData(layer.data);
        }

        if (!map.getLayer(sourceId)) {
          const paint = {};
          
          if (layer.type === 'fill') {
            paint['fill-color'] = layer.style?.color || '#00d4ff';
            paint['fill-opacity'] = layer.style?.opacity !== undefined ? layer.style.opacity : 0.5;
          } else if (layer.type === 'line') {
            paint['line-color'] = layer.style?.color || '#00d4ff';
            paint['line-width'] = layer.style?.width || 2;
          } else if (layer.type === 'circle') {
            paint['circle-color'] = layer.style?.color || '#00d4ff';
            paint['circle-radius'] = layer.style?.width || 6;
            paint['circle-opacity'] = layer.style?.opacity !== undefined ? layer.style.opacity : 0.8;
            paint['circle-stroke-width'] = 1;
            paint['circle-stroke-color'] = '#fff';
          }

          map.addLayer({
            id: sourceId,
            type: layer.type,
            source: sourceId,
            paint: paint,
            layout: {
              visibility: visibleLayers.has(layer.id) ? 'visible' : 'none'
            }
          });

          // Add click event for popups
          map.on('click', sourceId, (e) => {
            const coordinates = e.lngLat;
            const properties = e.features[0].properties;
            
            let html = '<div style="font-size:12px;">';
            for (const [key, value] of Object.entries(properties)) {
              html += `<strong>${key}:</strong> ${value}<br/>`;
            }
            html += '</div>';

            new maplibregl.Popup()
              .setLngLat(coordinates)
              .setHTML(html)
              .addTo(map);
          });

          // Change cursor on hover
          map.on('mouseenter', sourceId, () => {
            map.getCanvas().style.cursor = 'pointer';
          });
          map.on('mouseleave', sourceId, () => {
            map.getCanvas().style.cursor = '';
          });
        } else {
          // Update visibility
          map.setLayoutProperty(
            sourceId, 
            'visibility', 
            visibleLayers.has(layer.id) ? 'visible' : 'none'
          );
        }
      });
    };

    // If map is already loaded, sync immediately
    if (map.isStyleLoaded()) {
      syncLayers();
    } else {
      map.on('load', syncLayers);
    }
    
  }, [layers, visibleLayers]);

  // Initial population of visible layers when new layers arrive
  useEffect(() => {
    setVisibleLayers(prev => {
      const next = new Set(prev);
      layers.forEach(l => {
        if (!next.has(l.id)) next.add(l.id);
      });
      return next;
    });
  }, [layers]);

  const toggleLayer = useCallback((id) => {
    setVisibleLayers(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  return (
    <div className="map-container">
      <div ref={mapContainer} className="map-wrapper" />
      {layers.length > 0 && (
        <LayerPanel 
          layers={layers} 
          visibleLayers={visibleLayers} 
          onToggleLayer={toggleLayer} 
        />
      )}
    </div>
  );
}
