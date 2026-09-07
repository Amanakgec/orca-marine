// India Maritime & Island Territories Spatial Registry
// Encompassing Mainland Coastal Sectors, Lakshadweep (SW Arabian Sea), and Andaman & Nicobar (SE Bay of Bengal)

export const INDIA_TERRITORIES = [
  {
    id: "mainland-west",
    name: "Mainland — West Coast (Arabian Sea)",
    category: "Mainland",
    sea: "Arabian Sea",
    center: [72.8, 16.5],
    zoom: 6,
    badge: "🌊 Western Continental Shelf",
    description: "Extends from Gulf of Kutch to Cape Comorin. High upwelling during SW monsoon, dense pelagic fisheries (Mackerel, Sardines, Bombay Duck).",
    ports: ["Kandla", "Veraval", "Mumbai", "Mormugao", "Mangaluru", "Kochi"],
    coordinates: "68.5°E - 77.5°E, 8.0°N - 23.5°N"
  },
  {
    id: "mainland-east",
    name: "Mainland — East Coast (Bay of Bengal)",
    category: "Mainland",
    sea: "Bay of Bengal",
    center: [82.5, 15.5],
    zoom: 6,
    badge: "🌀 Coromandel & Deltaic Coast",
    description: "Extends from Sundarbans to Gulf of Mannar. Major riverine discharges (Ganges, Godavari, Krishna), cyclone-prone shelf, rich demersal grounds.",
    ports: ["Kolkata", "Paradip", "Visakhapatnam", "Chennai", "Cuddalore", "Tuticorin"],
    coordinates: "78.0°E - 89.5°E, 8.5°N - 22.5°N"
  },
  {
    id: "lakshadweep",
    name: "Lakshadweep Islands (South-West)",
    category: "Island Archipelago",
    sea: "Arabian Sea (SW)",
    center: [72.64, 10.56],
    zoom: 7.5,
    badge: "🏝️ Coral Atoll Union Territory",
    description: "Archipelago of 36 coral atolls and submerged banks in South-West Arabian Sea. Premier oceanic pole-and-line Skipjack Yellowfin Tuna fishery.",
    ports: ["Kavaratti", "Agatti", "Minicoy", "Andrott", "Amini"],
    coordinates: "71.5°E - 74.2°E, 8.2°N - 12.5°N",
    islands: [
      { name: "Kavaratti (Capital & Operations Base)", coords: [72.64, 10.56], type: "Administrative Capital" },
      { name: "Agatti Island & Lagoon", coords: [72.18, 10.85], type: "Airport & Tuna Center" },
      { name: "Minicoy Island (Maliku Atoll)", coords: [73.05, 8.28], type: "Southern 9-Degree Channel" },
      { name: "Andrott Island (East Barrier)", coords: [73.68, 10.82], type: "Lagoon Anchorage" },
      { name: "Amini & Kadmat Atolls", coords: [72.73, 11.12], type: "Coral Reef Reserve" }
    ]
  },
  {
    id: "andaman-nicobar",
    name: "Andaman & Nicobar Islands (South-East)",
    category: "Island Archipelago",
    sea: "Bay of Bengal & Andaman Sea (SE)",
    center: [92.74, 11.66],
    zoom: 6.8,
    badge: "🌿 Deep-Sea Ocean Ridge",
    description: "Archipelago of 572 tropical islands forming India's eastern maritime sentinel in the Andaman Sea. Dominates the Malacca Strait approaches with massive 600,000 sq km EEZ.",
    ports: ["Port Blair", "Havelock", "Car Nicobar", "Campbell Bay"],
    coordinates: "92.0°E - 94.2°E, 6.5°N - 14.0°N",
    islands: [
      { name: "South Andaman (Port Blair)", coords: [92.74, 11.66], type: "Major Seaport & Naval Command" },
      { name: "Havelock Island (Swaraj Dweep)", coords: [92.98, 12.00], type: "Bio-Reserve & Tuna Grounds" },
      { name: "North & Middle Andaman (Diglipur)", coords: [92.98, 13.26], type: "Continental Shelf Fishery" },
      { name: "Car Nicobar (Ten Degree Channel)", coords: [92.78, 9.16], type: "Tribal Reserve & Early Warning" },
      { name: "Great Nicobar (Indira Point)", coords: [93.85, 6.95], type: "Southernmost Tip (6°N)" }
    ]
  }
];

// Helper to convert islands into GeoJSON FeatureCollection for MapLibre rendering
export function getTerritoryGeoJSON() {
  const features = [];

  INDIA_TERRITORIES.forEach(terr => {
    // If archipelago, add individual island markers
    if (terr.islands) {
      terr.islands.forEach(isl => {
        features.push({
          type: "Feature",
          properties: {
            name: isl.name,
            territory: terr.name,
            type: isl.type,
            sea: terr.sea
          },
          geometry: {
            type: "Point",
            coordinates: isl.coords
          }
        });
      });
    }

    // Add territory center hub
    features.push({
      type: "Feature",
      properties: {
        name: terr.name,
        badge: terr.badge,
        category: terr.category,
        sea: terr.sea,
        ports: terr.ports.join(", ")
      },
      geometry: {
        type: "Point",
        coordinates: terr.center
      }
    });
  });

  return {
    type: "FeatureCollection",
    features
  };
}
