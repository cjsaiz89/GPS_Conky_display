# GPS_Conky_display

Displays GPS information (streamed by an UDP network) and displays it in Conky for Linux.
If there is a list of targets with their Lat and Lon position, it will also display de distance and time to reach the target.

**INSTRUCTIONS**

1-Create a target file with the correct format:
target_id name lat lon 
(i.e. 1 CTD1 25.145 -30.256)

2-Define working directories and filenames in mypositionV4.1.py:
gps_file = '/home/user/Downloads/gps_stream'
target_file = '/home/user/Downloads/targets_gps'
gps_output = '/home/user/Downloads/gps_output'
files don't need to have an extension, but any like .txt works as well

3-Define the target id number to display distance and time to the target
tgt_id = 11
this will display dist and time to target_id number 11

4-Save and close mypositionV4.1.py

5-Edit the Conky config file:
Add the following line at the end:
${color magenta} ${exec cat /home/user/Downloads/gps_output}
Make sure the path points to the gps_output file. This 'cat' command reads the content of the file gps_output to display in Conky
Define the text color you want.

6-Open the linux terminal (CTRL+ALT+t) and create a crontab to execute script on a schedule:
EDITOR=nano crontab -e
Add this line: 
"* * * * * python /home/user/Desktop/mypositionV4.1.py" 
To execute the python script every minute
Make sure the path to the script is correct or it won't be executed.

7-Remember to update the target ID on the mypositionV4.1.py
if there's no targets_gps use tgt_id='' to skip distance and time line.
