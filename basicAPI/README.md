# Инструкция
1. Проект должен содержать 
```
./app/data/advice_docs  #предоставляется отдельно
./app/data/recipe_docs  #предоставляется отдельно
./app/data/classifier   #предоставляется отдельно
./app/data/embeder      #предоставляется отдельно
./app/my_schemas/
./app/repo/
./app/routers/
./app/services/
./app/system_prompts/   #предоставляется отдельно
./app/__init__.py
./app/config.py
./app/main.py
./app/schemas.py
./app/service.py
./.env                  #предоставляется отдельно 
./.dockerignore
./docker-compose.yaml
./Dockerfile
./requrements.txt
./locustfile.py
```
2. Если все на месте, то выполнить сборку 
```
docker compose up -d
```
3. После обращаться к приложению  
```
<http>://<host>:8000/<route>
```