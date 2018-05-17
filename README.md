# Altering Search Results Based on User Search History
A search engine using search history to augment future search results.


# Installation requirements

This was developed and tested on Ubuntu 17.10. It should work on most Unix distro's but we make no guarentees for that.
There are features reliant on X11 running on the machine and will probably result in exceptions if this is not the case.

# Installation instructions


* Install python2.7
* Install [Elasticsearch-py](https://github.com/tweepy/tweepy) via `pip install elasticsearch`
* Install a recent version of Java

# Usage instructions

* Start up the Elasticsearch (ES) server by running `elasticsearch/elasticsearch-6.2.4/bin/elasticsearch
* Start search.py

## Indexing instructions
If you want to index your own terms on twitter you first have to install [tweepy](https://github.com/tweepy/tweepy) via `pip install tweepy`
Thereafter you have to set up a file called twitterKeys in the format: 
`consumer_key
consumer_secret
access_token
access_token_secret`. Each string should contain only the key itself and a each string should be on a separate line

Thereafter you can pipe any tokens in to indexer.py and they will be indexed by your ES.


