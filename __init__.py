# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from jira import JIRA
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the InsecureRequestWarning from urllib3
warnings.simplefilter('ignore', InsecureRequestWarning)


class JiraC:
    """
    A handler class for interacting with Jira issues and projects using the JIRA API.  # noqa: E501

    This class allows finding, listing, and updating issues within a Jira project.  # noqa: E501
    """

    def __init__(self, server, api_token, username=None):
        """
        Initializes the JiraC instance.

        Parameters:
            server (str): The Jira server URL.
            api_token (str): The API token for authenticating with Jira.
            username (str, optional): The username for Jira. Defaults to None.
        """
        self.server = server.rstrip('/')  # Ensure no trailing slash
        self.api_token = api_token
        self.username = username
        self.jira = self._connect_to_jira()
        self._current_issue = None

    def _connect_to_jira(self):
        """Connects to the Jira server and initializes the JIRA object."""
        options = {'server': self.server, 'verify': False}
        return JIRA(options, token_auth=self.api_token)

    @property
    def current_issue(self):
        """Gets the current issue set for operations."""
        return self._current_issue

    @current_issue.setter
    def current_issue(self, issue_key):
        """
        Sets the current issue for operations.

        Parameters:
            issue_key (str): The key of the issue to set.
        """
        try:
            issue = self.jira.issue(issue_key)
            self._current_issue = issue
        except Exception as e:
            print(f"Error setting issue with key '{issue_key}': {e}")
            self._current_issue = None

    # Property for Story Points using human-readable names
    @property
    def story_points(self):
        """Gets the story points for the current issue."""
        if not self._current_issue:
            raise ValueError("No current issue set.")
        return getattr(self._current_issue.fields, 'story_points', None)

    @story_points.setter
    def story_points(self, value):
        """Sets the story points for the current issue."""
        if not self._current_issue:
            raise ValueError("No current issue set.")
        self._current_issue.update(fields={'story_points': value})
        print(f"Story Points set to '{value}' for issue {self._current_issue.key}.")  # noqa: E501

    # Property for Assignee
    @property
    def assignee(self):
        """Gets the assignee for the current issue."""
        if not self._current_issue:
            raise ValueError("No current issue set.")
        return self._current_issue.fields.assignee.displayName if self._current_issue.fields.assignee else None  # noqa: E501

    @assignee.setter
    def assignee(self, value):
        """Sets the assignee for the current issue."""
        if not self._current_issue:
            raise ValueError("No current issue set.")
        self._current_issue.update(fields={"assignee": {"name": value}})
        print(f"Assignee set to '{value}' for issue {self._current_issue.key}.")  # noqa: E501

    # Property for Components
    @property
    def components(self):
        """Gets the components for the current issue."""
        if not self._current_issue:
            raise ValueError("No current issue set.")
        return [component.name for component in self._current_issue.fields.components]  # noqa: E501

    @components.setter
    def components(self, value):
        """Sets the components for the current issue."""
        if not self._current_issue:
            raise ValueError("No current issue set.")
        self._current_issue.update(fields={"components": [{"name": value}]})
        print(f"Components set to '{value}' for issue {self._current_issue.key}.")  # noqa: E501


def autocorrect_issue_key(issue_key):
    """
    Corrects the Jira issue key format if necessary.

    Parameters:
        issue_key (str): The input issue key to correct.

    Returns:
        str: The corrected issue key.
    """
    match = re.match(r'^([A-Z]+)-?(\d+)$', issue_key)
    if match:
        project_code = match.group(1)
        issue_number = match.group(2)
        corrected_key = f"{project_code}-{issue_number}"
        return corrected_key
    else:
        print(f"Invalid issue key format: {issue_key}")
        return issue_key  # Return as-is if it doesn't match the expected pattern  # noqa: E501
