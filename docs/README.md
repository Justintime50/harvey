# Documentation

## Things to Know

* Harvey will timeout git clone/pull after 300 seconds
* Harvey will timeout deploys after 30 minutes
* Harvey will shallow clone your project with the latest 10 commits
* Harvey expects the container name to match the GitHub repository name exactly, otherwise the healthcheck will fail

## Harvey Configuration Examples

**Harvey Configuration Criteria**
* Each repo needs a `harvey.json` file in the root directory stored in git
* You can specify one of `deploy` or `pull` as the pipeline type to run
* This file must follow proper JSON standards (start and end with `{ }`, contain commas after each item, no trailing commas, and be surrounded by quotes)
* Optional: `compose` value can be passed to specify the `docker-compose` file to be used. This key can also be used to specify a base file with additional compose files as overrides (eg: `docker-compose.yml -f docker-compose-prod.yml`).

```javascript
{
    "pipeline": "deploy",
    "compose": "docker-compose.yml -f docker-compose-prod.yml"
}
```
