# OptChain: AWS Deployment Guide

Welcome! This guide will help you deploy the **OptChain** system onto Amazon Web Services (AWS) EC2 servers. We have automated most of the hard work using Docker and Python scripts.

Follow these steps one by one to set up your environment, configure your settings, and run your experiments.

## 📋 Prerequisites

Before you begin, please ensure you have the following installed on your local computer:

* **Python 3.x**
* **Pip** (Python package manager)
* **AWS CLI** (configured with your credentials)

---

## 📂 Project Structure

Ensure your project folder looks like this before starting. It will help you navigate the instructions below.

```text
.
├── AWS_key/               <-- Put your .pem key files here
├── exper/
│   └── optchain/          <-- Experiment configurations go here
├── instances.json         <-- List of your AWS IP addresses
├── requirements.txt       <-- Python dependencies
├── run_experiment.sh      <-- The main script to start experiments
├── setup_env.py           <-- Script to install Docker on remote servers
└── read_log.py            <-- Script to view results

```

---

## Step 1: Install Dependencies

First, we need to install the software libraries required to control the AWS servers from your local machine.

Open your terminal in the project folder and run:

```bash
pip3 install -r requirements.txt

```

---

## Step 2: Prepare SSH Keys

We need a digital "key" to securely talk to the AWS servers.

1. Locate your AWS key pair file (usually ends in `.pem`).
2. Create a folder named `AWS_key` in the main directory if it doesn't exist.
3. Move your `.pem` file inside that folder.

*Note: Make sure your key file name matches what you use in the `instances.json` later.*

---

## Step 3: Configure AWS Nodes (`instances.json`)

We need to give the system an "address book" so it knows where your servers are located around the world.

Open the file named `instances.json`. This file organizes your servers by **Region** (like Virginia, London, etc.). For each region, you must provide:

1. **`ssh_key`**: The path to the key file you moved in Step 2.
2. **`ips`**: A list of the IP addresses for that specific region.

**Make sure your file looks exactly like this structure:**

```json
{
  "user": "ubuntu",
  "instances": [
    {
      "region": "Virginia",
      "ssh_key": "./AWS_key/Virginia.pem",
      "ips": [
        "18.215.189.60",
        "35.171.203.150",
        "44.200.197.12",
        "..."
      ]
    },
    {
      "region": "London",
      "ssh_key": "./AWS_key/London.pem",
      "ips": [
        "13.41.247.194",
        "18.130.179.86",
        "3.8.151.11",
        "..."
      ]
    },
    {
      "region": "Tokyo",
      "ssh_key": "./AWS_key/Tokyo.pem",
      "ips": [
        "54.199.250.14",
        "13.112.161.107",
        "52.197.73.99",
        "..."
      ]
    },
    {
      "region": "Saopaulo",
      "ssh_key": "./AWS_key/Saopaulo.pem",
      "ips": [
        "52.67.138.154",
        "54.233.71.60",
        "18.231.110.223",
        "..."
      ]
    }
  ]
}

```

### ⚠️ Important Checks:

* **Username:** Ensure `"user": "ubuntu"` is at the top. This is the standard username for AWS servers.
* **Key Locations:** Ensure you actually have files named `Virginia.pem`, `London.pem`, etc., inside your `AWS_key` folder.
* **Commas:** Notice that every item has a comma `,` at the end, **except** for the very last item in a list. If you miss a comma, the program will crash!

---

## Step 4: Set Up Remote Environments

Now we will prepare the remote AWS servers. This script automatically installs Docker, pulls the OptChain image, and sets up network bandwidth limits on every server listed in `instances.json`.

Run this command and wait for it to finish:

```bash
python3 setup_env.py
```

*Tip: This might take a few minutes depending on the number of servers.*

---

## Step 5: Configure the Experiment

Now we define **how** the blockchain should behave.

1. Navigate to the folder `./exper/optchain/`.
2. Create a new folder for your specific experiment ID. For example: `exper_0`.
3. Inside that folder, create or edit the configuration file (usually `config.json`).

Below is an example configuration. You can modify parameters like `shard_num` (number of shards) or `block_size`.

```json
{
  "shard_num": 4,
  "shard_size": 16,
  "block_size": 8192,
  "symbol_size": 64,
  "prop_size": 16,
  "avai_size": 16,
  "ex_req_num": 4,
  "in_req_num": 4,
  "confirmation_depth": 6,
  "mining_interval": 0,
  "runtime": 200,
  "tx_diff": "000001ffffffffffffffffffffffffffffffffffffffffffffffffffffffffdc",
  "prop_diff": "0000003f1f8fc7e3f1f8fc7e3f1f8fc7e3f1f8fc7e3f1f8fc7e3f1f8fc7e3f1b",
  "order_diff": "000000231188c46231188c46231188c46231188c46231188c46231188c46230f",
  "avai_diff": "0000001c0e070381c0e070381c0e070381c0e070381c0e070381c0e070381c0c",
  "in_avai_diff": "000000022876b18022876b18022876b18022876b18022876b18022876b180228",
  "bandwidths": [6, 9, 11, 13, 15, 16, 18, 20, 22, 25, 28, 31, 35, 42, 53, 76, 7, 9, 11, 13, 15, 17, 19, 21, 23, 26, 29, 32, 37, 44, 57, 88, 7, 10, 12, 14, 15, 17, 19, 21, 24, 26, 29, 33, 38, 46, 62, 100, 8, 10, 12, 14, 16, 18, 20, 22, 24, 27, 30, 34, 40, 50, 68, 100],
  "description": "Demo for Optchain"
}

```

---

## Step 6: Define the Run Batch

We use a shell script to tell the system which experiments to run and how many times to repeat them.

Open `run_experiment.sh` and look for the `batch_config` section.

**Syntax:** `"Experiment_ID : Number_of_Iterations"`

### Example 1: Run "exper_0" three times

```bash
protocol="optchain"

batch_config=(
    "0:3"  
)

```

### Example 2: Run "exper_0" three times AND "exper_1" three times

```bash
protocol="optchain"

batch_config=(
    "0:3"  
    "1:3"
)

```

---

## Step 7: Run the Experiment

It's time to launch!

First, ensure the script is executable (you only need to do this once):

```bash
chmod +x run_experiment.sh

```

Then, run the script:

```bash
./run_experiment.sh

```

---

## Step 8: Analyze Results

Once the experiments have finished running, you can pull the logs and analyze the data.

Use the `read_log.py` script. You need to provide three arguments:

1. **Protocol Name** (e.g., `optchain`)
2. **Experiment ID** (e.g., `0`)
3. **Iteration Number** (e.g., `1` for the first run)

**Command:**

```bash
# Syntax: python3 read_log.py [PROTOCOL] [EXP_ID] [ITERATION]
python3 read_log.py optchain 0 1

```

This will print the experimental results for Experiment 0, Iteration 1.