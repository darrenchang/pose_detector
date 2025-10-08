FROM node:24.3.0-alpine AS gui_builder
WORKDIR /ui-source
COPY pose-gui ./
RUN npm install
ENTRYPOINT ["npm", "run", "dev"]
