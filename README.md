# API Gateway Rest API to ECS fronted by an Application Load Balancer 

## Design
![diagram](diagrams/api.png)
## Deploy
If you specify a vpcid, it will be used. Otherwise, a VPC will be created as part of the stack. 
~~~
cdk deploy -c vpcid=vpc-#########
~~~