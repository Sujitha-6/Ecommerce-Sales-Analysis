import os
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from dotenv import load_dotenv

load_dotenv()

connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT"))
)
os.makedirs("../charts", exist_ok=True)

# Common chart settings
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 16
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 11


# --------------------------------
# 2. Monthly Sales Trend
# --------------------------------

query1 = """
SELECT
    YEAR(o.order_purchase_timestamp) AS sales_year,
    MONTH(o.order_purchase_timestamp) AS sales_month,
    ROUND(SUM(oi.price), 2) AS monthly_revenue
FROM orders_fixed_sql o
INNER JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY
    YEAR(o.order_purchase_timestamp),
    MONTH(o.order_purchase_timestamp)
ORDER BY sales_year, sales_month;
"""

df = pd.read_sql(query1, connection)

df["month"] = (
    df["sales_year"].astype(str) + "-" +
    df["sales_month"].astype(str).str.zfill(2)
)

fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(
    df["month"],
    df["monthly_revenue"],
    marker="o",
    linewidth=2.5,
    markersize=6,
    color="#2878B5"
)

ax.set_title("Monthly Sales Revenue Trend", pad=18)
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (BRL)")

ax.tick_params(axis="x", rotation=45)
ax.yaxis.set_major_formatter(
    ticker.StrMethodFormatter("{x:,.0f}")
)

ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("../charts/monthly_sales_trend.png", dpi=300, bbox_inches="tight")
plt.show()


# --------------------------------
# 3. Top 10 Product Categories
# --------------------------------

query2 = """
SELECT
    p.product_category_name,
    ROUND(SUM(oi.price), 2) AS revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY revenue DESC
LIMIT 10;
"""

df2 = pd.read_sql(query2, connection)

df2 = df2.sort_values("revenue", ascending=True)

fig, ax = plt.subplots(figsize=(12, 7))

bars = ax.barh(
    df2["product_category_name"],
    df2["revenue"],
    color="#43A581"
)

ax.set_title("Top 10 Product Categories by Revenue", pad=18)
ax.set_xlabel("Revenue (BRL)")
ax.set_ylabel("Product Category")

ax.xaxis.set_major_formatter(
    ticker.StrMethodFormatter("{x:,.0f}")
)

ax.bar_label(
    bars,
    labels=[f"{v:,.0f}" for v in df2["revenue"]],
    padding=5,
    fontsize=9
)

ax.grid(axis="x", linestyle="--", alpha=0.4)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("../charts/top_categories.png", dpi=300, bbox_inches="tight")
plt.show()


# --------------------------------
# 4. Payment Method Distribution
# --------------------------------

query3 = """
SELECT
    payment_type,
    COUNT(*) AS payment_count
FROM order_payments
GROUP BY payment_type
ORDER BY payment_count DESC;
"""

df3 = pd.read_sql(query3, connection)

fig, ax = plt.subplots(figsize=(10, 7))

wedges, _, autotexts = ax.pie(
    df3["payment_count"],
    labels=None,
    autopct="%1.1f%%",
    startangle=90,
    pctdistance=0.72,
    textprops={"fontsize": 10, "weight": "bold"},
    wedgeprops={"edgecolor": "white", "linewidth": 2}
)

ax.set_title("Payment Method Distribution", pad=18)

legend_labels = [
    f"{row.payment_type}: {row.payment_count:,}"
    for row in df3.itertuples()
]

ax.legend(
    wedges,
    legend_labels,
    title="Payment Methods (Count)",
    loc="center left",
    bbox_to_anchor=(1, 0.5)
)

ax.axis("equal")

plt.tight_layout()
plt.savefig("../charts/payment_distribution.png", dpi=300, bbox_inches="tight")
plt.show()


# --------------------------------
# 5. Customer Distribution by State
# --------------------------------

query4 = """
SELECT
    customer_state,
    COUNT(DISTINCT customer_unique_id) AS customer_count
FROM customers
GROUP BY customer_state
ORDER BY customer_count DESC;
"""

df4 = pd.read_sql(query4, connection)

df4 = df4.sort_values("customer_count", ascending=True)

fig, ax = plt.subplots(figsize=(12, 9))

bars = ax.barh(
    df4["customer_state"],
    df4["customer_count"],
    color="#E5A34A"
)

ax.set_title("Customer Distribution by State", pad=18)
ax.set_xlabel("Number of Customers")
ax.set_ylabel("State")

ax.xaxis.set_major_formatter(
    ticker.StrMethodFormatter("{x:,.0f}")
)

ax.bar_label(
    bars,
    labels=[f"{v:,.0f}" for v in df4["customer_count"]],
    padding=4,
    fontsize=8
)

ax.grid(axis="x", linestyle="--", alpha=0.4)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("../charts/customer_distribution.png", dpi=300, bbox_inches="tight")
plt.show()


# --------------------------------
# 6. Top 10 Sellers by Revenue
# --------------------------------

query5 = """
SELECT
    oi.seller_id,
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM order_items oi
GROUP BY oi.seller_id
ORDER BY total_revenue DESC
LIMIT 10;
"""

df5 = pd.read_sql(query5, connection)

df5 = df5.sort_values("total_revenue", ascending=True)

fig, ax = plt.subplots(figsize=(12, 7))

bars = ax.barh(
    df5["seller_id"].str[:8],
    df5["total_revenue"],
    color="#9273B5"
)

ax.set_title("Top 10 Sellers by Revenue", pad=18)
ax.set_xlabel("Revenue (BRL)")
ax.set_ylabel("Seller ID (First 8 Characters)")

ax.xaxis.set_major_formatter(
    ticker.StrMethodFormatter("{x:,.0f}")
)

ax.bar_label(
    bars,
    labels=[f"{v:,.0f}" for v in df5["total_revenue"]],
    padding=5,
    fontsize=9
)

ax.grid(axis="x", linestyle="--", alpha=0.4)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("../charts/seller_performance.png", dpi=300, bbox_inches="tight")
plt.show()


# --------------------------------
# 7. Close MySQL Connection
# --------------------------------

connection.close()

print("All 5 visualizations completed successfully!")
