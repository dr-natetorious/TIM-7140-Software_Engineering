from infra.datalake import DataLakeLayer
from infra.compute import ComputeLayer
from infra.sonarqube import SonarQubeLayer
def create_layers(scope):
  
  storage = DataLakeLayer(scope,'StorageLayer')
  compute = ComputeLayer(scope,'Compute',datalake=storage)
  sonar = SonarQubeLayer(scope,'SonarQube', datalake=storage)

  return [
    storage,
    compute,
    sonar
  ]