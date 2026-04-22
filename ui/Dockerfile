FROM node:22-alpine

ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN corepack enable && corepack prepare pnpm@10 --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --prefer-frozen-lockfile || pnpm install

COPY . .

EXPOSE 3000
CMD ["pnpm", "dev", "-p", "3000"]
