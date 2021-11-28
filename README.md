# CTFd cli
A small tool for taking CTFd challenges from a folder and inserting into a CTFd instance.

Usage is as depicted:
```
usage: ctfd.py [-h] [--token TOKEN] [--url URL] path

positional arguments:
  path           directory to traverse for challenges

optional arguments:
  -h, --help     show this help message and exit
  --token TOKEN  the access token for the API access, e.g. d41d8cd98f00b204e9800998ecf8427e
  --url URL      url to the instance, e.g. https://demo.ctfd.io. Without trailing slash
```

## Challenge structure
Challenges should be organized into directories resempling the categories. For example, if you have a challenge named *some-cool-challenge* in the *web* category, then put the challenge in the folder */web/some-cool-challenge*. 

Sample directories for two different challenges:
```
/web/some-cool-challenge/ctfd.json
/crypto/aes-for-beginners/ctfd.json
```

The ctfd.json file is a json-formattet file with meta-description for the challenge. The `downloadable_files` is optional and will take files from the folder and make them available for download. 
```json
{
  "flag": "CTF{the_actual_flag_here}",
  "title": "The Public Title Displayed in CTFd",
  "description": "The challenge description goes here."
  "downloadable_files": [
     "source.zip"
  ]
}
```
