import os
import json
import requests

def execute_action(action_data):
    """
    Execute a Linear action to create an issue.
    
    Expected action_data format:
    {
        "platform": "linear",
        "action": "create_issue",
        "team_id": "your-team-id",
        "title": "Issue title",
        "description": "Issue description",
        "priority": 2,  # 0-4 where 0 is no priority, 1 is urgent, 2 is high, 3 is medium, 4 is low
        "labels": ["bug", "feature"],  # Optional
        "assignee_id": "user-id"  # Optional
    }
    """
    try:
        # Validate action data
        if action_data.get("action") != "create_issue":
            return {"status": "error", "message": "Unsupported action for Linear"}
        
        team_id = action_data.get("team_id")
        title = action_data.get("title")
        description = action_data.get("description", "")
        priority = action_data.get("priority", 0)
        labels = action_data.get("labels", [])
        assignee_id = action_data.get("assignee_id")
        
        if not team_id:
            return {"status": "error", "message": "Missing team_id in action data"}
        
        if not title:
            return {"status": "error", "message": "Missing title in action data"}
        
        # Get Linear API token from environment variables
        linear_token = os.environ.get("LINEAR_API_TOKEN")
        if not linear_token:
            return {"status": "error", "message": "Linear API token not configured"}
        
        # Set up the API request
        headers = {
            "Authorization": f"Bearer {linear_token}",
            "Content-Type": "application/json"
        }
        
        # Prepare GraphQL mutation for creating an issue
        mutation = """
        mutation CreateIssue($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue {
              id
              identifier
              url
            }
          }
        }
        """
        
        # Prepare variables for the mutation
        variables = {
            "input": {
                "teamId": team_id,
                "title": title,
                "description": description,
                "priority": priority
            }
        }
        
        # Add optional fields if provided
        if assignee_id:
            variables["input"]["assigneeId"] = assignee_id
        
        # Make the API request to create an issue
        response = requests.post(
            "https://api.linear.app/graphql",
            headers=headers,
            json={
                "query": mutation,
                "variables": variables
            }
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            if result.get("data", {}).get("issueCreate", {}).get("success"):
                issue = result["data"]["issueCreate"]["issue"]
                return {
                    "status": "success",
                    "message": "Created Linear issue",
                    "details": {
                        "issue_id": issue.get("id"),
                        "identifier": issue.get("identifier"),
                        "url": issue.get("url")
                    }
                }
            else:
                errors = result.get("errors", [])
                return {
                    "status": "error",
                    "message": f"Failed to create Linear issue: {errors[0].get('message') if errors else 'Unknown error'}",
                    "details": result
                }
        else:
            return {
                "status": "error",
                "message": f"Failed to create Linear issue: {response.status_code}",
                "details": response.json() if response.content else None
            }
            
    except Exception as e:
        return {"status": "error", "message": f"Failed to execute Linear action: {str(e)}"}
