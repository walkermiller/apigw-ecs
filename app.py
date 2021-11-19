#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from aws_cdk import core

from apigw_ecs.apigw_ecs_stack import ApigwEcsStack


app = core.App()
ApigwEcsStack(app, "ApigwEcsStack",env=core.Environment(account='851165779994', region='us-east-2'))

app.synth()
