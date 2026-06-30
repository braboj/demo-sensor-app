// Default (development) environment. Replaced by environment.prod.ts in
// production builds via the fileReplacements in angular.json.
export const environment = {
  production: false,
  // Backend sensors endpoint. The dev backend is exposed on localhost:5000.
  apiUrl: 'http://localhost:5000/api/v1/sensors',
  // Grafana "Sensor Readings" dashboard (provisioned in docker compose on
  // :3000). Empty disables the in-app link; charting lives in Grafana.
  grafanaUrl: 'http://localhost:3000/d/sensor-readings/sensor-readings',
};
