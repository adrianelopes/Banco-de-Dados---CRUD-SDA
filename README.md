# Banco-de-Dados---CRUD-SDA

Comandos úteis:
Para rodar o docker:  docker-compose up -d

Se já tiver outro PostgreSQL rodando na porta 5432 use: sudo systemctl stop postgresql 

Usar psql dentro do container : docker exec -it ponesaltitante_db psql -U hobbit -d ponesaltitante

docker-compose down -v 

docker-compose up -d 

Rodar a aplicação: uvicorn main:app --reload
