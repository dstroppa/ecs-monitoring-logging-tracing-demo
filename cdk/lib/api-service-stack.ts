import cdk = require('@aws-cdk/core');
import ecs = require("@aws-cdk/aws-ecs");
import ecs_patterns = require("@aws-cdk/aws-ecs-patterns");
import sqs = require("@aws-cdk/aws-sqs");
import iam = require("@aws-cdk/aws-iam");

interface ApiServiceStackProps extends cdk.StackProps {
  cluster: ecs.Cluster;
  queue: sqs.IQueue;
}

export class ApiServiceStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id:string, props: ApiServiceStackProps) {
    super(scope, id);
    
    const apiServiceTaskRole = new iam.Role(this, "ApiServiceTaskRole", {
        assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com")
    });
    
    props.queue.grantSendMessages(apiServiceTaskRole);
    
    const apiService = new ecs_patterns.ApplicationLoadBalancedFargateService(this, "ApiService", {
        cluster: props.cluster,
        taskImageOptions: {
            image: ecs.ContainerImage.fromAsset("../api-service"),
            taskRole: apiServiceTaskRole,
            environment: {
                "QUEUE_NAME": props.queue.queueName
            }
        }
    });
    
    apiService.taskDefinition.addContainer("XRaySidecar", {
        image: ecs.ContainerImage.fromRegistry("amazon/aws-xray-daemon")
    });
    
  }
}