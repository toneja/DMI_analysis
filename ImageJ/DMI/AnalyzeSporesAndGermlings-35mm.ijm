// set scale unit for 4x objective 
run("Set Scale...", "distance=1.1263 known=1 unit=um");

// Generate a binary image from image
setAutoThreshold("MaxEntropy");
setOption("BlackBackground", false);
run("Convert to Mask", "method=MaxEntropy background=Light");
run("Despeckle");

// Save final manipulated image
saveAs("tif", "DMI/images/" + getTitle());

// Generate ROIs
run("Set Measurements...", "area centroid perimeter fit shape feret's redirect=None decimal=3");
// set min and max area filter (um^2) units
minarea = 300
maxarea = 2000
run("Analyze Particles...", "size=minarea-maxarea circularity=0.00-0.99 show=Overlay display exclude include add");
roiManager("Show None");
saveAs("Results", "GPM/results/" + File.getNameWithoutExtension(getTitle()) + ".csv");
