from infra.datalake import DataLakeLayer
from infra.compute import ComputeLayer
def create_layers(scope):
  
  storage = DataLakeLayer(scope,'StorageLayer')
  compute = ComputeLayer(scope,'Compute',datalake=storage)

  return [
    storage,
    compute
  ]