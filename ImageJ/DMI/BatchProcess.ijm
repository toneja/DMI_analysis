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
        
        // Execute our main macro
        runMacro("../DMI/AnalyzeSporesAndGermlings.ijm", plateSize);
        
        // Close the image
        close();

        // Clear the results table
        run("Clear Results");
    }
}

// Exit ImageJ
run("Quit");
