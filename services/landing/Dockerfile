FROM node:20-alpine AS builder

RUN apk add --no-cache git

RUN corepack enable && \
    corepack prepare pnpm@latest --activate

WORKDIR /app
RUN git clone --depth 1 https://github.com/dabneyhovse/landing .

RUN pnpm install --frozen-lockfile
RUN pnpm run build

FROM nginx:alpine AS runtime

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
