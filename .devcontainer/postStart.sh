#!/usr/bin/env bash

printf "\e[36mpostStartCommand\e[0m\n"

printf "\e[34mSetup Backend environment...\e[0m\n"
pushd backend
uv python install 3.12
uv sync --dev
popd

printf "\e[34mSetup Frontend environment...\e[0m\n"
pushd frontend
# volta install node@22
# volta install pnpm git-cz
# npm install -g npm pnpm git-cz
# npm install
# rm -rfv node_modules package-lock.json .next
# npm cache clean --force
npm -g install npm git-cz
npm install
popd
