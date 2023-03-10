# Metrics Dashboard

This is the repo for the internal business intelligence dashboard. The app is built using the [Dash framework](https://plotly.com/dash/). Dash is built on top of Flask.

## Prerequisites
* python 3.7 or above
* pip installed: https://pip.pypa.io/en/stable/installing/
* AWS elastic beanstalk CLI: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html

## Set up
## Getting Started
Before getting started, ensure that you have npm installed on your local machine.

Copy the `.envrc-sample` file to a `.envrc` file and replace credentials with required values found in AWS.

Run
Install required python packages:
```bash
make venv
make cpenv
source env/bin/activate
make install
```

```bash
direnv allow .envrc
```

### Docker
To get up and running with metrics locally, simply copy the `.env-examp` file and fill in the `secrets`, then run the below docker commands to build and run the image
```zsh
vi .env # Fill in secrets

make build
docker run -it -p 80:8080 -v $PWD:/app --env-file=.env metrics
```
Thats it, you should now be able to access metrics at [http://localhost/](http://127.0.0.1:80/). Changes you make to the metrics code base whilst the image is running should update.

### Localhost
The below step already does the installation setup needed stage, which installs all the needed files
```bash
make install
```

Ensure you have a copy of the database locally - see the README for servalan for instructions. The preference is a copy of the production database so that the numbers make more sense.

## Codebase Structure
The folder structure of the codebase is as follows:
* Assets - CSS style sheet + other web assets like favicons, images, etc.
* Components - the tab structure of the app - each tab has its own file.
* Data - Functions that connect to the database and retrieve data for charting
* Graphs - Graphing functions for the app - each chart is generated by its own function


## Deployments
To deploy the docker image to elastic-beanstalk simply use these commands
```zsh
eb set env $(sed '/^[\n\#]/d' .env) # Copies your .env variables to AWS EB

eb deploy metrics-staging-docker
```
Alternatively you can just merge a pull request into develop or master to use CI/CD to deploy to staging/prod respectively.


To deploy the dashboard to the server, from your CLI run the commands:

```zsh
eb deploy ENVIRONMENT_NAME
```
To see the environments available:

```zsh
eb list
```

You will need appropriate CLI permissions - see mark to get this set up if required.

## Upgrade Python Packages

To upgrade the packages as part of the routine maintenance for the repo. We are using [Pip Upgrader][https://pypi.org/project/pip-upgrader/]

Use the following command.

For all packages:
```bash
make upgrade
```

For dev packages alone:
```bash
make upgrade-dev
```

For production packages alone:
```bash
make upgrade-prod
```
