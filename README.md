# myFAIR analysis @ EMC

  * [Dependencies](#dependencies)
  * [Installation Instructions](#installation-instructions)
  * [Run the myFAIR analysis](#run-the-myfair-analysis)
  * [See results](#see-results)
  * [Using GEO files](#using-geo)
  * [Run the analysis again](#rerun-analysis)

For this testcase we are using variant selection by GEMINI analysis using genome in the bottle data. Specifically, we will be using Ashkenazim Father-Mother-Son trio data from the Personal Genome Project. You can download the down sampled version of the dataset created by the GEMINI team from a GIAB trio dataset.
The vcf file can be found [here](https://bioinf-galaxian.erasmusmc.nl/galaxy/library/list#folders/F8ae2ca084c0c0c70/datasets/e4e82f84348cba8c) and the ped file can be found [here](https://bioinf-galaxian.erasmusmc.nl/galaxy/library/list#folders/F8ae2ca084c0c0c70/datasets/5e4dbb32432c1676).
For the GEO data matrix option there is no workflow available. You can follow the steps to filter the data matrix and metadata based on selected samples and send them to Galaxy. You can find these steps under the "Using GEO files" header.

# <a name="dependencies"></a>Dependencies
* Python 2.7.12
* Django 1.10.2, 1.10.3 or 1.10.4
* Bioblend 0.8.1
* rdflib
* Java SE Development Kit 8u112
* Apache Jena Fuseki 2.4.1
* Galaxy 16.07 or an existing Galaxy server with the following tools available:
    * GEMINI (load, autosomal recessive/dominant, de novo, comp hets)
    * Add Column, Strip Header and File Concatenate (all can be found under the name file_manipulation in the Galaxy tool shed)

# <a name="installation-instructions"></a> Installation Instructions
**Install myFAIR on your existing VM**

To install myFAIR on your existing Virtual Machine follow these steps:

1. Install all dependencies.
2. Download or clone myFAIR to your home directory. The latest version can be found [here](https://github.com/ErasmusMC-Bioinformatics/myFAIR).
3. Change the Galaxy server setting by changing the **galaxy.ini.sample** file. Change the port to 8000 and change the host to 0.0.0.0
4. Run the server by opening the terminal and type: **myFAIR/manage.py runserver 0.0.0.0:8080**
5. To run the Apache Fuseki Server open the terminal and type:  **fuseki location/fuseki start**
7. Create a new dataset in Fuseki called "ds".
8. Start the Galaxy server by opening the terminal and type: **galaxy location/run.sh**
9. Download the Gemini workflow by importing a workflow using this url: https://bioinf-galaxian.erasmusmc.nl/galaxy/u/rick/w/training-gemini-vcfanalysis-11112016/json.
10. Test if 127.0.0.1:8080 shows the myFAIR login page and that 127.0.0.1:8000 shows the Galaxy page.
11. Download the Gemini annotation files [here](https://bioinf-galaxian.erasmusmc.nl/owncloud/index.php/s/JuH6c97y5lAVSf2) and place the folder "gemini_annotation" in the home folder.

After these steps, you can run the myFAIR analysis.

**Install and use our VM**

You can test myFAIR on our existing Virtual Machine.
Everything is already pre-installed and can be used after following these steps below:

1. Download the Virtual Machine [here](https://bioinf-galaxian.erasmusmc.nl/owncloud/index.php/s/Qr5Nu6CBotyvG1Z). **(The size of the Virtual Machine will be large due to the annotation files needed for Gemini, please make sure you have enough free space to run the Virtual Machine)**
2. Add the Virtual Machine and start the Virtual Machine (Password is "fair@emc")
3. Open the terminal and start the Fuseki Server by typing: **.local/apache-jena-fuseki-2.4.1/fuseki start**
4. Test if 127.0.0.1:8080 shows the myFAIR login page and that 127.0.0.1:8000 shows the Galaxy page. To see if the fuseki sevrer is running, go to 127.0.0.1:3030 and see if there is a green circle next to "Server status:".
5. Download the Gemini annotation files [here](https://bioinf-galaxian.erasmusmc.nl/owncloud/index.php/s/JuH6c97y5lAVSf2) and place the folder "gemini_annotation" in the home folder.
After these steps you can run the myFAIR analysis.

# <a name="run-the-myfair-analysis"></a> Run the myFAIR analysis
In order to run the myFAIR analysis you need to follow these steps:

1. Follow the Installation Instructions.
2. Open or download a browser (Firefox or Chrome recommended).
3. Go to the local Galaxy page: 127.0.0.1:8000
4. Login to your account or create a new account by clicking "User" and then clicking "Register".
5. Get the API Key from your account. If you do not have an API Key visible for you, create one.
6. Visit the B2DROP or page and create a folder where you can put your datafiles. You can also use the bioinf-galaxian Owncloud if you have an account.
    * If you do not have a B2DROP account please visit: https://b2drop.eudat.eu/index.php/login and click register.
    * If you have a B2DROP account, please log in and create a new folder.
    * Add the .vcf and .ped file to this folder.
    If you are using the GEO data matrix, please put that file in a folder.
7. Visit the myFAIR analysis page on 127.0.0.1:8080
8. Login using your Galaxy API Key and your B2DROP or bioinf-galaxian credentials.
9. Upload files to the Fuseki server:
    * Click on the "Upload Files" link.
    * Select the folder where your datafiles are located and click "See files".
    * You will now see the two files you added to this folder in step 6.
    * Choose which file is your datafile (vcf file) and which file is your metadata (ped file).
    * Click "Make Turtle" to start the creation of new triples and store them in the Fuseki server.
    * If you are using the GEO data matrix, please choose the "datafile" option for all data matrix files you want to upload. If you do not have a metadata file, click "Make Turtle". If you already have a metadata file please select "metadata" for that file and then click "Make Turtle".
    * You will be send back to the homepage.

10. Find your files or samples:

    a. Find all available files that have been uploaded to the Fuseki server.
    *   Select the option "Get all available files".
    *   Click on the "Process >>" button to start searching for your files.
    
    b. Find all available samples that have been uploaded to the Fuseki server.
    *   Select the option "Get all samples from all files".
    *   Click on the "Process >>" button to start searching for your files.

    c. Find your files using a sample name:
    *   Select the option "Get file(s) from sample".
    *   Enter a sample name.
    *   Click on the "Process >>" button to start searching for your files.
    
    d. Find your files using a group name:
    *   Select the option "Get samples from group".
    *   Enter the name of a group.
    *   Click on the "Process >>" button to start searching for your files.

    e. Find samples based on gender:
    *   Select the option "Get samples from sex".
    *   Enter a gender.
    *   Click on the "Process >>" button to start searching for your files.
    
    f. Find samples with a specific disease:
    *   Select the option "Get samples from disease".
    *   Enter the name of the disease.
    *   Click on the "Process >>" button to start searching for your files.
    
11. Send the files to Galaxy and run a workflow:
    *   After finding your files, select the "Training_gemini_vcfanalysis_11112016" workflow by clicking on the dropdown menu.
    *   Select the file you want to send and choose the options you want to use.
    *   Enter a new history name or leave empty to automatically generate a new history name.
    *   Then click on the "send to galaxy" button to start sending the files to a new history and running the selected workflow.
12. A cat will appear to let you know that the files are being send to Galaxy and that the workflow is running (if you have selected a workflow).
A checkmark will appear when the files are send to galaxy and the workflow is finished (if you selected a workflow).
If something went wrong (workflow failed, not selected a file) or you get timed-out, an error message will appear.
13. If you do not want to use a workflow you can choose "Use Galaxy" to only send the datafiles to Galaxy and work with the files directly in Galaxy.
14. You can visit the Galaxy page to see if the workflow is running by going to http://127.0.0.1:8000 or go to the next step.

# <a name="using-geo"></a> Using GEO files
To split GEO files and send only specific samples to a new Galaxy history follow these steps:

1. Download the GSE7621_series_matrix.txt files from ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE7nnn/GSE7621/matrix/
2. Place the data matrix in a folder in B2DROP or bioinf-galaxian Owncloud.
3. Index the data matrix by clicking on the Upload Files link. Then selecting the folder with the data matrix, then select the matrix file as a datafile and click on the "Make Turtle" button. (If you already have a metadata file based on the data matrix please select this file to be metadata. Step 4 will be skipped if you have selected this option.)
4. The metadata will be created automatically and uploaded to the same folder as the data matrix. After this is done you will be redirected to the homepage.
5. Select the "Get samples from group" option.
6. Enter the name of the folder where the data matrix is located.
7. Click on the "Process >>" button to start searching for all available samples in the data matrix.
8. A list of samples will be shown in the results table. On the right side you will see a checkbox to select the file you want to use, on the left side are two checkboxes with the options A and B.
9. Select a file you want to use (In this case all files should be the same).
10. Select the samples you want to use in group A and group B by checking the checkboxes next to the sample name.
11. Choose the file format tabular or auto.
12. Enter a new history name or leave empty to automatically generate a new history name.
13. Click the "send to galaxy" button.
14. The new matrix and metadata based on the selected samples will be send to Galaxy and will also be uploaded to the B2DROP or bioinf-galaxian Owncloud.
15. Visit the Galaxy page to view the uploaded and to start working with them.

# <a name="see-results"></a> See results
The following steps can be used to view the results of your histories.

1. Click on the "Get results from group" option.
2. Enter the group name that you want to get the results from.
3. Select the results you want to view by checking the select file checkmark.
4. Click on the "Show results" button.
5. A new page will open with the input and output files  and the analysis details.
6. Click on any of the "Download" buttons to download that file.

# <a name="rerun-analysis"></a> Run the analysis again
Follow these steps to run the analysis shown in the result page again:

1. In the results page click on the "Run again" button.
2. A cat will appear to show that the analysis is running.
3. After the files are send to Galaxy a checkmark will appear and you will be redirected the homepage.
4. Visit the Galaxy page to see the analysis.
