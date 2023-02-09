#!/usr/bin/python3

import requests
import re
import os
import sys

def treat_url(url):

	check_url = re.search("^https:\/\/chrome\.google\.com\/webstore\/detail\/.*\/[a-zA-Z0-9]{32}$", url)

	if check_url:
		print("URL")
		ext_name = url.split('/')[5]
		ext_id = url.split('/')[6]
		yield ext_name, ext_id
	else:
		print("ERROR - INVALID INPUT")
		sys.exit()

def treat_input(arg):

	check_file = re.search("^.*\.txt$", arg)

	if check_file and os.path.isfile(arg):
		print("Text file")
		with open(arg) as f:
			for line in f:
				print(line.rstrip())
				url_generator = treat_url(line.rstrip())
				for ext_name, ext_id in url_generator:
					yield ext_name, ext_id
	else:
		print("Not text file")
		url_generator = treat_url(arg)
		for ext_name, ext_id in url_generator:
			yield ext_name, ext_id


def get_crx(ext_name, ext_id):

	crx_filename = ext_name + '.crx'
	crx_x = 'id=' + ext_id + '&installsource=ondemand&uc'
	
	cookies = {
		'NID': '511=kbP9Akj2jywBWVd78MXD_ul3aupm6fd1zqmUJ-7H_eeY9FsyWAKsaoL4lvzkk7sot6jL6uabwxoLyFJPC5ZRWolSB8M980A3CP1DzmCu7oxIk6jP7yKThJIUhKmUJFrEHArN_Q8GFgqEwLTIHoK4vLHJo84n8JPoOxioxBq0r0I',
		'AEC': 'AakniGNT4RJzcCee9888Rkbuc7DjnzbyPxhy42p3TxZAqz957PuAUVPuzwQ',
		'1P_JAR': '2023-01-06-17',
	}

	headers = {
		'authority': 'clients2.google.com',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'accept-language': 'en-US,en;q=0.9',
		# 'cookie': 'NID=511=kbP9Akj2jywBWVd78MXD_ul3aupm6fd1zqmUJ-7H_eeY9FsyWAKsaoL4lvzkk7sot6jL6uabwxoLyFJPC5ZRWolSB8M980A3CP1DzmCu7oxIk6jP7yKThJIUhKmUJFrEHArN_Q8GFgqEwLTIHoK4vLHJo84n8JPoOxioxBq0r0I; AEC=AakniGNT4RJzcCee9888Rkbuc7DjnzbyPxhy42p3TxZAqz957PuAUVPuzwQ; 1P_JAR=2023-01-06-17',
		'referer': 'https://crxextractor.com/',
		'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Linux"',
		'sec-fetch-dest': 'document',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-site': 'cross-site',
		'sec-fetch-user': '?1',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
		'x-client-data': 'CJv6ygE=',
	}

	params = {
		'response': 'redirect',
		'prodversion': '49.0',
		'acceptformat': 'crx3',
		'x': crx_x,
	}

	response = requests.get('https://clients2.google.com/service/update2/crx', params=params, cookies=cookies, headers=headers)

	crx_url = response.url
	response = requests.get(crx_url)

	crx_file = open(crx_filename, 'wb')
	crx_file.write(response.content)
	crx_file.close()

	return crx_filename


def crx_to_zip(crx_filename):

	i = 0
	zip_filename = crx_filename[:-4] + '.zip'

	with open(crx_filename, "rb") as f:
		byte1 = f.read(1)
		byte2 = f.read(1)
		while ( byte2 and not (byte1 == b'P' and byte2 == b'K')):
		    byte1 = byte2
		    byte2 = f.read(1)
		    i += 1

	with open(crx_filename, "rb") as in_file:
		with open(zip_filename, "wb") as out_file:
		    out_file.write(in_file.read()[i:])

	return zip_filename


def main():

	args = sys.argv

	if 3 <= len(args) <= 4 and args.count('-i') == 1 and args.index('-i') < len(args) - 1:
		pass
	elif len(args) == 2 and args.count('-h') == 1:
		print("Usage: python3 crxgetter.py -i file.txt/URL [-k to keep .crx file]")
		sys.exit()
	else:
		print("ERROR - INVALID USAGE")
		print("Usage: python3 crxgetter.py -i file.txt/URL [-k to keep .crx file]")
		sys.exit()
	
	crx_keep = True if args.count('-k') == 1 else False

	extensions = dict(treat_input(args[args.index('-i') + 1]))
	for key in extensions:
		print(key, '->', extensions[key])
		crx_filename = get_crx(key, extensions[key])
		zip_filename = crx_to_zip(crx_filename)
		print("Created " + zip_filename)
		if crx_keep:
			print("Preserved " + crx_filename)
		else:
			os.remove(crx_filename)


if __name__ == "__main__":
    main()

# TO-DO
# SIMPLE GETOPTS ARG PARSER
