#!/bin/bash

# Exit immediately if any command fails
set -e

# Function to print usage information
usage() {
  echo "Usage: $0 <folder_name> <commit_hash> <env>"
  exit 1
}

# Function to check and clone/pull the repository
update_repo() {
  echo "##############################"
  echo "Updating repository"
  echo "##############################"
  if [ ! -d "$FOLDER_NAME" ]; then
    git clone "git@github.com:alethainc/spider-release-zone-ai.git" -b "$ENV" "$FOLDER_NAME"
    cd "$FOLDER_NAME"
  else
    cd "$FOLDER_NAME" || exit 1
    git checkout "$ENV"
    git pull origin "$ENV"
  fi
}

# Function to build and push Docker image
build_image() {
  echo "##############################"
  echo "Building Docker image"
  echo "##############################"
  docker build --no-cache -t "$IMAGE_NAME" .
  #docker push "$IMAGE_NAME"
}

# Function to stop and remove old Docker container
stop_and_remove_container() {
  echo "##############################"
  echo "Stopping and removing old Docker container"
  echo "##############################"
  if docker ps -a --format '{{.Names}}' | grep -Eq "^$CONTAINER_NAME$"; then
    echo "Stopping existing container: $CONTAINER_NAME"
    docker stop "$CONTAINER_NAME" || true
    echo "Removing existing container: $CONTAINER_NAME"
    docker rm "$CONTAINER_NAME" || true
  else
    echo "No existing container named $CONTAINER_NAME to stop or remove."
  fi
}

# Function to run the new Docker container
run_new_container() {
  echo "##############################"
  echo "Running new Docker container"
  echo "##############################"
  docker run -d -p 5000:5000 --name "$CONTAINER_NAME" --network my-network --env-file /home/ec2-user/env/.env "$IMAGE_NAME"
}

# Function to remove unused images
rm_images() {
  echo "##############################"
  echo "Removing unused Docker images"
  echo "##############################"
  docker system prune -a -f || true
}


# Ensure correct number of arguments
if [ $# -ne 3 ]; then
  usage
fi

FOLDER_NAME="$1"
COMMIT_HASH="$2"
ENV="$3"
CONTAINER_NAME="$FOLDER_NAME"
IMAGE_NAME=$1:$COMMIT_HASH
echo "$CONTAINER_NAME, $COMMIT_HASH, $ENV"

# Update repository
update_repo

# Build Docker image
build_image

# Stop and remove old Docker container
stop_and_remove_container

# Run new Docker container
run_new_container

# Remove unused images
rm_images