import os
print(os.getcwd())
os.system('COMPOSE_PROJECT_NAME=mytelegrambot docker-compose -f ./dev_env/docker-compose.standalone.yml up -d')
