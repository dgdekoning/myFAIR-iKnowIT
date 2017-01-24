# myFAIR analysis @ EMC

  * [Dependencies](#dependencies)
  * [Installation Instructions](#installation-instructions)
  * [Run the myFAIR analysis](#run-the-myfair-analysis)
  * [See results](#see-results)

For this testcase we are using variant selection by GEMINI analysis using genome in the bottle data. Specifically, we will be using Ashkenazim Father-Mother-Son trio data from the Personal Genome Project. You can download the down sampled version of the dataset created by the GEMINI team from a GIAB trio dataset.
The vcf file can be found [here](https://bioinf-galaxian.erasmusmc.nl/galaxy/library/list#folders/F8ae2ca084c0c0c70/datasets/e4e82f84348cba8c) and the ped file can be found [here](https://bioinf-galaxian.erasmusmc.nl/galaxy/library/list#folders/F8ae2ca084c0c0c70/datasets/5e4dbb32432c1676).

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
3. Open the terminal and and start the Fuseki Server by typing: **.local/apache-jena-fuseki-2.4.1/fuseki start**
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
6. Visit the B2DROP page and create a folder where you can put your datafiles.
    * If you do not have a B2DROP account please visit: https://b2drop.eudat.eu/index.php/login and click register.
    * If you have a B2DROP account, please log in and create a new folder.
    * Add the .vcf and .ped file to this folder.
7. Visit the myFAIR analysis page on 127.0.0.1:8080
8. Login using your Galaxy API Key and your B2DROP credentials.
9. Upload files to the Fuseki server:
    * Click on the "Upload Files" link.
    * Select the folder where your datafiles are located and click "See files".
    * You will now see the two files you added to this folder in step 6.
    * Choose which file is your datafile (vcf file) and which file is your metadata (ped file).
    * Click "Make Turtle" to start making a new rdf file and send this to the Fuseki server.
    * You will be send back to the homepage.

10. Find your files:

    a. Find your files using the group name:
    *   Select the option "Get file(s) from group".
    *   Enter the name of the folder you have created in B2DROP in the textbox.
    *   Click on the "Process >>" button to start searching for your files.

    b. Find your files using the sample name:
    *   Select the option "Get file(s) from sample"
    *   Enter one of the three sample names
    *   Click on the "Process >>" button to start searching for your files.

11. Send the files to Galaxy and run a workflow:
    *   After finding your files, select the "Training_gemini_vcfanalysis_11112016" workflow by clicking on the dropdown menu.
    *   Select the file you want to send and choose the option you want to use.
    *   Then click on the "send to galaxy" button to start sending the files to a new history.
12. A cat will show up to let you know that the files are being send to Galaxy.
A checkmark will appear when the files are in galaxy and the workflow will start.
If something went wrong or you get timed-out, an error message will appear.
13. If you do not want to use a workflow you can choose "Use Galaxy" to only send the datafiles to Galaxy and work with the files directly in Galaxy.
14. You can visit the Galaxy page to see if the workflow is running by going to http://127.0.0.1:8000 or go to the next step.

# <a name="see-results"></a> See results
The following steps can be used to view the results of your histories.

1. In the bottom dropdown menu you can select the latest history and click the "see results" button to view the results of the workflow.
2. In the results page you can find the input files used to run this workflow on the left side, the analysis details are in the middle and the output files are on the right side of the page. **(If there are no output files the table will say "No output files")**
3. To download a file click the "Download" button next to the filename.
4. Select a location to save the file and open the file to view the output.
5. To go back to the homepage, click the "<< back" link or to logout click the "Logout" link.
