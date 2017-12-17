# Gitea client

Connect:
```python
import os
token = os.environ["GITEA_TOKEN"]
j.clients.gitea.get_client("https://docs.grid.tf/api/v1", token)
```

Repositories:
```python
data = {}
data["name"] = "yves_repo"
data["description"] = "cool"
data["auto_init"] = False

g  = j.clients.gitea.get_client("https://docs.grid.tf/api/v1", token)

r = g.user.createCurrentUserRepo(data)
```

Labels:
```python
label_data={}

label_data["color"] = "#b60205"

label_data["name"] = "priority_critical"

label = g.repos.issueCreateLabel(label_data, "yves_repo", "yves@vreegoebezig.be")
```

Milestones:
```python
milestone_data={}

milestone_data["description"] = "test milestone"

milestone_data["title"] = "RC0"

milestone_data["title"] = "RC1"

milestone_data["due_on"] = "2017-12-15T15:22:43.188Z"

m = g.repos.issueCreateMilestone(milestone_data, "yves_repo", "yves@vreegoebezig.be")
```