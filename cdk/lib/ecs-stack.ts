import cdk = require("@aws-cdk/core");
import ecs = require("@aws-cdk/aws-ecs");

export class EcsStack extends cdk.Stack {
  public readonly ecsCluster: ecs.Cluster;

  constructor(scope: cdk.App, id: string) {
    super(scope, id);

    this.ecsCluster = new ecs.Cluster(this, "Cluster", {
      clusterName: "monitoring-logging-tracing-demo",
      containerInsights: true
    });

  }
}
