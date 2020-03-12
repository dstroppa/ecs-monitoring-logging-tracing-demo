import cdk = require('@aws-cdk/core');
import ecs = require("@aws-cdk/aws-ecs");
import ecs_patterns = require("@aws-cdk/aws-ecs-patterns");
import iam = require("@aws-cdk/aws-iam");

interface ProcessorServiceStackProps extends cdk.StackProps {
  cluster: ecs.Cluster;
}

export class ProcessorServiceStack extends cdk.Stack {
  public readonly processorService: ecs_patterns.QueueProcessingFargateService;
  
  constructor(scope: cdk.Construct, id:string, props: ProcessorServiceStackProps) {
    super(scope, id);

    this.processorService = new ecs_patterns.QueueProcessingFargateService(this, "ProcessorService", {
        cluster: props.cluster,
        image: ecs.ContainerImage.fromAsset("../processor-service")
    });
    
    this.processorService.taskDefinition.addContainer("XRaySidecar", {
        image: ecs.ContainerImage.fromRegistry("amazon/aws-xray-daemon")
    });

    const taskRolePolicy =  new iam.PolicyStatement();
    taskRolePolicy.addActions(
      //  Allows the ECS task to interact with X-Ray
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords",
      "xray:GetSamplingRules",
      "xray:GetSamplingTargets",
      "xray:GetSamplingStatisticSummaries"
    );
    taskRolePolicy.addAllResources();

    this.processorService.taskDefinition.addToTaskRolePolicy(
     taskRolePolicy
    );
  }
}