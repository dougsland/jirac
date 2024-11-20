# Jirac

`jirac` is a Python utility for interacting with Jira issues. This README provides comprehensive instructions on setting up environment variables, building and installing `jirac`, and using the package effectively.

## Table of Contents
- [Prerequisites](#prerequisites)
  - [How to Get a Jira API Token](how-to-get-a-jira-api-token)
- [Setup Environment Variables](#setup-environment-variables)
- [Installation](#installation)
  - [Using `pip`](#using-pip)
  - [Building and Installing a Wheel Distribution](#building-and-installing-a-wheel-distribution)
  - [Installing in a Virtual Environment (Optional)](#installing-in-a-virtual-environment-optional)
- [Usage](#usage)

## Prerequisites

- Python 3.9 or higher installed.
- Jira API token with appropriate permissions.
- `pip` and `setuptools` installed and up to date.

### How to Get a Jira API Token:

1. **Log In to Your Jira Account:**
   - Go to your Jira instance, typically at `https://<your-domain>`.
   - Log in with your credentials
   - Select Profile

2. **Access Personal Access Token**
   - In the left-hand menu.

3. **Create an Personal Access Token:**
   - Click the **"Personal Access Token"** button.
   - Enter a **label** for your token (e.g., `Jira Token for jirac`), and then click **"Create"** (select your expiration preference, unselect if you prefer to **NOT** expire).

4. **Copy Your Token:**
   - A window will appear showing your new token. **Copy the token** and store it in a secure place (e.g., a password manager).
   - **Important**: You won’t be able to view the token again once you close this window. If you lose it, you’ll need to create a new one.

## Setup Environment Variables

To use `jirac`, you need to configure the following environment variables. These variables can be added to your `~/.bashrc` (or `~/.zshrc` if you use zsh).

### Add the following lines to your shell configuration file:

```bash
# Jira configuration for jirac
export JIRA_SERVER_URL="https://issues.domain.com"
export JIRA_API_TOKEN="your_token"
export JIRA_USERNAME="your_kerberos_username@domain.com"  # Optional if using token-based authentication
export JIRA_PROJECT="PROJECT_NAME" # Example: "VROOM"
```

### Reload the Shell Configuration

To apply the changes:

```bash
source ~/.bashrc  # or `source ~/.zshrc` for zsh users
```

## Installation

### Using `pip`

To install `jirac` using `pip`:

1. Navigate to the directory containing `jirac`'s source code.
2. Run the following command to build and install `jirac` using `pip`:

```bash
sudo python -m pip install . --prefix=/usr
```

This will install `jirac` into `/usr/lib/python3.9/site-packages/` (adjust version accordingly based on your Python version).

### Building and Installing a Wheel Distribution

1. First, build the wheel using `pypa/build`:

   ```bash
   python -m pip install --upgrade build
   python -m build
   ```

   This will generate `.tar.gz` and `.whl` files in the `dist/` directory.

2. Next, install the built wheel:

   ```bash
   sudo python -m pip install dist/jirac-0.1.0-py3-none-any.whl --prefix=/usr
   ```

### Installing in a Virtual Environment (Optional)

For an isolated environment to avoid potential conflicts:

1. Create and activate a virtual environment:

   ```bash
   python -m venv myenv
   source myenv/bin/activate
   ```

2. Install `jirac`:

   ```bash
   pip install .
   ```

## Usage

After setting up your environment variables and installing `jirac`, you can go to [examples dir](./examples) or use the following example:

Showing issues with assignee **NOT SET** in the component **QM**
```bash
show-issues-assignee-as-none-using-component qm

Total: 8
```

Setting issues with assignee **NOT SET** in the component **QM** as **Douglas Landgraf**
```bash
show-issues-assignee-as-none-using-component qm --set-assignee "Douglas Landgraf"
<SNIP>
Issue VROOM-12345 has been assigned to Douglas Landgraf.

Total: 8
```

Example code [show-issue-info](./examples/show-issue-info)
```python
import argparse
import os
import re
from jirac import JiraC, autocorrect_issue_key


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fetch and print Jira issue details.")  # noqa: E501
    parser.add_argument('issue_key', help='The Jira issue key to fetch (e.g., VROOM-12345)')  # noqa: E501
    args = parser.parse_args()

    # Autocorrect the issue key format if necessary (from VROOM123 to VROOM-123)  # noqa: E501
    corrected_issue_key = autocorrect_issue_key(args.issue_key)

    # Fetch Jira connection details from environment variables
    server = os.getenv("JIRA_SERVER_URL")
    api_token = os.getenv("JIRA_API_TOKEN")
    username = os.getenv("JIRA_USERNAME")  # Optional if using token-based auth

    if not server or not api_token:
        print("Please set the environment variables: JIRA_SERVER_URL, JIRA_API_TOKEN")  # noqa: E501
        return

    # Initialize Jira client
    jira_client = JiraC(server, api_token, username)

    # Set the current issue to work with
    jira_client.current_issue = corrected_issue_key

    # Print all available information about the current issue
    if jira_client.current_issue:
        issue = jira_client.current_issue
        story_points = getattr(issue.fields, 'customfield_12310243', None)
        epic_link = getattr(issue.fields, 'customfield_12311140', None)
        sprint_data = getattr(issue.fields, 'customfield_12310940', None) or []
        sprint_names = [re.search(r'name=([^,]+)', sprint).group(1) if isinstance(sprint, str) and re.search(r'name=([^,]+)', sprint) else 'Unnamed Sprint' for sprint in sprint_data] if isinstance(sprint_data, list) else ['No sprint data available']  # noqa: E501

        print("-------------------------------------------------")
        print(f"Summary: {issue.fields.summary}")
        issue_url = f"{jira_client.server}/browse/{issue.key}"
        print(f"{issue_url}")
        print("-------------------------------------------------")
        print(f"Status: {issue.fields.status.name}")
        print(f"Assignee: {jira_client.assignee}")
        print(f"Components: {', '.join(jira_client.components) if jira_client.components else 'None'}")  # noqa: E501
        print(f"Resolution: {issue.fields.resolution.name if issue.fields.resolution else 'Unresolved'}")  # noqa: E501
        print("-------------------------------------------------")
        print(f"Epic Link: {epic_link}")
        print(f"Story Points: {story_points}")
        print(f"Sprint(s): {', '.join(sprint_names) if sprint_names else 'No sprints found'}")  # noqa: E501
        print(f"Priority: {issue.fields.priority.name if issue.fields.priority else 'None'}")  # noqa: E501
        print(f"Reporter: {issue.fields.reporter.displayName if issue.fields.reporter else 'None'}")  # noqa: E501
        print(f"Labels: {', '.join(issue.fields.labels) if issue.fields.labels else 'None'}")  # noqa: E501
        print(f"Created: {issue.fields.created}")
        print(f"Updated: {issue.fields.updated}")
        print("-------------------------------------------------")

        print(f"Description:\n\n{issue.fields.description}")
        print("-------------------------------------------------")


if __name__ == "__main__":
    main()
```
