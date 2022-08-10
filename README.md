# **CryptoFolio**

>A personal cryptocurrency portfolio tracking application that pulls information from multiple public APIs into one quick and convenient financial overview   



## Features
* Check latest token prices and statistics 
* Log buy and sell transactions
* Get current ethereum gas fee estimations
* Read the latest industry news

## Usage
To update and view portfolio values, navigate to the program's directory and type the following in the terminal:

```python
$ python cryptofolio.py
```
To get the latest crypto industry news, run using the '-n' flag. Ctrl + Left Click on a story's URL to view the full article in your browser
```python
$ python cryptofolio.py -n
```
    
Run the program with either the '-b' or '-s' flags to enter a new buy/sell transaction
```python
$ python cryptofolio.py -b
$ python cryptofolio.py -s