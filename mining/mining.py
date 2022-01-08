import subprocess


def run_parser(task):
    if task in ['cities', 'restaurants', 'reviews']:
        process = 'scrapy'
        args = f'runspider tripadvisor_crawler/spiders/{task}_spider.py -t json -o - > restaurants.json'
        subprocess.run([process, args])
    else:
        print('Incorrect Task!')


if __name__ == '__main__':
    task = input()
    run_parser(task)
