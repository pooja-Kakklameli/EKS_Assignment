from aws_cdk import (
    Stack,
    Duration,
    aws_eks as eks,
    aws_ssm as ssm,
    aws_lambda as _lambda,
    aws_iam as iam,
    custom_resources as cr,
)
from aws_cdk.lambda_layer_kubectl_v30 import KubectlV30Layer

from constructs import Construct


class EksCodeStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an EKS Cluster
        cluster = eks.Cluster(
            self, "MyCluster",
            version=eks.KubernetesVersion.V1_30,
            kubectl_layer=KubectlV30Layer(self, "kubectl"),
            default_capacity=2
        )

        # Create an SSM Parameter (assuming this stores environment like "development")
        ssm_parameter = ssm.StringParameter(
            self, "AccountEnvParam",
            parameter_name="/platform/account/env",
            string_value="development",  # Replace with your value
        )

        # Create the Lambda Function for the Custom Resource
        custom_function = _lambda.Function(
            self, "CustomResourceFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda")
        )

        # IAM Policy Statement for the Custom Resource
        custom_resource_policy = iam.PolicyStatement(
            actions=["ssm:GetParameter"],
            resources=[ssm_parameter.parameter_arn]
        )

        # Custom Resource
        custom_resource = cr.AwsCustomResource(
            self, "CustomResource",
            on_create=cr.AwsSdkCall(
                service="SSM",
                action="getParameter",
                parameters={"Name": ssm_parameter.parameter_name},
                physical_resource_id=cr.PhysicalResourceId.of("custom-resource"),
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements([custom_resource_policy])
        )

        # Use the Custom Resource output to configure the Helm chart
        ssm_value = custom_resource.get_response_field("Parameter.Value")

        # Assuming ssm_value is something like "development", translate to replica count
        replicas = 1 if ssm_value == "development" else 3

        # Helm Chart using values from Custom Resource
        chart = eks.HelmChart(
            self, "NginxIngress",
            cluster=cluster,
            chart="ingress-nginx",
            repository="https://kubernetes.github.io/ingress-nginx",
            release="nginx-ingress",
            values={
                "controller": {
                    "replicaCount": replicas
                }
            },
            namespace="kube-system",
            timeout=Duration.minutes(10)
        )
