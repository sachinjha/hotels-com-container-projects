FROM node:latest

# Create app directory
RUN mkdir -p /usr/src/ui
WORKDIR /usr/src/ui

# Install app dependencies
COPY package.json /usr/src/ui/
RUN npm install

# Bundle app source
COPY . /usr/src/ui

EXPOSE 9102
CMD [ "node", "app.js" ]