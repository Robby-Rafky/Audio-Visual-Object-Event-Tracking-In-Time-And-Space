# Audio-Visual-Object-Event-Tracking-In-Time-And-Space
Dissertation Project 

Takes an audio file and any camera source (currently linked to a wifi camera) and tracks a object given specfic parameters.
The location of the tracked object becomes the location source for the audio file to be played through the default audio output.
Depth data is extracted from the 2D frames given by the camera source via focal length and object parameters.


Uses colour thresholding to create a mask thats used for the tracking
![maskCompare](https://user-images.githubusercontent.com/58045054/194788959-70863fd9-f448-414f-87e6-6be6bc1eaf8a.PNG)


Once an object has been locked onto, the program reads only the "local frame" (the area around the tracked object) to reduce the likely hood of the tracked object being lost
![LocalArea](https://user-images.githubusercontent.com/58045054/194789340-2bda9de4-8f55-42c7-a7a6-d6939edb3d6a.PNG)
