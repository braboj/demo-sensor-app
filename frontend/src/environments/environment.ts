// Default (development) environment. Replaced by environment.prod.ts in
// production builds via the fileReplacements in angular.json.
export const environment = {
  production: false,
  // Backend sensors endpoint. The dev backend is exposed on localhost:5000.
  apiUrl: 'http://localhost:5000/api/v1/sensors',
};
