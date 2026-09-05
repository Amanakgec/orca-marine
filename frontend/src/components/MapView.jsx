import { useEffect, useRef, useState, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import LayerPanel from './LayerPanel';

export default function MapView({ layers }) {
  const mapContainer = useRef(null);
  const mapRef = useRef(null);
  const [visibleLayers, setVisibleLayers] = useState(new Set());

  // Initialize Map
  useEffect(() => {
    if (mapRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
      center: [78.9629, 15.5937], // Centered across the Indian Peninsula
      zoom: 5,
      attributionControl: false
    });

    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'bottom-right');
    map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right');

    map.on('load', () => {
      mapRef.current = map;
    });

    return () => {
      map.remove();
    };
  }, []);

  // Sync Layers & Auto-fly to queried region
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const syncLayers = () => {
      if (!map.isStyleLoaded()) return;

      const currentIds = layers.map(l => l.id);
      const style = map.getStyle();
      if (!style) return;

      const existingSources = style.sources || {};

      // 1. Remove old layers not in props
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
            paint['fill-outline-color'] = '#ffffff';
          } else if (layer.type === 'line') {
            paint['line-color'] = layer.style?.color || '#00d4ff';
            paint['line-width'] = layer.style?.width || 3;
            paint['line-opacity'] = layer.style?.opacity !== undefined ? layer.style.opacity : 0.9;
          } else if (layer.type === 'circle') {
            paint['circle-color'] = layer.style?.color || '#FF6B35';
            paint['circle-radius'] = layer.style?.width || 6;
            paint['circle-opacity'] = layer.style?.opacity !== undefined ? layer.style.opacity : 0.85;
            paint['circle-stroke-width'] = 1.5;
            paint['circle-stroke-color'] = '#ffffff';
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

          // Interactive popup
          map.on('click', sourceId, (e) => {
            if (!e.features || !e.features.length) return;
            const coordinates = e.lngLat;
            const properties = e.features[0].properties;

            let html = '<div style="font-size:12.5px; font-family: sans-serif; line-height:1.5;">';
            html += '<div style="font-weight: bold; margin-bottom: 6px; color: #00d4ff; border-bottom: 1px solid #334155; padding-bottom: 3px;">📍 ' + (layer.label || 'Feature Details') + '</div>';
            for (const [key, value] of Object.entries(properties)) {
              if (key !== 'coordinates' && key !== 'geometry') {
                const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                html += `<div><strong style="color:#94a3b8">${formattedKey}:</strong> ${value}</div>`;
              }
            }
            html += '</div>';

            new maplibregl.Popup({ closeButton: true, maxWidth: '320px' })
              .setLngLat(coordinates)
              .setHTML(html)
              .addTo(map);
          });

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

      // 3. Auto-fit camera to newly returned specific layers (excluding broad static IMBL)
      if (layers.length > 0) {
        let minLng = 180, minLat = 90, maxLng = -180, maxLat = -90;
        let found = false;

        const scanCoordinates = (coords) => {
          if (!Array.isArray(coords)) return;
          if (typeof coords[0] === 'number' && typeof coords[1] === 'number') {
            const [lng, lat] = coords;
            if (lng >= 64 && lng <= 96 && lat >= 5 && lat <= 26) {
              if (lng < minLng) minLng = lng;
              if (lng > maxLng) maxLng = lng;
              if (lat < minLat) minLat = lat;
              if (lat > maxLat) maxLat = lat;
              found = true;
            }
          } else {
            coords.forEach(scanCoordinates);
          }
        };

        // Prefer focused operational layers (PFZ, weather, routes, cyclone) over national boundary envelopes
        const targetLayers = layers.filter(l => !['imbl-layer', 'imbl-route-layer', 'mpa-layer'].includes(l.id));
        const layersToFit = targetLayers.length ? targetLayers : layers;

        layersToFit.forEach(l => {
          const features = l.data?.features || [];
          features.forEach(f => {
            if (f.geometry?.coordinates) {
              scanCoordinates(f.geometry.coordinates);
            }
          });
        });

        if (found) {
          map.fitBounds([[minLng, minLat], [maxLng, maxLat]], {
            padding: { top: 60, bottom: 60, left: 60, right: 60 },
            maxZoom: 9.5,
            duration: 1500
          });
        }
      }
    };

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
