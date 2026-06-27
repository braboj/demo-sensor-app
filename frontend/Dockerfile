# Use the official Node.js image as the base image
FROM node:alpine

# Set the working directory inside the container
WORKDIR /app

# Copy all the files from the frontend directory to the working directory
COPY . .

# Install angular-cli globally
RUN npm install -g @angular/cli

# Install the dependencies (reproducible: requires committed package-lock.json)
RUN npm ci

# Expose the port that the application will run on
EXPOSE 4200

# Start the application in development mode
CMD ["ng", "serve", "--host", "0.0.0.0"]