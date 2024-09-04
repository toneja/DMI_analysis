// Macro to batch process a folder of images one at a time
inputFolder = getArgument();

// Get plate size from folder name
plateSize = substring(inputFolder, lastIndexOf(inputFolder, "_") + 1);

// Get a list of files in the input folder
list = getFileList(inputFolder);

// Process each image file in the folder
for (i = 0; i < list.length; i++) {
    if (endsWith(list[i], ".jpg")) {
        // Open the image
        open(inputFolder + "/" + list[i]);
        imgTitle = File.getNameWithoutExtension(list[i]);

        // Execute our main macro
        runMacro("../DMI/AnalyzeSporesAndGermlings.ijm", plateSize);

        // Re-open and switch to the original image
        open(inputFolder + "/" + list[i]);
        selectWindow(imgTitle + "-1.jpg");

        // Multi-crop the ROIs
        roiCount = roiManager("Count");
        if (roiCount > 0) {
            roiManager("Select", 0);
            run("Select All");
            roiIndices = newArray(roiCount);
            for (n = 0; n < roiCount; n++) {
                roiIndices[n] = n;
            }
            roiManager("Select", roiIndices);
            roiManager("Add");
            RoiManager.multiCrop("DMI/images/", " show");
            selectWindow("CROPPED_ROI Manager");
            saveAs("tif", "DMI/images/Cropped-" + imgTitle + ".tif");
        }

        // Close the images
        while (nImages() > 0) {
            close();
        }

        // Clear the ROI manager
        roiManager("Reset");

        // Clear the results table
        run("Clear Results");
    }
}

// Exit ImageJ
run("Quit");
