FROM node:20-bookworm-slim AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY index.html vite.config.ts tsconfig.json ./
COPY src ./src
RUN npm run build

FROM node:20-bookworm-slim

ENV NODE_ENV=production
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY server.js ./server.js
COPY --from=build /app/dist ./dist

ENV PORT=8080
EXPOSE 8080

CMD ["node", "server.js"]
