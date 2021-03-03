import os.path
from infra.datalake import DataLakeLayer
from aws_cdk import (
    core,
    aws_sqs as sqs,
    aws_lambda_event_sources as events,
    aws_lambda as lambda_,
    aws_ecr_assets as ecr,
    aws_ecs as ecs,
    aws_ecs_patterns as ecsp,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_efs as efs
)

root_dir = os.path.join(os.path.dirname(__file__),'..')
class SonarQubeLayer(core.Construct):
  """
  Configure the compute layer
  """
  @property
  def datalake(self) -> DataLakeLayer:
    return self.__datalake

  def __init__(self, scope: core.Construct, id: str,datalake:DataLakeLayer, **kwargs) -> None:
    super().__init__(scope, id, **kwargs)

    self.__datalake=datalake
    self.security_group = ec2.SecurityGroup(self,'SecurityGroup',
      vpc=self.datalake.vpc,
      allow_all_outbound=True,
      description='SonarQube Security Group')

    self.sonarqube_svr_ecr = ecr.DockerImageAsset(self,'Repo',
      directory=os.path.join(root_dir, 'images/sonarqube-server'),
      repository_name='sonarqube')

    self.sonarqube_cli_ecr = ecr.DockerImageAsset(self,'Cli',
      directory=os.path.join(root_dir, 'images/sonarqube-scanner'),
      repository_name='sonarqube-cli')

    self.database = rds.DatabaseCluster(self,'Database',
      engine=rds.DatabaseClusterEngine.aurora_postgres(
        version = rds.AuroraPostgresEngineVersion.VER_11_9
      ),
      default_database_name='sonarqube',
      removal_policy= core.RemovalPolicy.DESTROY,
      credentials=rds.Credentials.from_username(
        username='postgres',
        password=core.SecretValue(value='postgres')),
      instance_props= rds.InstanceProps(
        vpc=self.datalake.vpc,
        security_groups=[self.security_group],
        instance_type=ec2.InstanceType('r6g.xlarge')))

    efs_data = self.datalake.efs.add_access_point('sonarqube-data',
      create_acl= efs.Acl(owner_gid="0", owner_uid="0", permissions="777"),
      path='/sonarqube/data')

    efs_temp = self.datalake.efs.add_access_point('sonarqube-temp',
      create_acl= efs.Acl(owner_gid="0", owner_uid="0", permissions="777"),
      path='/sonarqube/temp')
    
    self.service = ecsp.ApplicationLoadBalancedFargateService(self,'Server',
      assign_public_ip=True,
      vpc=self.datalake.vpc,
      desired_count=1,
      cpu=4096,
      memory_limit_mib=8*1024,
      listener_port=80,
      platform_version= ecs.FargatePlatformVersion.VERSION1_4,
      security_groups=[self.security_group, self.datalake.efs_sg ],     
      task_image_options= ecsp.ApplicationLoadBalancedTaskImageOptions(
        image= ecs.ContainerImage.from_docker_image_asset(asset=self.sonarqube_svr_ecr),
        container_name='sonarqube-svr',
        container_port=9000,
        enable_logging=True,
        environment={
          '_SONAR_JDBC_URL':'jdbc:postgresql://{}/sonarqube'.format(
              self.database.cluster_endpoint.hostname),
          '_SONAR_JDBC_USERNAME':'postgres',
          '_SONAR_JDBC_PASSWORD':'postgres'
        }))
    
    for name in [
      'AmazonElasticFileSystemClientFullAccess' ]:
      self.service.task_definition.task_role.add_managed_policy(
        iam.ManagedPolicy.from_aws_managed_policy_name(name))

    self.service.task_definition.add_volume(
      name='data',
      efs_volume_configuration= ecs.EfsVolumeConfiguration(
        file_system_id= self.datalake.efs.file_system_id,
        #root_directory='/var/sonarqube/data',
        transit_encryption= 'ENABLED',
        authorization_config= ecs.AuthorizationConfig(
          access_point_id= efs_data.access_point_id,
          iam='DISABLED')))

    # self.service.task_definition.add_volume(
    #   name='temp',
    #   efs_volume_configuration= ecs.EfsVolumeConfiguration(
    #     file_system_id= self.datalake.efs.file_system_id,
    #     root_directory='/var/sonarqube/temp'))
        # transit_encryption= 'ENABLED',
        # authorization_config= ecs.AuthorizationConfig(
        #   access_point_id= efs_temp.access_point_id )))
