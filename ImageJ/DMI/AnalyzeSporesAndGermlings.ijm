// set scale unit for 4x objective and set min and max area filter (um^2) units
plateSize = getArgument();
if (plateSize == "35mm") {
	dist = 1.126;
	known = 1;
	min_area = 300;
} else {
	dist = 9600;
	known = 8600;
	min_area = 400;
}
run("Set Scale...", "distance=dist known=known unit=um");

// Check for RGB image
if (bitDepth() > 8) {
	// Convert to grayscale
	run("8-bit");
}

// Generate a binary image from image
setAutoThreshold("MaxEntropy");
setOption("BlackBackground", false);
run("Convert to Mask", "method=MaxEntropy background=Light");
run("Despeckle");

// Save final manipulated image
saveAs("tif", "DMI/images/" + getTitle());

// Generate ROIs
run("Set Measurements...", "area centroid perimeter fit shape feret's redirect=None decimal=3");
run("Analyze Particles...", "size=minarea-2000 circularity=0.00-0.99 show=Overlay display exclude include add");
roiManager("Show None");
saveAs("Results", "DMI/results/" + File.getNameWithoutExtension(getTitle()) + ".csv");
