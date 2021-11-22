#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from aws_cdk import core

from apigw_ecs.apigw_ecs_stack import ApigwEcsStack
from apigw_ecs.ecs_stack import EcsStack


app = core.App()

account = app.node.try_get_context('account')
region = app.node.try_get_context('region')
ApigwEcsStack(app, "ApigwEcsStack",env=core.Environment(account=account, region=region))
EcsStack(app, "EcsStack",env=core.Environment(account=account, region=region))

app.synth()