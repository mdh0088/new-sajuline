# Nuxt.js 3 Frontend Dockerfile
FROM node:20-alpine as base

# Install dependencies for native modules
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Development stage
FROM base as development
RUN npm ci --include=dev
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Build stage
FROM base as builder
RUN npm ci --include=dev
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine as production
WORKDIR /app

# Install runtime dependencies only
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

# Copy built application
COPY --from=builder /app/.output .output

EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]