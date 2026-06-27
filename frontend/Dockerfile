# --- Build stage: compile the Angular app ---
FROM node:22-alpine AS build

WORKDIR /app

# Install dependencies first for better layer caching (deps change rarely).
COPY package.json package-lock.json ./
RUN npm ci

# Build the production bundle (ng build defaults to the production config,
# which swaps in environment.prod.ts -> same-origin /api/sensors).
COPY . .
RUN npm run build

# --- Runtime stage: serve the static bundle via nginx ---
FROM nginx:1.27-alpine

# SPA routing + /api reverse proxy to the backend service.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# The Angular application builder emits static assets under browser/.
COPY --from=build /app/dist/sensor-app/browser /usr/share/nginx/html

EXPOSE 80
# nginx:alpine already runs `nginx -g 'daemon off;'` as its CMD.
