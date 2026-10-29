import pandas as pd
import matplotlib.pyplot as plt

df =pd.read_excel(
    "Online_Retail_Practice.xlsx",
    sheet_name="Online Retail"
)

print(df.head())
print(df.shape)
print(df.isnull().sum())

df = df.drop(columns=['Unnamed: 8','revenue','Total revenue'])
print(df.shape)
print(df.isnull().sum())

while True:
    try:
        rows= int(input("How many rows do you want to research:"))

        if rows >0:
            break
        print("please enter a positive integer")

    except ValueError:
        print("the entered value is wrong, please enter a positive integer")

df = df.head(rows).copy()
print(f"Rows selected for analysis: {len(df)}")
print('number of duplication rows:')
print(df.duplicated(keep=False).sum())

duplicates = df[df.duplicated(keep=False)]
print(duplicates.head(rows))

#choose whether delate
while True:
    option = input('do you want to remove the duplicate rows?(y/n): ').strip().lower()

    if option == 'y' or option == 'n':
        break

    print('Your option is invalid. Please enter y or n.')

if option == 'y':
    df_remove = df.drop_duplicates().copy()
else:
    df_remove = df.copy()
print(f'row after section is {len(df_remove)}')


#choose what they want
df_remove["Revenue"] = df_remove["Quantity"] * df_remove["UnitPrice"]
while True:
    country = (input("which country do you want search：")).strip()
    result = df_remove[
        df_remove["Country"].str.title() == country.title()
    ]

    if not result.empty:
        break

    print(f'country: {country} is unavailable, please enter another country.')

#word input fix

if result.empty:
    print("Country not found")
else:
    print(result.head(rows))
    print(f'total search result {len(result)}')

    total_revenue = result["Revenue"].sum()
    print(f'total revenue: {total_revenue:,.3f}')

    unique_invoices = result["InvoiceNo"].nunique()
    print(f'unique invoices: {unique_invoices}')

    if unique_invoices > 0:
        average_invoices_value = total_revenue / unique_invoices
        print(f"Average Invoice Value: £{average_invoices_value:,.2f}")
    else:
        print("Average Invoice Value unavailable: no valid invoices.")

    negative_records = df_remove[df_remove['Quantity']<0]
    print(f"negative_quantity records:{len(negative_records)}")
    print(negative_records.head(rows))

    sales = df_remove[
        (df_remove ['Quantity']>0) &
        (df_remove ['UnitPrice']>0)
    ]

    print(sales.head(rows))

    total_units_number = sales["Quantity"].sum()
    print(f'total_units_number is: {total_units_number:,.3f}')

    gross_sales = sales["Revenue"].sum()
    print(f"Gross_sales is:{gross_sales:,.3f}")

    returns = df_remove[
        (df_remove['Quantity']<0) &
        (df_remove['UnitPrice']>0)
    ]

    returns_amount = abs(returns["Revenue"].sum())
    print(f'returns_amount is:{returns_amount:,.3f}')

    net_revenue = gross_sales - returns_amount
    print(f'net_revenue is:{net_revenue:,.3f}')

    check_revenue = df_remove["Revenue"].sum()
    print(f'check_revenue is:{check_revenue:,.3f}')

    adjusting_different = abs(net_revenue - check_revenue)
    print(f'adjusting_different is:{adjusting_different:,.3f}')

    if adjusting_different <= 0.001:
        print('Pass:the net_revenue available')
    else:
        print('False:the net_revenue need to check')
        negative_price = df_remove[df_remove['UnitPrice']<0] #negative_price means the count didn't satisfy any condition before
        negative_price_amount = abs(negative_price["Revenue"].sum())
        print(f'the special negative_price_amount is{negative_price_amount:,.3f}')

        print(negative_price[["InvoiceNo", "Description", "Quantity", "UnitPrice", "Revenue"]])

        adjustment = negative_price["Revenue"].sum()

        if abs(net_revenue + adjustment - check_revenue) <= 0.001:
            print('Pass:Revenue difference explained')
        else:
            print('False:Unexplained difference remains')

    bad_debt_records = df_remove[
        df_remove["Description"].eq("Adjust bad debt") &
        (df_remove["UnitPrice"] < 0)
        ]

    bad_debt = bad_debt_records["Revenue"].sum()
    print(f"Bad Debt Adjustment: £{bad_debt:,.3f}")

    total_net_transaction_amount = check_revenue
    print(f"Total Net Transaction Amount: £{total_net_transaction_amount:,.3f}")

    cancellation_stuff = df_remove[
        df_remove["InvoiceNo"].astype(str).str.startswith("C")
    ]
    print(f"Cancellation Records: {len(cancellation_stuff)}")
    print(cancellation_stuff.head(rows))

    all_negative = (cancellation_stuff["Quantity"] < 0).all()
    print(f"All cancellations have negative quantity: {all_negative}")

    other_negative = df_remove[
       (df_remove["Quantity"] < 0) &
       (~df_remove["InvoiceNo"].astype(str).str.startswith("C"))
    ]
    all_zero_price = (other_negative["UnitPrice"] == 0).all()
    print(f"All other negative records have zero price: {all_zero_price}")

    while True:
        chart_option = input(
            "Choose chart analysis: A = Overall, B = Selected Country: "
        ).strip().lower()

        if chart_option == "a" or chart_option == "b":
            break

        print("Invalid option. Please enter A or B.")

    if chart_option == "a":
        chart_data = df_remove
    else:
        chart_data = result

    country_sales = chart_data.groupby("Country")["Revenue"].sum()
    country_ranking = country_sales.sort_values(ascending=False)

    print(country_ranking.head(rows))

    product_sales = chart_data[
        (chart_data["Quantity"] > 0) &
        (chart_data["UnitPrice"] > 0)
        ].groupby("Description")["Revenue"].sum()
    product_ranking = product_sales.sort_values(ascending=False)

    print(product_ranking.head(rows))

    # Chart 1: Countries by Net Transaction Amount

    top_countries = country_ranking.head(10)

    plt.figure(figsize=(12, 6))

    plt.bar(
        top_countries.index,
        top_countries.values
    )

    if chart_option == "a":
        plt.title(f"Top {len(top_countries)} Countries by Net Transaction Amount")
    else:
        plt.title(f"Net Transaction Amount - {country.title()}")

    plt.xlabel("Country")
    plt.ylabel("Net Transaction Amount (£)")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(
        f"country_sales_{chart_option}_{country.lower().replace(' ', '_')}_{len(df)}.png",
        dpi=300
    )
    plt.show()

    print("Country sales chart saved successfully!")

    # Chart 2: Products by Gross Revenue

    top_products = product_ranking.head(10)

    plt.figure(figsize=(12, 7))

    plt.barh(
        top_products.index[::-1],
        top_products.values[::-1]
    )

    if chart_option == "a":
        plt.title(f"Top {len(top_products)} Products by Gross Revenue - Overall")
    else:
        plt.title(f"Top {len(top_products)} Products by Gross Revenue - {country.title()}")

    plt.xlabel("Gross Revenue (£)")
    plt.ylabel("Product")

    plt.tight_layout()

    plt.savefig(
        f"product_sales_{chart_option}_{country.lower().replace(' ', '_')}_{len(df)}.png",
        dpi=300
    )
    plt.show()

    print("Product sales chart saved successfully!")

    # PROJECT COMPLETION MESSAGE

    print("\n===================================")
    print("ONLINE RETAIL DATA ANALYSIS")
    print("===================================")

    print("Data processing completed.")
    print("Sales analysis completed.")
    print("Country ranking completed.")
    print("Product ranking completed.")
    print("Visualizations saved successfully.")

    print("===================================")





