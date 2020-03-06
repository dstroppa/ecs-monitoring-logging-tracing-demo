#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { EcsStack } from '../lib/ecs-stack';
import { ProcessorServiceStack } from '../lib/processor-service-stack';
import { ApiServiceStack } from '../lib/api-service-stack';

const app = new cdk.App();
const ecsStack = new EcsStack(app, 'EcsStack');
const processorServiceStack = new ProcessorServiceStack(app, 'ProcessorServiceStack', {
    cluster: ecsStack.ecsCluster
});
const apiServiceStack = new ApiServiceStack(app, 'ApiServiceStack', {
    cluster: ecsStack.ecsCluster,
    queue: processorServiceStack.processorService.sqsQueue
});

