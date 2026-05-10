FROM node:22-slim AS builder
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/
RUN pnpm install --frozen-lockfile
COPY apps/web ./apps/web
RUN pnpm --filter web build

FROM node:22-slim
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY --from=builder /app/apps/web/package.json ./
COPY --from=builder /app/apps/web/node_modules ./node_modules
COPY --from=builder /app/apps/web/build ./build
EXPOSE 5173
CMD ["node", "build"]
