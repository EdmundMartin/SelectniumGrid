# Selectnium Hub
Selectnium hub works as a load balancer allowing for the load balancing of multiple Selenium hubs. The hub simply 
forwards requests, while keeping a record of the hub each session is registered to.

## Using Selenium
```python
from selenium import webdriver
from selenium.webdriver import ChromeOptions

options = ChromeOptions()
cap = options.to_capabilities()

chrome = webdriver.Remote(
          command_executor='http://0.0.0.0:8002',
          desired_capabilities=cap)

chrome.get('https://www.google.com')
print(chrome.title)

chrome.get('https://edmundmartin.com')
all_titles = chrome.find_element_by_css_selector('h2')
print(all_titles)

chrome.quit()
```
No changes to code is needed to run the hubs. Just the address of the hub being provided instead of the address of the 
underlying hub(s).