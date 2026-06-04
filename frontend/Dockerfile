# Stage 1: build
FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .

ARG API_URL=http://localhost:8000
ENV VITE_API_URL=$API_URL

RUN npm run build

# Stage 2: runtime
FROM node:20-alpine

WORKDIR /app

COPY --from=build /app/build ./build
COPY --from=build /app/package.json .
COPY --from=build /app/node_modules ./node_modules

ENV PORT=3000
ENV NODE_ENV=production
EXPOSE 3000

CMD ["node", "build/index.js"]
