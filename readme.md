# House Market Monitering and Recommendation

### Requirements   

Linux/OS X

Python 3.5 or above

Pip

### Installation 

See the requirements first. After you satisfy all the requirements, you can install and run like following commands:

`cd crawler/spider`

`	python install.py`

`python main.py`

Then it will start crawling and write 4 files:

1. house.json(store all the on-sale property details)
2. house_id.txt(store all the on-sale property id on zoopla)
3. sold.json(store the sold property which were in the house_id.txt)
4. crawler/dailyupdate/day-month-year_update.json(update the onsale property info)

