
This is a demo template. A acceptable workflow file should be <custom-name>.yaml or 
<custom-name>.yml

# Secrets in the repository: DOCKERHUB_PATOKEN DOCKERHUB_USERNAME and/or GH_PAT
# if denied: requested access to the resource is denied, it might need to delete the existing image from DockeHub
name: Docker Image CI for Github
on:
  push:
    branches: ['learning', 'main']
#    paths:
#      - 'dockerdir/Dockerfile'
# If at least one path matches a pattern in the paths filter, the workflow runs.
# The paths and paths-ignore keywords accept glob patterns that use the * and ** wildcard characters to match more than one path name. 
env:
# YAML is just markup, not code. You can't expect a generalised behaviour of evaluating any kind of expression.Template expression variables (${{ var.variable }}) get processed at compile time. Macro syntax variables ($(var)) get processed during runtime before a task runs.
  DOCKERFILE_DIR: ./dockerdir/
  DOCKER_TAG_NAME: 0.1
  GITHUB_REGISTRY: ghcr.io
  DOCKER_IMAGE_NAME: ${{ github.repository }}
  # the value: zhaohuiwang/make-poetry-git

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    permissions:
      packages: write
      contents: read
      attestations: write
      id-token: write
    steps:
      - name: Check out the repo
        uses: actions/checkout@v4
      # Infom to show current working dir, content, one vairable value (troubleshooting) 

      - name: display current directory
        run: |
          pwd
          ls -a
          echo "DOCKER_IMAGE_NAME variable: $DOCKER_IMAGE_NAME"
      ##### Build, publish to GitHub
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.GITHUB_REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and Push the Image
        run: |
          docker build --tag ${{ env.GITHUB_REGISTRY }}/${{ env.DOCKER_IMAGE_NAME }}:${{ env.DOCKER_TAG_NAME }} ${{ env.DOCKERFILE_DIR }}
          docker push ${{ env.GITHUB_REGISTRY }}/${{ env.DOCKER_IMAGE_NAME }}:${{ env.DOCKER_TAG_NAME }}
############### 
# if you like to published to DockerHub as well here, 
# first, bring the "Get Repository Name" and "login to DockerHub registry" up front,
# second, put this into the env DOCKERHUB_REGISTRY: docker.io
# lastly, re tag the docker image and published to DockeHub with the following script

#          docker tag ${{ env.GITHUB_REGISTRY }}/${{ env.DOCKER_IMAGE_NAME }}:${{ env.DOCKER_TAG_NAME }} ${{ secrets.DOCKERHUB_USERNAME }}/${{ env.REPOSITORY_NAME }}:${{ env.DOCKER_TAG_NAME }}
#          docker push ${{ env.DOCKERHUB_REGISTRY }}/${{ secrets.DOCKERHUB_USERNAME }}/${{ env.REPOSITORY_NAME }}:${{ env.DOCKER_TAG_NAME }}
###############
          
      ##### Build, publish to DockerHub
      ## Username maybe different between GitHub and DockerHub, we need to parse DockerHub usename and project name (uses the repository name here). to define a environment variable and write it to the GITHUB_ENV environment file.
      - name: Get Repository Name
        run: |
          echo "REPOSITORY_NAME=`basename ${{ github.repository }}`" >> $GITHUB_ENV
      # or
      # echo "REPOSITORY_NAME=${GITHUB_REPOSITORY#*/}" >> $GITHUB_ENV
      - name: login to DockerHub registry
        uses: docker/login-action@v3
        with:
        # first you need to specify your DOCKERHUB_USERNAME and DOCKERHUB_PATOKEN inside your repos secrets.
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_PATOKEN }}
      - name: Build and Push the Docker Image to DockerHub Registry
        uses: docker/build-push-action@v5
        with:
          context: dockerdir/
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/${{ env.REPOSITORY_NAME }}:${{ env.DOCKER_TAG_NAME }}

# Every time there is a new code is pushed into the repository it is going to rebuild the container image and publish it.

# actions/checkout@v4 -- This action checks-out (clone) your repository under $GITHUB_WORKSPACE, so your workflow can access it. (see GitHub Marketplace - Tools from the community and partners to simplify tasks and automate processes. Note use instead of run)
# login Github build iamge and push to Github container registry, build and push the image to GitHub packages repository

# GitHub Repositories > Actions > All workflows Click to see job/name and all the loggs

# both OK
# docker build --tag ghcr.io/zhaohuiwang/make-poetry-git:latest ./dockerdir/
# docker build ./dockerdir/ --tag ghcr.io/zhaohuiwang/make-poetry-git:latest

# The following code to login to GitHub Container Registry does not work for me
# docker login --username zhaohuiwang --password ${{ secrets.GH_PAT }} ghcr.io

# add permissions for workflows error "denied: installation not allowed to Write organization package Error: Process completed with exit code 1.""
# https://docs.github.com/en/actions/use-cases-and-examples/publishing-packages/publishing-docker-images#publishing-images-to-github-packages

# GitHub Actions includes a collection of variables called contexts (e.g. github.repository) and a similar collection of variables called default variables (e.g. GITHUB_REPOSITORY). 
# Reference custom variables defined in the workflow.	${{ env.MY_VARIABLE }}
# Reference information about the workflow run and the event that triggered the run.	${{ github.repository }}
# The default environment variables that GitHub sets are available to every step in a workflow but exist only on the runner that is executing your job. You can use most contexts at any point in your workflow, including when default variables would be unavailable. For example, you can use contexts with expressions to perform initial processing before the job is routed to a runner for execution; this allows you to use a context with the conditional if keyword to determine whether a step should run. Once the job is running, you can also retrieve context variables from the runner that is executing the job, such as runner.os.
