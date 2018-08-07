# House Market Monitering and Recommendation System

This project is my final year dissertation and the final report is available [here](https://www.academia.edu/s/7b571b33fb/implementation-and-study-of-k-nearest-neighbour-and-regression-algorithm-for-real-time-housing-market-recommendation-application?source=link). 

The aim of this project is to develop a real time system which can catch new properties come up from the market and provide investors property recommendation based on machine learning techniques.  

<div align=center>![google-map](https://github.com/wasamisam0119/UG_Dissertation/blob/newdev/attachment/google_map.png?raw=true)</div>

The application will allow user search areas or cities in different property types and return
a list of properties each displayed as a flag on the Google Map. The ranking is sort by the
estimated price-to-rent ratio. If user clicks on the flag, basic information will show up and
a list of neighbour properties will also be displayed. This neighbour list is a house id list
which contains 5 most similar neighbours calculated by our KNN method.

### Requirements   

Linux/OS X

Python 3.5 or above

### Installation 

See the requirements first. After you satisfy all the requirements, you can install and run like following commands:

`brew install pip`

`cd crawler/spider`

`	python install.py`

`python main.py`

Then it will start crawling and write 4 files:

1. house.json(store all the on-sale property details)
2. house_id.txt(store all the on-sale property id on zoopla)
3. sold.json(store the sold property which were in the house_id.txt)
4. crawler/dailyupdate/day-month-year_update.json(update the onsale property info)


### Architecture

<div align=center>![arch](https://github.com/wasamisam0119/UG_Dissertation/blob/newdev/images/systemdiagram.png?raw=true)</div>

