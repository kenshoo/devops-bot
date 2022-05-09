from pulumi_komponents.awslambda import AwsLambda, AwsLambdaArgs
from pulumi import Config

config = Config()

AwsLambda(AwsLambdaArgs(config))
