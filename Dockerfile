# Use versão compatível com seu package.json
FROM node:22-slim

WORKDIR /app

# Copie apenas os arquivos de dependência primeiro (melhora o cache)
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia o restante do projeto
COPY . .

# Gera o build de produção
RUN npm run build

# Instala servidor estático (serve)
RUN npm install -g serve

EXPOSE 3001

# Inicia o servidor estático servindo a pasta dist
CMD ["serve", "-s", "dist", "-l", "3001"]
