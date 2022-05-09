# lambda-python-template

This repository is a template for how to create easily [AWS lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) with full CI-CD support using [Pulumi infrastructure](https://www.pulumi.com/).
for now, we support 3 types of lambda trigger: s3 operations, scheduled and via API call. 

The project structure should be as following:

1. in the functions folder you should place all the lambda functions implementation code + requirements.txt file contains list of packages for the lambda code to install.
   please note that python runtime includes the boto3 library, so no need to install it.
2. in the _pulumi_resources_ folder place the following:
   - yaml configuration file (actually Pulumi stack) per lambda per environment.
   for example: if you want scheduled lambda on aws prod account and on aws lab account - you should create 2 yaml configuration files: Pulumi.scheduled_lambda_lab.yaml and Pulumi.scheduled_lambda_prod.yaml. in those files you should set the account with the field: _aws:account_.
   more details in configuration section.
   - the Pulumi.yaml file contains general configurations for all the Pulumi project.
   - in the _main.py_ file we actually create the component we need.  
3. in the invoke.py file you should describe the hierarchy of the lambda modules:
   - the var stacks_to_lambda_module is a dictionary with stack name key and LambdaModule value.
        the LambdaModule class get 2 parameters: 
     - packages - array of python packages that combine the lambda implementation code.
     - entry_point - the root file when the lambda handler function exist.
   - the var repo_name contains the name of your repository.
4. if you need vault integration, you can use the env.template file. place there your secrets path and those secrets will inject into lambda code in runtime as environment variables.

in order to get CI-CD support register to Skipper with stack: lambda.

## Configuration Details:

general configuration (relevant for all the trigger types):

| Name  | Required  | Type  | Values| Description  |
| ------------ | ------------ |------------ | ------------ | ------------ |
| general:project-name:  | Required  | string  |  | Defines the project name  |
| general:owner:  | Required  | string  | | Defines the owner mail of the created component |
| aws:account:  | Required  | string  | lab, prod, social | Defines the aws account where the components will create |
| aws:region:  | Required  | string  | us-east-1 | Defines the aws region where the components will create. *Required only for sns lambda type |
| lambda:name:  | Required  | string  |  | Defines the name of the lambda |
| lambda:role:  | Required  | string  |  | Defines the execution role for the lambda |
| lambda:handler:  | Required  | string  |  | Defines the lambda handler entry point |
| lambda:runtime:  | Required  | string  | python3.7, python3.8 | Defines the lambda code runtime |
| lambda:type:  | Required  | string  | s3, api_gateway, scheduled | Defines how to trigger the lambda |
| lambda:environment-variables:  |  | array[string]  | | Defines the environment variables for the lambda. aws have some [default vars](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html), and we also added the aws_account. vault secrets will also be available as env vars. |
| lambda:memory-size:  |  | int  | default value: 128 | Amount of memory in MB your Lambda Function can use at runtime |
| lambda:concurrent-executions:  |  | int  | default value: -1 | Amount of reserved concurrent executions for this lambda function. A value of 0 disables lambda from being triggered and -1 removes any concurrency limitations. |
| lambda:timeout:  |  | int  | default value: 3 | Amount of time your Lambda Function has to run in seconds. |

#### configurations for each trigger type:

1. scheduled

   | Name  | Required  | Type  | Values| Description  |
      | ------------ | ------------ |------------ | ------------ | ------------ |
   | scheduled:schedule-expression:  | Required | string  |  | The scheduling expression. For example, cron(0 20 * * ? *) or rate(5 minutes). |

2. s3

   | Name  | Required  | Type  | Values| Description  |
   | ------------ | ------------ |------------ | ------------ | ------------ |
   | s3:bucket:  | Required | string  |  | Defines the bucket to trigger the lambda on  |
   | s3:events:  | Required | array[string]  |  | Defines on which events to trigger the lambda  |
   | s3:filter-prefix: / s3:filter-suffix:  |  | string  |  | Defines the path of the trigger within the bucket   |

3. api_gateway
   
   | Name  | Required  | Type  | Values| Description  |
   | ------------ | ------------ |------------ | ------------ | ------------ |
   | api:description:  | | string  |  | Defines the description of the api  |
   | api:path-suffix:  | Required | string  |  | The last path segment of the API.  |
   | api:async-mode:  | | bool  |  | Defines if the API will work in async-mode  |

4. event_bridge

   | Name  | Required  | Type  | Values| Description  |
   | ------------ | ------------ |------------ | ------------ | ------------ |
   | event:event_pattern:  | Required | multi-line string  |  | Defines event pattern in event rule  |

4. sns

   | Name  | Required  | Type  | Values| Description  |
   | ------------ | ------------ |------------ | ------------ | ------------ |
   | sns:topic:  | Required | string  |  | ARN of the SNS topic to subscribe to.  |




