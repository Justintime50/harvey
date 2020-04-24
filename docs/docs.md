# Documentation

## Harvey Configuration Examples

Each repository that uses Harvey must have a `harvey.sh` file in the root directory of the project. Below you'll find common examples of configuration files based on language.

With Harvey, you can take almost any `.travis.yml` file and convert it straight across to a `harvey.sh` file.

**Harvey Configuration Criteria**
- Each repo needs a `.harvey` file in their root directory stored in git
- Each `.harvey` config file will house information about your tests and build
- This file must follow proper JSON standards (start and end with `{ }`, contain commans after each item, and be surrounded by quotes)

The following example will run a full pipeline (tests, build and deploy), tag it with a unique name, and provide the data for the test stage:

```javascript
{
    "pipeline": "full",
    "tag": "justin-test",
    "data": {
        "project": "justinpaulhammond.com",
        "language": "php",
        "version": "7.4"
    }
}
```

**Shell Test Criteria**
- Each repo needs a `harvey.sh` file in their root directory stored in git
- Each `harvey.sh` file must have `#!/bin/sh` as the first line
- Each `harvey.sh` file must conform to shell scripting standards (DO NOT use bash, sh is used as some of the testing docker containers do not have bash pre-installed)
- Each project is stored in the `project` directory in your testing Docker container. Either `cd project` before running your commands or specify this in your path when running commands that reference files.

### Shell

```shell
#!/bin/sh

# TEST
shellcheck project/src/*.sh
```

### Python

```shell
#!/bin/sh

# INSTALL
pip install pylint > /dev/null 2>&1 && printf "%s\n" "Pylint installed"
pip install pylint-exit > /dev/null 2>&1 && printf "%s\n" "Pylint exit installed"

# TEST
pylint project/pullbug/*.py --rcfile=.pylintrc || pylint-exit $?
if [ $? -ne 0 ]; then
  echo "An error occurred while running pylint." >&2
  exit 1
fi

pylint project/examples/*.py --rcfile=.pylintrc || pylint-exit $?
if [ $? -ne 0 ]; then
  echo "An error occurred while running pylint." >&2
  exit 1
fi
```

### PHP

```shell
#!/bin/sh

cd project

cd src

# Use the following if you need to install composer in your test environment (if you do not already have a composer.phar file in your project)
# php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
# php -r "if (hash_file('sha384', 'composer-setup.php') === 'e0012edf3e80b6978849f5eff0d4b4e4c79ff1609dd1e613307e16318854d24ae64f26d17af3ef0bf7cfb710ca74755a') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;"
# php composer-setup.php
# php -r "unlink('composer-setup.php');"

php composer.phar install --no-ansi --no-interaction --no-scripts --no-suggest --prefer-dist

./vendor/bin/phplint . --exclude=vendor
```

### Node

```shell
#!/bin/sh

cd project

# INSTALL
npm i

# TEST
npx eslint index.js
npx eslint lib/data-router.js
```
