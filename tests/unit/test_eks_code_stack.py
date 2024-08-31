import aws_cdk as core
import aws_cdk.assertions as assertions

from eks_code.eks_code_stack import EksCodeStack

# example tests. To run these tests, uncomment this file along with the example
# resource in eks_code/eks_code_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EksCodeStack(app, "eks-code")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
