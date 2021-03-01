from infra.vpce import VpcEndpointsForAWSServices
from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_efs as efs
)

class DataLakeLayer(core.Construct):
  """
  Configure the datalake layer
  """
  def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.vpc = ec2.Vpc(self,'Network')
    VpcEndpointsForAWSServices(self,'Endpoints',vpc=self.vpc)

    self.product_descr_bucket = s3.Bucket(self,'AndroidProducts',
      removal_policy= core.RemovalPolicy.DESTROY)

    self.efs = efs.FileSystem(self,'ApkStore',
      vpc=self.vpc,
      lifecycle_policy= efs.LifecyclePolicy.AFTER_14_DAYS,
      performance_mode= efs.PerformanceMode.GENERAL_PURPOSE)

