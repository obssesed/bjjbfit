# Stage 1: Build
FROM node:22-alpine AS build

WORKDIR /app

# Instalamos dependencias primero para aprovechar caché
COPY package*.json ./
RUN npm install

# Copiamos el resto del código y construimos
COPY . .
RUN npm run build -- --configuration production

# Stage 2: Serve
FROM nginx:alpine

# Copiamos la configuración personalizada de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiamos los archivos estáticos generados por Angular
# Ajustamos la ruta según el output de Angular 21 (normalmente dist/frontend/browser)
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
