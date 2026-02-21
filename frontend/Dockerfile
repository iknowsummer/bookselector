FROM node:20-alpine AS builder

WORKDIR /app

# 依存関係インストール
COPY package.json package-lock.json ./
RUN npm ci

# ソースをコピーしてビルド
COPY . .

RUN npm run build

# --- runner ---
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --gid 1001 nodejs && \
    adduser --uid 1001 --ingroup nodejs --disabled-password nextjs

# standalone出力 + 静的ファイルをコピー
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
