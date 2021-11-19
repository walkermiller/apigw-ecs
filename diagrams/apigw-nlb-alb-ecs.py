from diagrams import Diagram, Edge, Cluster
from diagrams.aws.network import NLB, APIGateway, ALB 
from diagrams.aws.compute import ECS


with Diagram("API", show=False):
    with Cluster("AWS"):
        api = APIGateway("API")
        with Cluster("VPC"):

            nlb = NLB("NLB")
            alb = ALB("ALB")
            firstService = ECS("first")
            secondService = ECS("second")
            thirdService = ECS("third")

    api >> Edge(label="VPCLink") >> nlb >> alb
    alb >> Edge(label="/first") >>firstService
    alb >> Edge(label="/second") >> secondService
    alb >> Edge(label="/thrid") >> thirdService


