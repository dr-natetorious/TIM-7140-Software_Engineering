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

    efs_sg = ec2.SecurityGroup(self,'EfsGroup',
      vpc=self.vpc,
      allow_all_outbound=True,
      description='Security Group for ApkStore EFS')

    efs_sg.add_ingress_rule(
      peer= ec2.Peer.any_ipv4(),
      connection=ec2.Port.all_traffic(),
      description='Allow any traffic')

    self.efs = efs.FileSystem(self,'ApkStore',
      vpc=self.vpc,
      security_group= efs_sg,
      lifecycle_policy= efs.LifecyclePolicy.AFTER_14_DAYS,
      performance_mode= efs.PerformanceMode.GENERAL_PURPOSE)

