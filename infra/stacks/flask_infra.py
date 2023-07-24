import aws_cdk as cdk
from aws_cdk import (Stack, aws_dynamodb, aws_ec2, aws_iam, aws_sns,
                     aws_sns_subscriptions)
from constructs import Construct


class StupidSimpleFlaskInfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # predefined network to deploy server in; Just looking it up using network id (aka vpc id)
        vpc = aws_ec2.Vpc.from_lookup(self, "StupidSimpleVPC", vpc_id="<<TODO: Replace with your VPC ID>>")

        mailing_list = aws_dynamodb.Table(
            self,
            "MailingList",
            partition_key=aws_dynamodb.Attribute(
                name="email",
                type=aws_dynamodb.AttributeType.STRING
            )
        )

        ip_list = aws_dynamodb.Table(
            self,
            "IPList",
            partition_key=aws_dynamodb.Attribute(
                name="ip",
                type=aws_dynamodb.AttributeType.STRING
            )
        )

        topic = aws_sns.Topic(
            self, "FlaskMySNSTopic",
            display_name="Stupid Simple Flask Notification"
        )

        # Add an email subscriber to the SNS topic
        email_address = "<<TODO: Replace with your email address>>"
        topic.add_subscription(aws_sns_subscriptions.EmailSubscription(email_address))

        server_access_role = aws_iam.Role(
            self, "FlaskRole",
            assumed_by=aws_iam.ServicePrincipal("ec2.amazonaws.com")
        )

        server_access_role.add_to_policy(aws_iam.PolicyStatement(
            actions=[
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Scan",
                "dynamodb:Query",
            ],
            resources=[mailing_list.table_arn, ip_list.table_arn]
        ))

        server_access_role.add_to_policy(aws_iam.PolicyStatement(
            actions=["sns:Publish"],
            resources=[topic.topic_arn]
        ))

        firewall_rule_group = aws_ec2.SecurityGroup(
            self,
            id="FlaskServerSG",
            vpc=vpc,
            description="Firewall rules for flask server"
        )

        firewall_rule_group.add_ingress_rule(
            peer=aws_ec2.Peer.any_ipv4(),
            connection=aws_ec2.Port.tcp(22),
            description="Allow incoming connection for SSH Server/Application management",
        )

        firewall_rule_group.add_ingress_rule(
            peer=aws_ec2.Peer.any_ipv4(),
            connection=aws_ec2.Port.tcp(5001),
            description="Allow incoming connection for the webapp",
        )


        flask_server = aws_ec2.Instance(
            self,
            "FlaskServer",
            instance_name="melbourne-university-event-demo-server",
            key_name="melb-uni-fg-evetn",
            vpc=vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PUBLIC),
            machine_image=aws_ec2.LookupMachineImage(
                name="al2023-ami-2023.1.20230719.0-kernel-6.1-x86_64"
            ),
            instance_type=aws_ec2.InstanceType.of(
                aws_ec2.InstanceClass.T2, aws_ec2.InstanceSize.MICRO
            ),
            security_group=firewall_rule_group,
            role=server_access_role
        )

        # install pip in the server
        flask_server.add_user_data(
            "sudo yum install -y python3-pip; pip install flask boto3"
        )

        eip = aws_ec2.CfnEIP(self, "FlaskServerIP")
        eip_association = aws_ec2.CfnEIPAssociation(
            self,
            "FlaskServerIPAssociation",
            instance_id=flask_server.instance_id,
            eip=eip.ref,
        )

