FROM node:18

WORKDIR /app

# Копируем package.json и package-lock.json для установки зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

COPY . .

EXPOSE 3000

# Запускаем dev-сервер
CMD ["npm", "start"]
