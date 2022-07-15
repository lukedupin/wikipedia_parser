from fox_parser import FoxParser
from msn_parser import MsnParser
import csv
import multiprocessing as mp
import urllib.request

#Description: Open the CSV file of targets (line delimited) and create a list of URL's to parse
def get_url_list( target_path ):
    with open(target_path,'r') as f:
        reader = csv.reader(f)
        url_list = list(reader)
        f.close()
        return url_list

#Description: Get the raw content data for a URL from the internet
def download_file_from_url(url):
    raw_data = None
    try:
        with urllib.request.urlopen(url) as f:
            raw_data = f.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(e.reason)
    return raw_data

#Description: accept data in a queue to write to a single file.  We are using this function so that multiple
# processes cannot write to the same file at the same time
def file_writer( write_queue, dump_path ):
    while True:
        data = write_queue.get()
        if(data == 'kill'):
            return
        with open(dump_path,'a') as f:
            f.write(data)
            f.write('\n\n\n')
            f.close()

#Description: from a url, donwload the content, use the appropriate parser, and queue the data to be written to disc
def parse_html( url, type, write_queue ):

    raw_data = download_file_from_url(url)

    if type == 'msn':
        parser = MsnParser()
    elif type == 'fox':
        parser = FoxParser()
    else:
        print("invalid parser type")
        return

    parser.feed( raw_data )
    parsed_data = parser.get_data()
    write_queue.put(parsed_data)

    print("Successfully parsed: "+str(url))


def parse_all_urls( url_list, type, dump_path ):

    #only use 50% of the available threads on system, to avoid taxing the machine too much
    process_count = int(mp.cpu_count()*0.5)

    #This queue is used to handle incoming parsed data to write to a single file.
    #We are using a queue so that we don't end up having multiple processes writing to the same file at once.
    manager = mp.Manager()
    write_queue = manager.Queue()

    #Create a pool of processes to parse each URL in the list
    with mp.Pool(processes=process_count) as pool:
        pool.apply_async(file_writer, (write_queue, dump_path))
        pool.starmap(parse_html, [(url[0], type, write_queue) for url in url_list])
        write_queue.put('kill')
        pool.close()
        pool.join()







#PROGRAM BEGINS HERE
if __name__ == '__main__':

    #Get command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="extract data from html files via a url")
    parser.add_argument("target_path", type=str, help="path to CSV file with target URL links")
    parser.add_argument("--type", type=str,required=True, help="Choose the type of webpage to parse. Currently options are: msn or fox")
    parser.add_argument("--dump", type=str,required=True, help="path to file where data will be dumped")


    args = parser.parse_args()

    if not (args.type == "msn" or args.type == "fox"):
        print("Please specify a supported webpage type.  Choices are: msn, fox")
        print("You chose: "+str(args.type))
        exit(1)


    #Read input file as CSV to get list of target URL's
    url_list = get_url_list(args.target_path)

    #Parse the URL's
    parse_all_urls( url_list, args.type, args.dump )
