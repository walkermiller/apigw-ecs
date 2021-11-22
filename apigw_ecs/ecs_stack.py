from aws_cdk import (
    core as cdk,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elb,
    aws_elasticloadbalancingv2_targets as targets
)

class EcsStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        image="public.ecr.aws/w5p8b6x2/cputest:latest"
        containerPort=80
        vpc = ec2.Vpc.from_lookup(self, 
            'ECSVPC',
            vpc_id=self.node.try_get_context('vpcid'))

        # alb = elb.ApplicationLoadBalancer.from_lookup(self, 
        #     'ALB',
        #     load_balancer_arn=self.node.try_get_context('alb'))
    
        listener = elb.ApplicationListener.from_lookup(self,
            id="listener",
            load_balancer_arn=self.node.try_get_context('alb'),
            listener_protocol=elb.ApplicationProtocol.HTTP,
            listener_port=80)
         
        ecs_cluster = ecs.Cluster(
            scope=self,
            id="ecs-cluster",
            vpc=vpc,
            enable_fargate_capacity_providers=True,
            container_insights=True
        )

        target_group = elb.ApplicationTargetGroup(
            self,
            id="tg",
            vpc=vpc,
            protocol=elb.ApplicationProtocol.HTTP,
            target_type=elb.TargetType.IP
        )

        listener.add_target_groups(
            id="listtg",
            path_pattern = "/second",
            priority=10,
            target_groups=[target_group]
        )

        ecs_task_definition = ecs.TaskDefinition(self,
            id="taskdef",
            cpu="256",
            compatibility=ecs.Compatibility.FARGATE,
            memory_mib="512",
            network_mode=ecs.NetworkMode.AWS_VPC,
            

        )
        ecs_task_definition.add_container(
            id="container",
            image=ecs.ContainerImage.from_registry(image),
            port_mappings=[ecs.PortMapping(container_port=containerPort, host_port=containerPort, protocol=ecs.Protocol.TCP)]
        )

        ecs_service = ecs.FargateService(
            self,
            id="service",
            cluster=ecs_cluster,
            platform_version=ecs.FargatePlatformVersion.VERSION1_4,
            task_definition=ecs_task_definition
        )

        ecs_service.attach_to_application_target_group(target_group=target_group)





