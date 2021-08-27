# Documentation

## Things to Know

- Harvey will timeout builds at 30 minutes.
- Harvey will timeout git clone/pull after 180 seconds.
- Harvey will shallow clone your project with the latest 10 commits.
- Harvey pulls/clones from the master branch.
- When using the `compose` workflow, the container and/or service name must match the GitHub repository name exactly (alphanumeric characters only) to pass the healthcheck

## Harvey Configuration Examples

**Harvey Configuration Criteria**
- Each repo needs a `harvey.json` file in the root directory stored in git
- Each `harvey.json` config file will house information about your tests and build/deploy
- This file must follow proper JSON standards (start and end with `{ }`, contain commas after each item, no trailing commas, and be surrounded by quotes)

The following example will run a full pipeline (tests, build and deploy), tag it with a unique name based on the GitHub project. Provide the language and version for the test stage.

**Note:** All keys must be lowercase!

```javascript
{
    "pipeline": "full",
    "language": "php",
    "version": "7.4"
}
```

* Optional: `compose` value can be passed to specify the `docker-compose` file to use **if** building from a docker-compose file and hitting the `/pipelines/start/compose` endpoint (eg: `docker-compose.yml -f docker-compose-prod.yml`).
* Optional: `dockerfile` value can be passed to specify the name of the Dockerfile to build from (including path if not in root directory).

**Possible Pipeline Values**
- `full` - test, build, deploy stages will be run
- `deploy` - build, deploy stages will be run
- `test` - test stage will be run
- `pull` - pulls the project, this is useful if you have a custom deployment/testing workflow and simply want to pull the project changes

## Harvey Testing Examples

Each repository that uses Harvey's testing functionality must have a `harvey.sh` file in the root directory of the project. Below you'll find common examples of configuration files based on language.

Simply source the Harvey shell functions and add an or statement to each command you run to test if it succeeds or fails. Harvey will run all of your tests regardless of if they fail or succeed but only move on to the build/deploy stages if no tests fail. Harvey will output the entire set of logs for your tests which will show which commands passed or failed. Just add `|| harvey_fail` to the end of any command.

With Harvey, you can take almost any `.travis.yml` file and convert it straight across to a `harvey.sh` file.

**Shell Test Criteria**
- Each repo needs a `harvey.sh` file in the root directory stored in git
- Each `harvey.sh` file must have `#!/bin/sh` as the first line
- Each `harvey.sh` file must conform to shell scripting standards
- **DO NOT** use bash - sh is used as some of the testing docker containers do not have bash pre-installed

### Shell

```shell
#!/bin/sh
. /harvey/.harvey # Source the functions for Harvey

# TEST
shellcheck src/*.sh || harvey_fail
```

### Python

```shell
#!/bin/sh
. /harvey/.harvey # Source the functions for Harvey

# INSTALL
pip install pylint || harvey_fail
pip install pylint-exit || harvey_fail

# TEST
pylint pullbug/*.py || harvey_fail
pylint examples/*.py || harvey_fail
```

### PHP

```shell
#!/bin/sh
. /harvey/.harvey # Source the functions for Harvey

cd src || harvey_fail

# Use the following if you need to install composer in your test environment (if you do not already have a composer.phar file in your project)
# php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" || harvey_fail
# php -r "if (hash_file('sha384', 'composer-setup.php') === 'e0012edf3e80b6978849f5eff0d4b4e4c79ff1609dd1e613307e16318854d24ae64f26d17af3ef0bf7cfb710ca74755a') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;" || harvey_fail
# php composer-setup.php || harvey_fail
# php -r "unlink('composer-setup.php');" || harvey_fail

php composer.phar install --no-ansi --no-interaction --no-scripts --no-suggest --prefer-dist || harvey_fail

./vendor/bin/phplint . --exclude=vendor || harvey_fail
```

### Node

```shell
#!/bin/sh
. /harvey/.harvey # Source the functions for Harvey

# INSTALL
npm i || harvey_fail

# TEST
npx eslint index.js || harvey_fail
npx eslint lib/data-router.js || harvey_fail
```
