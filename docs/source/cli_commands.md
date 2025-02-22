# CLI (Command Line Interface)

The `seedfarmer` CLI provides the primary way to interface with the orchestration framework that manages a deploymement with AWS CodeSeeder.  It is used by CICD pipelines and individual users to:
 - deploy code (modules) via a deployment and manifest
 - fetch metadata related to currently deployed modules
 - destroy deployments
 - apply changes to deployments (via a GitOps model)

## Summary Commands
These commands are  structured in the format of:
```
seedfarmer <verb> <object> -<parameters>
```
### Top Level Commands:
```
> seedfarmer
Usage: seedfarmer [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  apply    Apply a deployment spec relative path for PROJECT
  destroy  Destroy PROJECT Deployment
  init     Initialize a new module in the proper structure
  list     List the relative data (module or deployment)
  remove   Top Level command to support removing module metadata
  store    Top Level command to support storing module metadata

```

The command listed above are used by the CLI, CICD implementations, and individual users.  There are no restrictions on the use of the commands (i.e users do have the ability to delete metadata and ssm data - so be careful!!) <br>

Each sub-command has help information related to how to use them.  Users typically will use the ```seedfarmer apply```, ```seedfarmer list``` and the ```seedfarmer destroy``` commands regularly.



### Example Walkthru - Deploy and Apply changes
The first time deploying, a deployment manifest must be created [see here](manifests.md).  The deployment manifests should be in the ```manifests``` directory.  All paths are relative to the project level (at all times).  For this example, we have a deployment manifest  located at ```manifests/walkthru/deployment.yaml``` and and modules manifests located at ```manifests/walkthru/<whatevername>```.  To check our deployment without apply any changes, our command would look like this:
```
seedfarmer apply manifests/walkthru/deployment.yaml --dry-run
```
None of these changes would be applied / deployed until we remove the `dry-run` flag:
```
seedfarmer apply manifests/walkthru/deployment.yaml
```

Once complete, we now have a deployment we can use.  After, if there are modules or groups we want to add OR remove (via altering the manifests), we can apply those changes once again:
```
seedfarmer apply manifests/walkthru/deployment.yaml
```
The CLI will take care of assessing: 
- which modules need to be redeployed due to changes
- which modules are up to date
- which modues or groups of modules need to be destroyed

Once we are finished with the deployment (ex. the ```local``` deployment), we can destroy all artifacts via:
```
seedfarmer destroy local
```

## HTTP Proxy Support
SeedFarmer does support the use of an HTTP-Proxy.  It is invoked via setting an environment variable in the context of where the CLI is being invoked.  SeedFarmer always leverages HTTPS for its boto3 invocations, so be sure to set the proper parameter.

The parameter we recognize is `HTTPS_PROXY` .  To set it for your runtime, you can do the folllowing (prior to invoking the CLI):
```code
export HTTPS_PROXY=https://<server>:<port>
```
For example, my server DNS is `mygreatserver.com` and is listening on port `8899` 
```code
export HTTPS_PROXY=http://mygreatserver.com:8899
```

In the above example, you will notice that my proxy is NOT over HTTPS....but the `HTTPS_PROXY` variable is being set.  This is correct, as SeedFarmer is leverging HTTPS for is invocation, regardless of your proxy configuration (it is up to you to determine the proper endpoint).

NOTE: if you run the SeedFarmer CLI with the `--debug` flag, you can see what the proxy is being configured for:

```code
[2023-05-11 12:54:48,392 | DEBUG | _service_utils.py: 32 | MainThread ] Proxies Configured: {'http': None, 'https': 'http://mygreatserver:8899'}
```
