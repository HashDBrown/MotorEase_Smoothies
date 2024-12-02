# MotorEase
This repo holds the code for the MotorEase accessibility testing tool.

## Purpose
MotorEase is a software testing tool aimed at detecting motor impaired user accessibility guidelines within Android applications using Screenshots and XML data from Android testing tools. Provided is the information on how to use MotorEase.

## Provenance

The MotorEase code and data is available on Github at: (https://github.com/SageSELab/MotorEase)[https://github.com/SageSELab/MotorEase]

The MotorEase code and data has been permanently archived on Zenodo at: (https://doi.org/10.5281/zenodo.10460701)[https://doi.org/10.5281/zenodo.10460701]

## Setup & Usage

- "There are three ways to build the project: using Docker within a container (recommended), building locally with Docker, or using a Python environment.

<ins>Docker instructions: </ins>

- There are 2 docker builds for this project. The ARM build for Apple Silicon and the AMD build for any other devices. You can find the images hosted on DockerHub here: 

- ARM: itsarunkv/motorease-arm

- AMD: docker pull itsarunkv/motorease-amd

- Pull your necessary image using this command: ```docker pull itsarunkv/motorease-arm``` or ```docker pull itsarunkv/motorease-amd```

<ins>Docker Image Information: </ins>

- The current docker image is built with sample Screenshot and XML data. This data is a representation of the data used in the study and provides a sample run option for the user. 

- This project uses a GloVe embedding for textual similarities. However, GloVe embedding files are large and difficult to host on GitHub. Therefore, we have created a sampleGlove.txt file within the docker container to act as a dummy GloVe model in place of a real one. This text file is formatted the exact same way as a Glove model is normally formatted.

<ins> Build 1: Running the Image with Local Build: </ins>

- With these instructions, you will be able to run the Docker Image locally and propagate your changes to the Docker Container automatically. These set of instructions are for Windows WSL. 

- This build uses the: glove.6B.100d from ```https://github.com/stanfordnlp/GloVe?tab=readme-ov-file#download-pre-trained-word-vectors```so please download the glove embedding here if you would like to use the same model.
  - Other models can be used and to use those models please change line 47 in Code/MotorEase.py .
  - This model was chosen because it simulated the same results as the original Docker Image. 

- To build the image run:
 ```bash
 docker build -t motorease Code
 ```

- To run a container of the image please run the command below. This command mounts the code directory which allows developers to have their changes propagated to docker container automatically. 
```bash
docker run -it --rm -v $(pwd)/Data:/data -v $(pwd)/Code:/code -v $(pwd)/Output:/output --env DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix motorease
``` 

- To enter a container of the image without running the command to start to program:
```bash
docker run -it --rm -v $(pwd)/Data:/data -v $(pwd)/Code:/code -v $(pwd)/Output:/output --env DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix motorease /bin/bash
``` 

- To clean up the image:
 ```bash
 docker rmi motorease
 ```

- Note 1: Depending on the Glove embedding used, you may need over 64 GB of ram
  - Docker image can easily be over 10 GB
  - When the codes failed, all the memory is still there, meaning, every time you run a 10 GB big model and fail, you have 10 GB allocated ram not released

- Note 2: The compilation is slow even with a 8-core CPU. So, you may experience a long delay when it comes to both running and building the program.

<ins> Build 2: Running the Image within Docker: </ins>

[Video Tutorial](https://drive.google.com/file/d/1FKK-Hn-CGmNpBthx0Z-T0SHbMVoSUvEp/view?usp=drive_link)

***Step 1: Add the GloVe Embeddings Path***
- Create an `embeddings` folder in the repository's root directory.
- MotorEase requires glove embeddings to work and needs the download for the model. The model is large and not able to be hosted on GitHub. Please visit https://nlp.stanford.edu/projects/glove/ and download 1 of the 4 available options.
- Add the Glove Embedding of your choice to the `embeddings` folder you created earlier.
- Navigate to line **151** in `Code/MotorEase.py`, uncomment the line, update the txt file, and comment out the original line.

***Step 2: Run the Docker Image***

- Navigate to the root directory of `MotorEase_Smoothies`.
- Use the following commands based on your platform. This command links the local `Code`, `Data`, and `embeddings` directories to the Docker container, ensuring changes in these directories reflect in the container.

**MacOS/Linux**:
```bash
docker run -it -v $(pwd)/Code:/MotorEase-main/Code -v $(pwd)/embeddings:/MotorEase-main/embeddings -v $(pwd)/Data:/MotorEase-main/Data itsarunkv/motorease-arm /bin/bash
```
 
**PowerShell**:
```bash
docker run -it -v ${PWD}/Code:/MotorEase-main/Code -v ${PWD}/embeddings:/MotorEase-main/embeddings -v ${PWD}/Data:/MotorEase-main/Data itsarunkv/motorease-amd /bin/bash
``` 

**Command Prompt**:
```bash
docker run -it -v %CD%\Code:/MotorEase-main/Code -v %CD%\embeddings:/MotorEase-main/embeddings -v %CD%\Data:/MotorEase-main/Data itsarunkv/motorease-amd /bin/bash
```

- **Note**: Replace itsarunkv/motorease-arm with itsarunkv/motorease-amd if using an AMD-based system.

- Now, any change in the `Data`, `Code`, and `embeddings` directories will show in the Docker container.

- ***To test your data, just add the PNG and corresponding XML file to the `Data` folder.***

***Step 3: Update the Scripts***
- Uncomment the Docker method code in each of these files:
  - `Code/MotorEase.py`
  - `Code/detectors/Visual/TouchTarget.py`
  - `Code/detectors/Visual/IconDistance.py`
  - `Code/detectors/Visual/UIED-master/run_single.py`

- Look for the *"Docker method"* comments in each file and uncomment those sections while commenting out the original method.

***Step 4: Install Dependencies***

- Once inside the container, install `matplotlib` using pip:
```bash
pip install matplotlib
```

***Step 5: Run the Project***

- Enter the `Code` directory in the container and run:
```bash
 python3 MotorEase.py 
```
The script will:
  1. Process data from the `Data` folder.
  2. Use the GloVe embeddings file specified on line 68.
  3. Generate an accessibility report and bar graphs for interactive and violating elements:
     - `AccessibilityReport.txt`
     - `violating_graph.png`
     - `interactive_graph.png`
     - `violating_vs_interactive.png`

***Step 6: Copy Output Files to Local Machine***
- Exit the container:
    ```bash
    exit
    ```
  - This should now take you back to the root directory of MotorEase_Smoothies.
- Create a `Results` folder in the repository's root directory.
- Copy the output files to your `Results` folder in the local directory:
    ```bash
    docker cp {container_id}:/MotorEase-main/AccessibilityReport.txt Results/
    docker cp {container_id}:/MotorEase-main/violating_graph.png Results/
    docker cp {container_id}:/MotorEase-main/interactive_graph.png Results/
    docker cp {container_id}:/MotorEase-main/violating_vs_interactive.png Results/
    ```
- Check the `Results` folder for these files.

<ins> Build 3: Python Environment: </ins>

[Video Tutorial](https://drive.google.com/file/d/1sn_aZDEI6OwyvYYORG--hA1WdCgJUlfU/view?usp=sharing)
- These set of instructions is if you would like to run the repository remotely using a Python Environment. 

Versions compatible with MotorEase:
- ```Python Version: 3.9.13```

- ```Pip Version: 23.3.2```

***Step 1: Updating the paths***

Go to line 151 in the Code/MotorEase.py file and change the file path to the folder that holds your Glove Embeddings txt file. MotorEase requires glove embeddings to work, and needs the download for the model. The model is large and not able to be hosted on GitHub. Please visit https://nlp.stanford.edu/projects/glove/ and download 1 of the 4 available options.

Go to each of the following files: motorease.py, icondistance.py, touchtarget.py, run_single.py and update the paths to the path to MotorEase root directory. You can quickly find the changes needed by ctrl+f: "Python Method". Comment out the current paths and replace the commented out path's with MotorEase Path

Files to be updated:
- `Code/MotorEase.py`: 2 paths 
- `Code/detectors/Visual/IconDistance.py`: 3 paths
- `Code/detectors/Visual/TouchTarget.py`: 5 paths
- `Code/detectors/Visual/UIED-master/run_single.py`: 1 path

**NOTE:** Using Environment: The Code directory will have a requirements.txt file that lists all required packages for MotorEase to run. 

***Step 2: creating a new python environment***
 ```bash
 python3 -m venv .venv
 ``` 
***Step 3: Once your environment is created, activate it with this command:***
 ```bash
 source .venv/bin/activate
 ```
***Step 4: Use this command to download all of the dependencies into your virtual environment:***
```bash
pip install -r Code/requirements.txt
``` 
***Step 5: Once the requirements are installed and there are PNG and XML files in the Data folder, run MotorEase from the Code directory using this command:***
 ```bash
 cd Code/
 python3 MotorEase.py
 ```
  
- The output of either method will be a file with the Motor impairment accessibility guideline violations, AccessibilityReport.txt
- The Graphed Data from the accessibility report is generated in 3 differnet Bar Graphs:
     - violating_graph.png
     - interactive_graph.png
     - violating_vs_interactive.png
  
- If you would like to run MotorEase on your own screenshot/xml pair, remove existing data in the data folder and add PNG screenshots and their XML files from a single
  application.

<ins>Reproducing Full Paper Results:</ins>

- Coming Soon, we are uploading the (large) dataset for the full reproduction. 

<ins>Adding Real GloVe Embeddings and Your Own Screen Information:</ins>

- With the inclusion of placeholder data throughout the project, we make it easy to run and check for execution. However, this tool is designed for developers to check Motor accessibility issues within their project. This requires both an authentic GloVe embedding file and screenshots (PNG files) and UI-Automator files (XML) to be in the container. This can be done using the wget command. 

- GloVe embeddings used: ```wget https://nlp.stanford.edu/data/glove.42B.300d.zip```

- Please ensure that the Glove embedding is downloaded to the /MotorEase-main/Code/ folder. When you download your GloVe embedding file, rename it to sampleGlove.txt and delete the placeholder sampleGlove.txt file so that the code can use the real embeddings. The resulting file path for the GloVe embedding file should be: ```/MotorEase-main/Code/gloveSample.txt```

- In order to load your own images, navigate to the Data folder in the container and delete the existing photos. Use the wget command to download your images into the directory so they may be used. 






## Guideline Appendix

| Accessibility Guidelines             |     Guideline Description                                  | Guideline Source | Previous Implementation                                    |    Implmeted by MotorEase                                    |
|--------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|
| Visual Touch Target Size             |    This guideline corresponds to the visual bounds of an icon without its padding. We ensure that the visual icon has a size of at least 48x48px.                                  |[40, 64] | | | x |
| Touch Target Size.                   |  This guideline looks at the bounding box of an element on the screen and requres the bounding box irrespective of the icon size, to be a minimum of 48x48px.                                    |[2, 8, 9, 11, 17, 20, 27, 38, 40, 62] | x |  |
| Persistent Elements                  |  This guideline requires elements that appear across multiple screens to remain in a similar general locations across screens. This makes it easier for users to anticipate where an icon may be.                                    |[2, 9, 11] |  | x |
| Clickable Span                       |    This guideline requires elements that can be interacted with are large enough. this includes text with hyperlinks as well.                                   |[20] | x |  |
| Duplicate Bounds                     |   This guideline looks at bounding boxes for elements on the screen and suggests that developers not have any elements that may share identical bounding boxes, or have an element with two bounding boxes of the same size.                                   |[20]  |  |  |
| Editable Item Descriptions           |  Editable items like text fields and date windows need descriptions to let users know that they can be interacted with and can be edited.                                     |[20, 34] | x |  |
| Expanding Section Closure            | This guideline requires sections such as pop-ups and lists to be closable using a visual icon that implies closure. This eliminates the need to close a section using a gesture.                                      |[2, 8, 9, 11] |  | x |
| Non-Native Elements                  |    This guideline requires developers to use native tools in the construction of their application in order to be compatible with native assistive features.                                 |[8, 27]  |  x |  |
| Visual Icon Distance                 |  This guideline looks at the visual distance between any given icons on the screen. It requires icons to be a minimum of 8px in distance to aboid mistaps.                                    |[11, 17, 62, 80]  |   | x |
| Labeled Elements                     | This guideline requires elements to have metadata descriptions of the icon and its functionality so that assistive measures such as VoiceOver can vocalize these functionalities.                                       |[20, 34, 35, 41] |  x |  |
| Captioning                           |  Captioning refers to image, audio, and video captioning requirements in the metadata. It requires  media to have a label in order for assistive services to explain the content to the user.                                   |[1, 2, 5, 8, 9, 11, 38, 41, 66, 70]  |  x |  |
| Keyboard Navigation                  | This guideline suggest developers to design interfaces that can be traveresd using a keyboard without needing gestures and complex taps.                                      |[1, 5, 30, 35, 41] |  x |  |
| Traversal Order                      |  This guideline sggests that interfaces that use keyboard navigation need to have a proper and logical traversal order of elements on the screen. An example of this is using the "tab" key to traverse elements on the screen.                                    |[1, 20, 35]  |  x |  |
| Motion Activation                    |  This guideline requires an alternate mode of interaction if motion is used to perform some action.                                     |[2, 8, 9] |   |  |
| Wide gaps between related information| This guideline suggest that related info across the screen should not be scattered so that if a user needs to perform an action related to some information, the action may not be in the same general location                                  | [27]  |  x |  |
| Facial Recognition                   | This guideline checks to see if facial recognition can be used for unlock functions within applications, not requiring motor impaired users to type out a password                                    |[22, 27]  |  x |  |
| Single Tap Navigation                | Single tap navigation requires a single tap traversal of an app while achieving the same functionality. For example: swiping to delete a row in a list must be accomplished through a series of taps that can aid in deleting the row.                                     | [2, 8, 9, 11, 35, 53]| | |
| Poor form design/instructions        | This guideline suggests developers to design forms that have proper traversals and editable descriptions. It also suggests proper distances between form fields.                                       |[1, 5]| | |

## Apps Used
| Name | Package | GooglePlayLink | Downloads | Stars |
|------|---------|----------------|----------|-------|
| Zeus  | app.zeusln.zeus | https://play.google.com/store/apps/details?id=app.zeusln.zeus | 1000 | 4 |
| Rocket.Chat  | chat.rocket.android | https://play.google.com/store/apps/details?id=chat.rocket.android | 500000 | 4.2 |
| Rootless Pixel Launcher  | amirz.rootless.nexuslauncher | https://play.google.com/store/apps/details?id=amirz.rootless.nexuslauncher | 1000000 | 4.2 |
| MTG Familiar  | com.gelakinetic.mtgfam | https://play.google.com/store/apps/details?id=com.gelakinetic.mtgfam | 500000 | 4.4 |
| Launcher  | com.finnmglas.launcher | https://play.google.com/store/apps/details?id=com.finnmglas.launcher | 5000 | 4.1 |
| Library  | com.cgogolin.library | https://play.google.com/store/apps/details?id=com.cgogolin.library | 10000 | 3.4 |
| Simple ToDo  | apps.jizzu.simpletodo | https://play.google.com/store/apps/details?
 id=apps.jizzu.simpletodo&pcampaignid=MKT-Other-
 global-all-co-prtnr-py-PartBadge-Mar2515-1 | 10000 | 4.5 |
| SmartCookieWeb  | com.cookiegames.smartcookie | https://play.google.com/store/apps/details?id=com.cookiegames.smartcookie&pcampaignid=pcampaignidMKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1 | 50000 | 3.9 |
| PCAPdroid  | com.emanuelef.remote_capture | https://play.google.com/store/apps/details?id=com.emanuelef.remote_capture | 10000 | 4.3 |
| Rview  | com.ruesga.rview | https://play.google.com/store/apps/details?id=com.ruesga.rview | 5000 | 4.7 |
| Converter NOW  | com.ferrarid.converterpro | https://play.google.com/store/apps/details?id=com.ferrarid.converterpro | 1000 | 4.7 |
| APKShare  | be.brunoparmentier.apkshare | https://play.google.com/store/apps/details?id=be.brunoparmentier.apkshare | 1000 | 4.3 |
| DNS Hero  | com.gianlu.dnshero | https://play.google.com/store/apps/details?id=com.gianlu.dnshero&pcampaignid=MKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1 | 5000 | 4 |
| Shaarlier  | com.dimtion.shaarlier | https://play.google.com/store/apps/details?id=com.dimtion.shaarlier | 1000 |  |
| Pdf Viewer Plus  | com.gsnathan.pdfviewer | https://play.google.com/store/apps/details?id=com.gsnathan.pdfviewer | 10000 | 4.6 |
| Taskbar  | com.farmerbb.taskbar | https://play.google.com/store/apps/details?id=com.farmerbb.taskbar | 1000000 | 4.4 |
| Seafile  | com.seafile.seadroid2 | https://play.google.com/store/apps/details?id=com.seafile.seadroid2 | 100000 | 3.8 |
| K-9 Mail  | com.fsck.k9 | https://play.google.com/store/apps/details?id=com.fsck.k9 | 5000000 | 3.9 |
| Gotify  | com.github.gotify | https://play.google.com/store/apps/details?id=com.github.gotify | 5000 | 4.7 |
| RGB Tool  | com.fastebro.androidrgbtool | https://play.google.com/store/apps/details?id=com.fastebro.androidrgbtool | 10000 | 4.1 |
| NoSurf for reddit  | com.aaronhalbert.nosurfforreddit | https://play.google.com/store/apps/details?id=com.aaronhalbert.nosurfforreddit | 1000 | 4.5 |
| Simple Scrobbler  | com.adam.aslfms | https://play.google.com/store/apps/details?id=com.adam.aslfms&pcampaignid=MKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1 | 500000 | 3.5 |
| Look4Sat  | com.rtbishop.look4sat | https://play.google.com/store/apps/details?id=com.rtbishop.look4sat | 10000 | 4.3 |
| Lightning  | acr.browser.lightning | https://play.google.com/store/apps/details?id=acr.browser.lightning | 10000 | 4 |
| Movian Remote  | com.claha.showtimeremote | https://play.google.com/store/apps/details?id=com.claha.showtimeremote | 10000 | 4 |
| MHWorld Database  | com.gatheringhallstudios.mhworlddatabase | https://play.google.com/store/apps/details?id=com.gatheringhallstudios.mhworlddatabase | 100000 | 4.7 |
| Just (Video) Player  | com.brouken.player | https://play.google.com/store/apps/details?id=com.brouken.player | 10000 | 4.2 |
| Com-Phone Story Maker  | ac.robinson.mediaphone | https://play.google.com/store/apps/details?id=ac.robinson.mediaphone | 50000 | 3.8 |
| OpenDocument Reader  | at.tomtasche.reader | https://play.google.com/store/apps/details?id=at.tomtasche.reader | 5000000 | 4 |
| ImgurViewer  | com.ensoft.imgurviewer | https://play.google.com/store/apps/details?id=com.ensoft.imgurviewer | 10000 | 4.6 |
| Torchlight  | com.secuso.torchlight2 | https://play.google.com/store/apps/details?id=com.secuso.torchlight2 | 1000 | 4.6 |
| Aria2Android  | com.gianlu.aria2android | https://play.google.com/store/apps/details?id=com.gianlu.aria2android&pcampaignid=MKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1 | 5000 | 4.6 |
| arXiv eXplorer - Mobile App for arXiv.org  | com.gbeatty.arxiv | https://play.google.com/store/apps/details?id=com.gbeatty.arxiv&pcampaignid=MKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1 | 10000 | 4.7 |
| Track & Graph  | com.samco.trackandgraph | https://play.google.com/store/apps/details?id=com.samco.trackandgraph | 10000 | 4.2 |
| Vectorify da home!  | com.iven.iconify | https://play.google.com/store/apps/details?id=com.iven.iconify | 10000 | 4.5 |
| RxDroid  | at.jclehner.rxdroid | https://play.google.com/store/apps/details?id=at.jclehner.rxdroid | 10000 | 4.5 |
| Hangar  | ca.mimic.apphangar | https://play.google.com/store/apps/details?id=ca.mimic.apphangar | 100000 | 4.1 |
| Man Man  | com.adonai.manman | https://play.google.com/store/apps/details?id=com.adonai.manman | 5000 | 4.5 |
| Nock Nock  | com.afollestad.nocknock | https://play.google.com/store/apps/details?id=com.afollestad.nocknock&utm_source=global_co&utm_medium=prtnr&utm_content=Mar2515&utm_campaign=PartBadge&pcampaignid=MKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1 | 1000 | 4.7 |
| RethinkDNS  | com.celzero.bravedns | https://play.google.com/store/apps/details?id=com.celzero.bravedns | 10000 |  |

