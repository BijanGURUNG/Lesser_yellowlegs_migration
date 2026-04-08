# Lesser_yellowlegs_migration

### Lesser yellowlegs (_Tringa flavipes_) migrate from upper latitudes of north america to the central and south america every year. USFWS tracked the migratory ### patterns of approximately 114 birds from Alaska, central Canada, and Eastern Canada. The dataset is available in MoveBanks repository  
### with the https://doi.org/10.5066/P9C7JWCC.  

### This rich datasets (Telemetry from GPS) can be applied to study the behavior of the birds, such as refueling sites, breeding sites, leading edge, and trailing edge. 

### There are two Python files in this repository. 

### 1. Cublic spline interpolation: This Python code applied the cublic spline function to smoothen the polylines, representing the flight tracks of Lesser yellowlegs. There are gaps in the recorded data because GPS signal is lost at many places. These recorded data or points are used to generate polylines that represent the flight path of the bird. I applied the cublic spline function (with time as the parameter) to generate a smooth curve that resembles the flight path. 

### 2. Identifying the fueling or resting sites: 


