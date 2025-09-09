# Banco-de-Dados---CRUD-SDA

Comandos úteis:
Para rodar o docker:  docker-compose up -d

Se já tiver outro PostgreSQL rodando na porta 5432 use: sudo systemctl stop postgresql 

Usar psql dentro do container : docker exec -it ponesaltitante_db psql -U hobbit -d ponesaltitante

docker-compose down -v 

docker-compose up -d 

Rodar a aplicação: uvicorn main:app --reload



pip install flask

Python 

Flask (framework web bem leve e fácil)

SQLite (banco de dados simples, já vem no Python)

HTML + Bootstrap (para interface da página)


Inserir → cadastra um novo quarto, cliente ou reserva.

Alterar → muda preço, tipo ou nome.

Pesquisar por nome → busca cliente ou tipo de quarto.

Remover → exclui cliente, quarto ou reserva.

Listar todos → mostra todos os registros de um tipo.

Exibir um → mostra detalhes de um objeto.

Relatório:

Relatório de Quartos:

Quantos quartos cadastrados.

Quantos ocupados / disponíveis.

Valor médio da diária.


Relatório de Clientes:

Quantos clientes cadastrados.



Relatório de Reservas:

Quantas reservas feitas.

Valor total em diárias reservadas.

Cliente que mais reservou.