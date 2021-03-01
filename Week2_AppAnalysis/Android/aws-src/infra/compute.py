import os.path
from infra.datalake import DataLakeLayer
from aws_cdk import (
    core,
    aws_ecr_assets as ecr,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_efs as efs
)

root_dir = os.path.join(os.path.dirname(__file__),'..')

class ComputeLayer(core.Construct):
  """
  Configure the compute layer
  """
  def __init__(self, scope: core.Construct, id: str,datalake:DataLakeLayer, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.add_devbox(datalake=datalake)
    ecr.DockerImageAsset(self,'fdroid-scrape',
      directory=os.path.join(root_dir,'fdroid-scrape'),
      repository_name='fdroid-scrape')

  def add_devbox(self, datalake:DataLakeLayer):
    """
    Create single node for development
    """
    self.devbox = ec2.Instance(self,'DevBox',
      instance_type=ec2.InstanceType('t2.medium'),
      machine_image= ec2.MachineImage.latest_amazon_linux(
        cpu_type=ec2.AmazonLinuxCpuType.X86_64,
        storage= ec2.AmazonLinuxStorage.GENERAL_PURPOSE
      ),
      vpc=datalake.vpc,
      allow_all_outbound=True)

    self.devbox.add_user_data(
      "yum check-update -y",
      "yum upgrade -y",
      "yum install -y amazon-efs-utils nfs-utils docker",
      "service docker start",
      "file_system_id_1=" + datalake.efs.file_system_id,
      "efs_mount_point_1=/mnt/efs/",
      "mkdir -p \"${efs_mount_point_1}\"",
      "test -f \"/sbin/mount.efs\" && echo \"${file_system_id_1}:/ ${efs_mount_point_1} efs defaults,_netdev\" >> /etc/fstab || " + "echo \"${file_system_id_1}.efs." + core.Stack.of(self).region + ".amazonaws.com:/ ${efs_mount_point_1} nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,_netdev 0 0\" >> /etc/fstab", "mount -a -t efs,nfs4 defaults"
    )

    for policy in [
      'AmazonSSMManagedInstanceCore',
      'AmazonS3FullAccess',
      'AWSCodeCommitFullAccess',
      'AmazonCodeGuruReviewerFullAccess' ]:
      self.devbox.role.add_managed_policy(
        iam.ManagedPolicy.from_aws_managed_policy_name(policy))
