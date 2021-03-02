import os.path
from infra.datalake import DataLakeLayer
from aws_cdk import (
    core,
    aws_lambda as lambda_,
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

  @property
  def datalake(self) -> DataLakeLayer:
    return self.__datalake

  def __init__(self, scope: core.Construct, id: str,datalake:DataLakeLayer, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.__datalake=datalake
    self.add_devbox()
    self.add_repo_collector()

    ecr.DockerImageAsset(self,'fdroid-scrape',
      directory=os.path.join(root_dir,'fdroid-scrape'),
      repository_name='fdroid-scrape')

  def add_repo_collector(self):
    """
    Add lambda for downloading each repository
    """
    repo = ecr.DockerImageAsset(self,'Repo',
      directory=os.path.join(root_dir,'fdroid-scrape-repo'),
      repository_name='fdroid-scrape-repo')

    self.scrape_repo = lambda_.DockerImageFunction(self,'fdroid-scrape-repo',
      code = lambda_.DockerImageCode.from_ecr(
        repository=repo.repository,
        tag=repo.image_uri.split(':')[-1]), # lambda_.DockerImageCode.from_image_asset(directory=os.path.join(src_root_dir,directory)),
      description='Python container lambda function for '+repo.repository.repository_name,
      timeout= core.Duration.minutes(15),
      memory_size=4096,
      tracing= lambda_.Tracing.ACTIVE, 
      # Note: This throttles the AWS S3 batch job.
      # Downloading too fast will cause f-droid to disconnect the crawler
      reserved_concurrent_executions= 5,
      filesystem= lambda_.FileSystem.from_efs_access_point(
        ap= self.datalake.efs.add_access_point(
          'fdroid-scrape-repo',
          path='/fdroid-scrape-repo',
          create_acl=efs.Acl(owner_gid="0", owner_uid="0", permissions="777")),
        mount_path='/mnt/efs'
      ),
      environment={
        'EFS_MOUNT':'/mnt/efs'
      },
      vpc= self.datalake.vpc)

    for name in [
      'AmazonElasticFileSystemClientFullAccess',
      'AWSXrayWriteOnlyAccess',
      'AmazonS3FullAccess',
      'AWSCodeCommitFullAccess' ]:
      self.scrape_repo.role.add_managed_policy(
        iam.ManagedPolicy.from_aws_managed_policy_name(name))

  def add_devbox(self):
    """
    Create single node for development
    """
    self.devbox = ec2.Instance(self,'DevBox',
      instance_type=ec2.InstanceType('t2.medium'),
      machine_image= ec2.MachineImage.latest_amazon_linux(
        cpu_type=ec2.AmazonLinuxCpuType.X86_64,
        storage= ec2.AmazonLinuxStorage.GENERAL_PURPOSE
      ),
      vpc=self.datalake.vpc,
      allow_all_outbound=True)

    if self.datalake.efs.file_system_id == None:
      raise AssertionError('No filesystem id present')

    self.devbox.add_user_data(
      "yum check-update -y",
      "yum upgrade -y",
      "yum install -y amazon-efs-utils nfs-utils docker",
      "service docker start",
      "file_system_id_1=" + self.datalake.efs.file_system_id,
      "efs_mount_point_1=/mnt/efs/",
      "mkdir -p \"${efs_mount_point_1}\"",
      "test -f \"/sbin/mount.efs\" && echo \"${file_system_id_1}:/ ${efs_mount_point_1} efs defaults,_netdev\" >> /etc/fstab || " + "echo \"${file_system_id_1}.efs." + core.Stack.of(self).region + ".amazonaws.com:/ ${efs_mount_point_1} nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,_netdev 0 0\" >> /etc/fstab", "mount -a -t efs,nfs4 defaults"
    )

    for policy in [
      'AmazonSSMManagedInstanceCore',
      'AmazonS3FullAccess',
      'AWSCodeCommitFullAccess',
      'AmazonCodeGuruReviewerFullAccess',
      'AmazonEC2ContainerRegistryPowerUser']:
      self.devbox.role.add_managed_policy(
        iam.ManagedPolicy.from_aws_managed_policy_name(policy))
