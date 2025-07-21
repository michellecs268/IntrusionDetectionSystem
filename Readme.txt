Intrusion Detection System Program Guide
1. Open the terminal
2. Navigate to the directory where IDS.py is located. Ensure that the following files are present:
	- Events.txt
	- Stats.txt
	- a txt file containing new statistics
3. As this program uses scipy to generate live events, ensure that scipy is installed using either pip or pip3
	e.g. pip3 install scipy
	or pip install scipy
4. Run python IDS.py Events.txt Stats.txt <days>, where days is the number of days used to simulate training data.
	e.g. python3 IDS.py Events.txt Stats.txt 10
	or python IDS.py Events.txt Stats.txt 10
5. The program will process the initial Events and Stats files
6. When prompted, input the new statistics file
	e.g. new_stats.txt
7. When prompted, input the number of days to simulate live events
	e.g. 30
8. The program will generate daily events with anomaly counters for each day
9. Input either another statistics file in the same way as step no.6, or 'q' to exit the program