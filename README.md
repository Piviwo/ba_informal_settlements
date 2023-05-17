This code was created in the course of a bachelor thesis about 
'Open Data and urban monitoring: The potential of open source geodata for semi-automated monitoring of informal settlements'
Two approaches have been tested: a unsupervised K-Means-Algorithm and three supervised models namely a Support Vector Machine, a Random Forest-Model and a K-Nearest-Neighbors-Model. They are all located in the 'code'-folder.

The dataset consists of four sentinel-files that are used for trainig (located in the 'input_data'-folder).
Additionally, multiclass and binary groundtruth samples are used for the supervised classification models. They come in a shapefile format ('groundtruth_data'-folder).

For predictions, new input files need to be added! 