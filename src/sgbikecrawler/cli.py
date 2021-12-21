import json
import csv

import click
from sgbikecrawler import SGBikeCrawler


@click.command()
@click.option("--csv", is_flag=True, help="Outputs results to csv")
@click.option(
    "--terminal", is_flag=True, help="Outputs results to terminal", default=False
)
@click.option("--max", "max_", help="Maximum price of the listing", default="")
@click.option("--min", "min_", help="Minimum price of the listing", default="")
@click.option("-m", "--model", help="The bike model you are interested in")
def main(model, min_, max_, terminal, csv):
    bikes_list = SGBikeCrawler.retrieve_all_listings(
        bike_model=model, price_min=min_, price_max=max_
    )

    if csv:
        generate_csv(bikes_list)

    if terminal:
        print(json.dumps(bikes_list, indent=4))


def generate_csv(bikes_list):
    if len(bikes_list) <= 0:
        print("bike listings empty... skipping")
        return

    keys = bikes_list[0].keys()
    with open("bike_ads.csv", "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(bikes_list)


if __name__ == "__main__":
    main()
