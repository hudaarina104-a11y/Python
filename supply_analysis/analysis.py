import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Аналіз поставок препаратів")
    parser.add_argument("csv_file", nargs="?", default="supplies.csv", help="Шлях до CSV")
    args = parser.parse_args()

    csv_path = Path(args.csv_file)
    output_folder = csv_path.resolve().parent
    data = pd.read_csv(csv_path)

    median_quantity = np.median(data["quantity"].to_numpy())
    std_price = np.std(data["price_per_unit"].to_numpy())

    data["total_price"] = data["quantity"] * data["price_per_unit"]

    supplier_totals = data.groupby("supplier")["total_price"].sum()
    best_supplier = supplier_totals.idxmax()
    best_total = supplier_totals.max()

    
    category_totals = data.groupby("category")["quantity"].sum()

    low_supply_filename = "low_supply.csv"
    low_supply = data[data["quantity"] < 100]
    low_supply.to_csv(output_folder / low_supply_filename, index=False)

    top_three = data.sort_values(by="total_price", ascending=False).head(3)
    print("Три найдорожчі поставки:")
    print(top_three.to_string(index=False))

    
    report = (
        "ЗВІТ ПРО АНАЛІЗ ПОСТАВОК\n"
        f"Середня ціна препарату: {average_price:.2f}\n"
        f"Медіана кількості: {median_quantity:.2f}\n"
        f"Стандартне відхилення ціни: {std_price:.2f}\n"
        f"Постачальник з найбільшою сумарною вартістю: {best_supplier} ({best_total:.2f})\n"
        f"Файл з дефіцитними поставками: {low_supply_filename}\n"
        "\nСумарна кількість препаратів за категоріями:\n"
        + category_totals.to_string()
        + "\n"
    )
    (output_folder / "report.txt").write_text(report, encoding="utf-8")
    print("\n" + report)

    
    category_totals.plot(kind="bar")
    plt.title("Quantity of medicines by category")
    plt.xlabel("Category")
    plt.ylabel("Total quantity")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_folder / "categories.png")
    plt.close()
    print("Файли збережено:", low_supply_filename, "report.txt, categories.png")


if __name__ == "__main__":
    main()
