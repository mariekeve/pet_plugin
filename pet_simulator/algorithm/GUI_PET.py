from qgis.core import QgsRasterLayer, QgsProject

# Provide the path to your GeoTIFF file
tif_file_path = '/path/to/your/raster_file.tif'

# Define the desired extent (xmin, ymin, xmax, ymax) in the map's coordinate reference system (CRS)
desired_extent = (xmin, ymin, xmax, ymax)  # Replace these with your desired values

# Create a QgsRasterLayer object from the GeoTIFF file path with the desired extent
raster_layer = QgsRasterLayer(tif_file_path, 'Raster Layer', 'gdal', True, QgsProject.instance())
raster_layer.setExtent(desired_extent)

# Check if the layer was loaded successfully
if not raster_layer.isValid():
    print('Error: Invalid raster layer.')
else:
    # Add the raster layer to the map canvas
    QgsProject.instance().addMapLayer(raster_layer)

# Output a message to indicate the process is complete
print('Raster layer loaded and displayed.')