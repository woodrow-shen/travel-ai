FROM node:22-slim AS base
WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

FROM base AS development
CMD ["npm", "run", "dev"]

FROM base AS builder
RUN npm run build

FROM node:22-slim AS production
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
COPY --from=builder /app/public ./public
CMD ["npm", "start"]
