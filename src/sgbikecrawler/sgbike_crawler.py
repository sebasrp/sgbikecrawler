import json
import csv

import click
from sgbikemart import SGBikeMart


@click.command()
@click.option("--csv", is_flag=True, help="Outputs results to csv")
@click.option("--terminal", is_flag=True, help="Outputs results to terminal")
@click.option("-m", "--model", help="The bike model you are interested in")
def main(model, terminal, csv):
    crawler = SGBikeMart()
    bikes_list = crawler.retrieve_all_listings(bike_model="Yamaha FZ")

    if csv:
        generate_csv(bikes_list)

    if terminal:
        print(json.dumps(bikes_list, indent=4))


def generate_csv(bikes_list):
    keys = bikes_list[0].keys()  # assumes all items are same dicts
    with open("bike_ads.csv", "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(bikes_list)


if __name__ == "__main__":
    main()
