FROM node:22-alpine

RUN npm i -g pnpm@9.0.0


# set working directory at repo root
WORKDIR /app

COPY package.json pnpm-workspace.yaml pnpm-lock.yaml turbo.json ./

COPY apps ./apps

COPY packages ./packages


RUN pnpm install

# move to frontend app
WORKDIR /app/apps/http-server

EXPOSE 4000

CMD [ "pnpm", "run", "start" ]