// Production environment. Uses a same-origin relative path so the static
// frontend can be served behind a reverse proxy that forwards /api to the
// backend (see the nginx setup in #17 / deployment in #29).
export const environment = {
  production: true,
  apiUrl: '/api/v1/sensors',
};
