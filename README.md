# Xatu Dashboard
Generate multiple visualizations with the most current data about blobs in the Ethereum Network, and view them inside a webpage!

This dashboard generator is made to bind with a Clickhouse instance connected to [Xatu's](https://github.com/ethpandaops/xatu/) server.

You can view our instance of these plots [here](https://migalabs.io/xatu).

There is a total of **10** plots, such as **_Average blob arrival time_**, **_Blob propagation by blob count_** and **_Average used blob size_**.

Preview
---
![image](https://github.com/migalabs/xatu-dashboard/assets/114911132/75c59bef-d375-4e7e-bc34-f0bd1bfde79d)
---
# Generating a dashboard
## Before running
The generator can be run with Docker Compose (as well as serving the dashboard) or by running the script directly.

Setting up the environment variables is necessary for the generation of the dashboards. For reference, please view `/.env.example`.

Note that only Clickhouse's [native port](https://clickhouse-driver.readthedocs.io/en/latest/index.html) is supported.

## Script
Running the script directly will output the generated dashboards at `plot-generator/generated/` as HTML files.

### Install dependencies
```console
$ pip install -r plot-generator/requirements.txt
$ pip install -U python-dotenv
```

### Generate all dashboards
```console
$ python3 plot-generator/main.py
```

### Generate a specific plot
(See `plot-generator/src/builder_functions.py` for the list of plots).

The default name for the outputted dashboard in this mode is "testing.html". This template is not stylized.

To refer to a plot, use its position in the array. For example, to generate the first, second and third plots, run:
```console
$ python3 plot-generator/main.py -t 1 2 3
```
## Docker compose
```console
$ docker compose build && docker compose up
```
This will build and run the generator and server containers, which will create the dashboard at the start of every hour (as configured in `plot-generator/cron/jobs`), and serve it at the port configured inside your `.env` respectively.

The endpoint where each dashboard is located is the name of itself. For instance, the "blob" (`generated/blob.html`) dashboard will be located at `ip:port/blob`.
