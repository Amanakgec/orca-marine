import React, { useState } from 'react';
import { INDIA_TERRITORIES } from '../data/indiaTerritoriesGeo';

export default function IndiaTerritoryMap({ isOpen, onClose, onSelectTerritory }) {
  const [selectedId, setSelectedId] = useState('lakshadweep');
  const [hoveredItem, setHoveredItem] = useState(null);

  if (!isOpen) return null;

  const currentTerritory = INDIA_TERRITORIES.find(t => t.id === selectedId) || INDIA_TERRITORIES[0];

  const handleSelect = (terr) => {
    setSelectedId(terr.id);
    if (onSelectTerritory) {
      onSelectTerritory(terr);
    }
  };

  return (
    <div className="territory-modal-overlay" onClick={onClose}>
      <div className="territory-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="territory-modal-header">
          <div className="territory-header-title">
            <span className="territory-header-icon">🗺️</span>
            <div>
              <h3>Indian Maritime &amp; Island Territories</h3>
              <p>Mainland Coastlines · Lakshadweep (SW) · Andaman &amp; Nicobar (SE)</p>
            </div>
          </div>
          <button className="territory-close-btn" onClick={onClose} type="button" title="Close Navigator">✕</button>
        </div>

        {/* Territory Selector Quick Tabs */}
        <div className="territory-tabs">
          {INDIA_TERRITORIES.map((terr) => (
            <button
              key={terr.id}
              type="button"
              className={`territory-tab-btn ${selectedId === terr.id ? 'active' : ''}`}
              onClick={() => handleSelect(terr)}
            >
              {terr.id === 'lakshadweep' ? '🏝️ Lakshadweep (SW)' : 
               terr.id === 'andaman-nicobar' ? '🌴 Andaman & Nicobar (SE)' :
               terr.name.split('—')[1]?.trim() || terr.name}
            </button>
          ))}
        </div>

        <div className="territory-body-grid">
          {/* Responsive SVG Map with explicit bounds encompassing SW & SE Islands */}
          <div className="territory-svg-container">
            <svg
              viewBox="0 0 680 600"
              className="territory-svg"
              preserveAspectRatio="xMidYMid meet"
            >
              <defs>
                <linearGradient id="mainlandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#1e3a5f" />
                  <stop offset="100%" stopColor="#0e2a4a" />
                </linearGradient>
                <linearGradient id="selectedGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#00d4ff" />
                  <stop offset="100%" stopColor="#0066ff" />
                </linearGradient>
                <filter id="glowEffect" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>

              {/* Ocean Basin Backgrounds */}
              <rect x="0" y="0" width="680" height="600" fill="#071220" rx="12" />

              {/* Coordinate Grid Guides */}
              <g stroke="#1a2d48" strokeWidth="0.8" strokeDasharray="3 3">
                <line x1="60" y1="120" x2="640" y2="120" />
                <line x1="60" y1="240" x2="640" y2="240" />
                <line x1="60" y1="360" x2="640" y2="360" />
                <line x1="60" y1="480" x2="640" y2="480" />
                <line x1="160" y1="40" x2="160" y2="560" />
                <line x1="320" y1="40" x2="320" y2="560" />
                <line x1="480" y1="40" x2="480" y2="560" />
              </g>

              {/* Water Basin Titles */}
              <text x="110" y="340" fill="#204060" fontSize="14" fontWeight="700" letterSpacing="3">ARABIAN SEA</text>
              <text x="400" y="310" fill="#204060" fontSize="14" fontWeight="700" letterSpacing="3">BAY OF BENGAL</text>
              <text x="520" y="440" fill="#1b3650" fontSize="12" fontWeight="700" letterSpacing="2">ANDAMAN SEA</text>

              {/* Simplified Geometric Mainland India Outline */}
              <path
                d="M 230 60
                   L 260 50 L 300 70 L 340 70 L 370 100 L 390 125
                   L 460 140 L 490 160 L 480 185 L 430 190 L 405 210
                   L 410 240 L 390 280 L 370 340 L 350 410 L 330 460
                   L 320 510 L 310 525 L 300 510 L 285 450 L 265 370
                   L 255 310 L 235 270 L 205 260 L 190 275 L 180 260
                   L 200 220 L 190 170 L 220 120 Z"
                fill={selectedId.startsWith('mainland') ? "url(#selectedGrad)" : "url(#mainlandGrad)"}
                stroke="#00d4ff"
                strokeWidth={selectedId.startsWith('mainland') ? "2" : "1"}
                opacity={selectedId.startsWith('mainland') ? 0.9 : 0.65}
                className="map-territory-path"
                onClick={() => handleSelect(INDIA_TERRITORIES[0])}
                onMouseEnter={() => setHoveredItem("Mainland India")}
                onMouseLeave={() => setHoveredItem(null)}
              />

              {/* West Coast Highlights */}
              <path
                d="M 200 220 L 205 260 L 235 270 L 255 310 L 265 370 L 285 450 L 310 525"
                fill="none"
                stroke={selectedId === 'mainland-west' ? "#00ffcc" : "#38bdf8"}
                strokeWidth={selectedId === 'mainland-west' ? "4" : "2"}
                strokeLinecap="round"
                className="interactive-coast"
                onClick={() => handleSelect(INDIA_TERRITORIES[0])}
              />

              {/* East Coast Highlights */}
              <path
                d="M 430 190 L 410 240 L 390 280 L 370 340 L 350 410 L 330 460 L 310 525"
                fill="none"
                stroke={selectedId === 'mainland-east' ? "#00ffcc" : "#38bdf8"}
                strokeWidth={selectedId === 'mainland-east' ? "4" : "2"}
                strokeLinecap="round"
                className="interactive-coast"
                onClick={() => handleSelect(INDIA_TERRITORIES[1])}
              />

              {/* ========================================================= */}
              {/* LAKSHADWEEP ISLANDS (South-West Arabian Sea)               */}
              {/* Lat 8°-12°N, Lon 71°-74°E -> Canvas Position (~x: 180-230, y: 440-520) */}
              {/* ========================================================= */}
              <g 
                className={`island-cluster ${selectedId === 'lakshadweep' ? 'active-cluster' : ''}`}
                onClick={() => handleSelect(INDIA_TERRITORIES[2])}
                onMouseEnter={() => setHoveredItem("Lakshadweep Archipelago (Arabian Sea SW)")}
                onMouseLeave={() => setHoveredItem(null)}
                style={{ cursor: 'pointer' }}
              >
                {/* Visual Highlight Boundary Box */}
                <rect
                  x="180"
                  y="435"
                  width="70"
                  height="105"
                  rx="8"
                  fill={selectedId === 'lakshadweep' ? "rgba(0, 212, 255, 0.2)" : "rgba(14, 42, 74, 0.4)"}
                  stroke={selectedId === 'lakshadweep' ? "#00d4ff" : "#204060"}
                  strokeWidth="1.5"
                  strokeDasharray="4 2"
                />

                {/* Island Nodes: Amini, Kavaratti, Agatti, Andrott, Minicoy */}
                <circle cx="210" cy="455" r="5" fill="#00ffcc" filter="url(#glowEffect)" /> {/* Amini/Kadmat */}
                <circle cx="202" cy="470" r="4.5" fill="#00ffcc" /> {/* Agatti */}
                <circle cx="215" cy="480" r="6" fill="#00d4ff" filter="url(#glowEffect)" /> {/* Kavaratti Capital */}
                <circle cx="232" cy="482" r="4.5" fill="#00ffcc" /> {/* Andrott */}
                <circle cx="225" cy="525" r="5.5" fill="#00ffcc" /> {/* Minicoy Southern */}

                {/* Island Labels */}
                <text x="215" y="425" textAnchor="middle" fill="#00d4ff" fontSize="11" fontWeight="700" letterSpacing="0.5">
                  LAKSHADWEEP
                </text>
                <text x="215" y="437" textAnchor="middle" fill="#94a3b8" fontSize="9">
                  (Arabian Sea · SW)
                </text>
                <text x="228" y="495" fill="#ffffff" fontSize="9" fontWeight="600">Kavaratti</text>
                <text x="236" y="530" fill="#ffffff" fontSize="8.5">Minicoy</text>
              </g>

              {/* ========================================================= */}
              {/* ANDAMAN & NICOBAR ISLANDS (South-East Bay of Bengal)      */}
              {/* Lat 6°-14°N, Lon 92°-94°E -> Canvas Position (~x: 520-560, y: 330-550) */}
              {/* ========================================================= */}
              <g 
                className={`island-cluster ${selectedId === 'andaman-nicobar' ? 'active-cluster' : ''}`}
                onClick={() => handleSelect(INDIA_TERRITORIES[3])}
                onMouseEnter={() => setHoveredItem("Andaman & Nicobar Archipelago (Bay of Bengal SE)")}
                onMouseLeave={() => setHoveredItem(null)}
                style={{ cursor: 'pointer' }}
              >
                {/* Visual Highlight Boundary Box */}
                <rect
                  x="510"
                  y="320"
                  width="70"
                  height="235"
                  rx="8"
                  fill={selectedId === 'andaman-nicobar' ? "rgba(0, 212, 255, 0.2)" : "rgba(14, 42, 74, 0.4)"}
                  stroke={selectedId === 'andaman-nicobar' ? "#00d4ff" : "#204060"}
                  strokeWidth="1.5"
                  strokeDasharray="4 2"
                />

                {/* Andaman Group (North, Middle, South Andaman) */}
                <ellipse cx="538" cy="350" rx="4.5" ry="9" fill="#00ffcc" /> {/* North Andaman / Diglipur */}
                <ellipse cx="540" cy="375" rx="5" ry="12" fill="#00ffcc" /> {/* Middle Andaman */}
                <circle cx="552" cy="390" r="4.5" fill="#38bdf8" /> {/* Havelock / Swaraj Dweep */}
                <ellipse cx="542" cy="405" rx="6" ry="14" fill="#00d4ff" filter="url(#glowEffect)" /> {/* Port Blair (South) */}

                {/* 10 Degree Channel Divider */}
                <line x1="515" y1="440" x2="575" y2="440" stroke="#334155" strokeWidth="1" strokeDasharray="2 2" />
                <text x="545" y="437" textAnchor="middle" fill="#64748b" fontSize="7.5">10° Channel</text>

                {/* Nicobar Group (Car Nicobar, Nancowry, Great Nicobar) */}
                <circle cx="545" cy="460" r="5" fill="#00ffcc" /> {/* Car Nicobar */}
                <circle cx="548" cy="485" r="4" fill="#00ffcc" /> {/* Nancowry */}
                <ellipse cx="555" cy="515" rx="7" ry="12" fill="#00d4ff" filter="url(#glowEffect)" /> {/* Great Nicobar */}
                <circle cx="558" cy="532" r="3" fill="#ff4d4d" /> {/* Indira Point (Southern Tip) */}

                {/* Territory Labels */}
                <text x="545" y="305" textAnchor="middle" fill="#00d4ff" fontSize="11" fontWeight="700" letterSpacing="0.5">
                  ANDAMAN &amp; NICOBAR
                </text>
                <text x="545" y="317" textAnchor="middle" fill="#94a3b8" fontSize="9">
                  (Bay of Bengal · SE)
                </text>
                <text x="554" y="410" fill="#ffffff" fontSize="9" fontWeight="600">Port Blair</text>
                <text x="566" y="520" fill="#ffffff" fontSize="8.5">Great Nicobar</text>
              </g>

              {/* Tooltip Overlay */}
              {hoveredItem && (
                <g transform="translate(20, 565)">
                  <rect x="0" y="0" width="360" height="26" rx="6" fill="rgba(10, 22, 40, 0.9)" stroke="#00d4ff" strokeWidth="1" />
                  <text x="12" y="17" fill="#00d4ff" fontSize="11" fontWeight="600">📍 {hoveredItem}</text>
                </g>
              )}
            </svg>
          </div>

          {/* Territory Detail & Action Panel */}
          <div className="territory-info-card">
            <div className="territory-badge-row">
              <span className="territory-type-badge">{currentTerritory.badge}</span>
              <span className="territory-sea-badge">🌊 {currentTerritory.sea}</span>
            </div>

            <h4 className="territory-name">{currentTerritory.name}</h4>
            <p className="territory-desc">{currentTerritory.description}</p>

            <div className="territory-meta-box">
              <div className="meta-item">
                <span className="meta-label">🌐 Geo Coordinates</span>
                <span className="meta-value">{currentTerritory.coordinates}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">⚓ Key Ports / Anchorages</span>
                <span className="meta-value">{currentTerritory.ports.join(' · ')}</span>
              </div>
            </div>

            {/* If Island, list sub-islands */}
            {currentTerritory.islands && (
              <div className="island-nodes-list">
                <span className="nodes-title">🏝️ Surveyed Island Clusters:</span>
                <div className="nodes-grid">
                  {currentTerritory.islands.map((isl, idx) => (
                    <div key={idx} className="node-chip">
                      <strong>{isl.name.split('(')[0]}</strong>
                      <span className="node-sub">{isl.type}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              className="territory-fly-btn"
              onClick={() => {
                if (onSelectTerritory) onSelectTerritory(currentTerritory);
                onClose();
              }}
              type="button"
            >
              🚀 Fly Map Camera to {currentTerritory.name.split('(')[0]}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
