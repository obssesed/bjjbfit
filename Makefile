# Comandos de Docker para BJJFit

.PHONY: up down restart build logs shell-backend migrate superuser clean

# Levantar el proyecto en segundo plano
up:
	docker-compose up -d

# Bajar el proyecto
down:
	docker-compose down

# Reiniciar los servicios
restart:
	docker-compose restart

# Construir las imágenes desde cero
build:
	docker-compose build --no-cache

# Ver los logs en tiempo real
logs:
	docker-compose logs -f

# Acceder a la terminal del backend
shell-backend:
	docker-compose exec backend /bin/sh

# Ejecutar migraciones manualmente
migrate:
	docker-compose exec backend python manage.py migrate

# Crear un superusuario
superuser:
	docker-compose exec backend python manage.py createsuperuser

# Limpieza total (Borra volúmenes y base de datos)
clean:
	docker-compose down -v --rmi all
