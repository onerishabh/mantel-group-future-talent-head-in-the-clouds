import aws_cdk as cdk
from stacks.flask_infra import StupidSimpleFlaskInfraStack
app = cdk.App()

AWS_ACCOUNT_ID = app.node.try_get_context(f"AWSAccountID")
AWS_REGION_NAME = app.node.try_get_context("AWSProfileRegion")

DEP_ENV = cdk.Environment(account=AWS_ACCOUNT_ID, region=AWS_REGION_NAME)

StupidSimpleFlaskInfraStack(
    app,
    "StupidSimpleFlaskInfraStack",
    env=DEP_ENV,
)

cdk.Tags.of(app).add("project", "melb-fg-uni-event")
cdk.Tags.of(app).add("creator", "<<TODO: Replace with your email address>>")

app.synth()
