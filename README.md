# Microservices Charts

`iam.yaml` is a Helm-templated version of the Crossplane claim from the provided repository. The Helm chart only requires two inputs: `serviceName` and `policiesFolder`.

To demonstrate, we can run the `helm template` command with these inputs:

```bash
helm template . --set policiesFolder=iam_policies/microsvc1 --set serviceName=microsvc1
```

The command generates the following YAML output:

```yaml
apiVersion: iam.crossplane.io/v1
kind: Xiam
metadata:
  name: microsvc1
spec:
  permissions:
    - type: microsvc1_policy
      policyDocument: |
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:DescribeSecret",
                        "secretsmanager:ListSecrets"
                    ],
                    "Resource": "*"
                }
            ]
        }
    - type: microsvc1_policy2
      policyDocument: |
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:DescribeSecret",
                        "secretsmanager:ListSecrets"
                    ],
                    "Resource": "*"
                }
            ]
        }
```

This system is designed without a `values.yaml` file to ensure the values are provided dynamically through **ArgoCD Appsets** during deployment. This makes the chart more flexible and suitable for an automated, declarative GitOps workflow.

Refer [ArgoCD Appsets Repo](https://github.com/Suraj01Dev/argocd-appsets-iam) for details on this.

