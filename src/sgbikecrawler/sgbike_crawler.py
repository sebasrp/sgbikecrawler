import json
import click
from sgbikemart import SGBikeMart


@click.command()
@click.option("-model", "--model", help="The bike model you are interested in")
def main(model):
    crawler = SGBikeMart()
    bikes_list = crawler.retrieve_all_listings(bike_model="Yamaha")
    print(json.dumps(bikes_list, indent=4))


if __name__ == "__main__":
    main()
