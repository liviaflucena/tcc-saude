# ---------- STAGE 1: build ----------
FROM node:22-alpine AS builder
WORKDIR /app

# Instala dependências primeiro (cache eficiente)
COPY package.json package-lock.json* ./
RUN npm ci

# Copia código e builda
COPY . .
RUN npm run build

# ---------- STAGE 2: nginx server ----------
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# Remove config default e adiciona a nossa
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia o build do Vite
COPY --from=builder /app/dist ./

# Saúde rápida
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost/ || exit 1

EXPOSE 80
