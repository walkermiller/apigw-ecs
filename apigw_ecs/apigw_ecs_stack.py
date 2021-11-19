from aws_cdk import (
    aws_elasticloadbalancingv2,
    core as cdk,
    aws_apigateway as apigateway,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elb,
    aws_elasticloadbalancingv2_targets as targets
)


class ApigwEcsStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        image="public.ecr.aws/w5p8b6x2/cputest:latest"
        containerPort=80
        vpc = ec2.Vpc.from_lookup(self, 'ECSVPC', vpc_id=self.node.try_get_context('vpcid')) if self.node.try_get_context('vpcid') else ec2.Vpc(self, "ECSVPC")

        ecs_cluster = ecs.Cluster(
            scope=self,
            id="ecs-cluster",
            vpc=vpc,
            enable_fargate_capacity_providers=True,
            container_insights=True
        )


        ## Build ECS Service with an ALB
        # task_image_options = ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
        #     image=ecs.ContainerImage.from_registry(image),
        #     container_port=containerPort)

        task_image_options = ecs_patterns.ApplicationLoadBalancedTaskImageProps(
            image=ecs.ContainerImage.from_registry(image),
            container_ports=[80]
        )

        # alb = elb.ApplicationLoadBalancer(self, id="ALB", vpc=vpc, internet_facing=False)

        fargate_service = ecs_patterns.ApplicationMultipleTargetGroupsFargateService(
            scope=self,
            id="fargateService",
            assign_public_ip=False,
            cluster=ecs_cluster,
            platform_version=ecs.FargatePlatformVersion.VERSION1_4,
            task_image_options=task_image_options,
            cpu=256,
            memory_limit_mib=512,
            load_balancers=[
                ecs_patterns.ApplicationLoadBalancerProps(
                    listeners=[
                        ecs_patterns.ApplicationListenerProps(
                            name="HTTP:80",
                            port=80,
                            protocol=elb.ApplicationProtocol.HTTP
                        )
                    ],
                    public_load_balancer=False,
                    name="ecs-alb"
                )
            ],
            target_groups=[
                ecs_patterns.ApplicationTargetProps(
                    container_port=containerPort
                )
            ])

        ## Create NLB and forward traffic to ALB
        nlb = elb.NetworkLoadBalancer(
            scope=self,
            id="nlb",
            vpc=vpc,
            internet_facing=False,
            load_balancer_name="ecs-service-lb"
        )

    
        ## Create the NLB Target Group
        nlb_tg = elb.NetworkTargetGroup(
            scope=self,
            id="ecs-alb-tg",
            vpc=vpc,
            port=80,
            protocol=elb.Protocol.TCP,
            target_type=elb.TargetType.ALB,
            targets=[targets.AlbTarget(
                alb=fargate_service.load_balancer,
                port=80)]
        )

        nlb.add_listener("HTTP", 
            protocol=elb.Protocol.TCP,
            port=80,
            default_target_groups=[nlb_tg])

        ## Creat VPCLink to NLB
        vpc_link = apigateway.VpcLink(self,
            id="VPCLink"
        )

        vpc_link.add_targets(nlb)

        ## Create API
        api = apigateway.RestApi(self,
            id="TestAPI",
            deploy=True,
            rest_api_name="TestAPI",
        )

        ## Create the API Integration
        integration = apigateway.Integration(
            type=apigateway.IntegrationType.HTTP_PROXY,
            integration_http_method='ANY',
            options=apigateway.IntegrationOptions(
                connection_type=apigateway.ConnectionType.VPC_LINK,
                vpc_link=vpc_link
            ))

        root_proxy = api.root.add_proxy(default_integration=integration, any_method=True)

        ##  Second ECS Service

        # econd_fargate_service = ecs_patterns.

