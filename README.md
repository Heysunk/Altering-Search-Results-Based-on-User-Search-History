# PersonalizedElasticSearch
A search engine using previous results to augment future results.


# Installation requirements

This was developed and tested on Ubuntu 17.10. It should work on most Unix distro's but we make no guarentees for that.
There are features reliant on X11 running on the machine and will probably result in exceptions if this is not the case.

# Installation instructions


* Install python2.7
* Install [tweepy](https://github.com/tweepy/tweepy) via `pip install tweepy`
* Install [Elasticsearch-py](https://github.com/tweepy/tweepy) via `pip install elasticsearch`
* Install a recent version of Java

# Usage instructions

* Start up the Elasticsearch (ES) server by running `elasticsearch/elasticsearch-6.2.4/bin/elasticsearch
* Start search.py

## Indexing instructions
If you want to index your own terms on twitter you can pipe any tokens in to indexer.py.
Using indexer.py requires you to set up your own keys in a file called twitterKeys.


