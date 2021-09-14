# Documentation

## Things to Know

* Harvey will timeout git clone/pull after 300 seconds
* Harvey will timeout deploys after 30 minutes
* Harvey will shallow clone your project with the latest 10 commits
* Harvey expects the container name to match the GitHub repository name exactly, otherwise the healthcheck will fail

## Harvey Configuration

**Configuration Criteria**
* Each repo either needs a `harvey.json` file in the root directory stored in git or a `data` key passed into the webhook delivered to Harvey. This can be accomplished by using something like [workflow-webhook](https://github.com/distributhor/workflow-webhook) or another homegrown solution. (Harvey will always fallback to the `harvey.json` file if there is no `data` key present)
* You can specify one of `deploy` or `pull` as the pipeline type to run
* This file must follow proper JSON standards (start and end with `{ }`, contain commas after each item, no trailing commas, and be surrounded by quotes)
* Optional: `compose` value can be passed to specify the `docker-compose` file to be used. This key can also be used to specify a base file with additional compose files as overrides (eg: `docker-compose.yml -f docker-compose-prod.yml`).

**Example**
```javascript
{
    "pipeline": "deploy",
    "compose": "my-docker-compose-prod.yml"
}
```
