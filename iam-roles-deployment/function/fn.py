"""A Crossplane composition function."""

import grpc
from crossplane.function import logging, response
from crossplane.function.proto.v1 import run_function_pb2 as fnv1
from crossplane.function.proto.v1 import run_function_pb2_grpc as grpcv1
import json

class FunctionRunner(grpcv1.FunctionRunnerService):
    """A FunctionRunner handles gRPC RunFunctionRequests."""

    def __init__(self):
        """Create a new FunctionRunner."""
        self.log = logging.get_logger()

    async def RunFunction(
        self, req: fnv1.RunFunctionRequest, _: grpc.aio.ServicerContext
    ) -> fnv1.RunFunctionResponse:
        """Run the function."""
        log = self.log.bind(tag=req.meta.tag)
        log.info("Running function")


        rsp = response.to(req)


        name = req.observed.composite.resource["metadata"]["name"]
        permissions = req.observed.composite.resource["spec"]["permissions"]
        trustPolicyDoc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        rsp.desired.resources[f"role"].resource.update(
            {
                "apiVersion": "iam.aws.m.upbound.io/v1beta1",
                "kind": "Role",
                "metadata": {
                    "name": name,
                    "annotations": {
                        "crossplane.io/external-name": name,
                    },
                },
                "spec": {
                    "forProvider": {
                        "assumeRolePolicy": json.dumps(trustPolicyDoc),
                    },
                },
            }
        )


        for permission in permissions:
            permission_name=permission["type"]
            rsp.desired.resources[f"iam-{name}"].resource.update(
                {
                    "apiVersion": "iam.aws.m.upbound.io/v1beta1",
                    "kind": "Policy",
                    "metadata": {
                        "name": permission_name,
                        "annotations": {
                            "crossplane.io/external-name": permission_name,
                        },
                    },
                    "spec": {
                        "forProvider": {
                            "policy": json.dumps(json.loads(permission["policyDocument"])),
                        },
                    },
                }
            )

            rsp.desired.resources[f"policy-attachment"].resource.update(
                {
                    "apiVersion": "iam.aws.m.upbound.io/v1beta1",
                    "kind": "RolePolicyAttachment",
                    "metadata": {
                        "name": name,
                    },
                    "spec": {
                        "forProvider": {
                            "role": name,
                            "policyArnRef": {"name":permission_name}
                        },
                    },
                }
            )



        return rsp
