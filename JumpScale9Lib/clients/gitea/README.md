# Gitea client

Connect:
```python
j.clients.gitea.get()
```

Repositories:
```python
data = {}
data["name"] = "yves_repo"
data["description"] = "cool"
data["auto_init"] = False

g  = j.clients.gitea.get()

r = g.client.user.createCurrentUserRepo(data)
```

Labels:
```python
label_data={}

label_data["color"] = "#b60205"

label_data["name"] = "priority_critical"

label = g.client.repos.issueCreateLabel(label_data, "yves_repo", "yves@vreegoebezig.be")
```

Milestones:
```python
milestone_data={}

milestone_data["description"] = "test milestone"

milestone_data["title"] = "RC0"

milestone_data["title"] = "RC1"

milestone_data["due_on"] = "2017-12-15T15:22:43.188Z"

m = g.client.repos.issueCreateMilestone(milestone_data, "yves_repo", "yves@vreegoebezig.be")
```


Helper functions:

We added some extra functions that wrap several of the generated client's functionalities to make our life easier.

The ones that exist so far:

- `g.addLabelsToRepos`: Adds a list of labels to a list of repos. If labels are not supplied to the function, it uses the default labels list.


```python
default_labels = [
    {'color': '#e11d21', 'name': 'priority_critical'},
    {'color': '#f6c6c7', 'name': 'priority_major'},
    {'color': '#f6c6c7', 'name': 'priority_minor'},
    {'color': '#d4c5f9', 'name': 'process_duplicate'},
    {'color': '#d4c5f9', 'name': 'process_wontfix'},
    {'color': '#bfe5bf', 'name': 'state_inprogress'},
    {'color': '#bfe5bf', 'name': 'state_question'},
    {'color': '#bfe5bf', 'name': 'state_verification'},
    {'color': '#fef2c0', 'name': 'type_bug'},
    {'color': '#fef2c0', 'name': 'type_feature'},
    {'color': '#fef2c0', 'name': 'type_question'},
    {'color': '0000000', 'name': 'state_blocked'},
]
```

running the following will add the default labels to repos sarah-test and yves-repo. If a label with the same name exists on either repos, it will be skipped.

```python
repos = [{'owner': 'boctors@greenitglobe.com', 'name':'sarah-test'}, {'owner': 'yves@vreegoebezig.be', 'name':'yves_repo'}]
g.repos.helpers.addLabelsToRepos(repos)
```


- `g.addMileStonesToRepos`: Adds a list of milestones to a list of repos. If milestones are not supplied to the function, it uses the default milestones for the current quarter.


running the following will add the default milestones to repos sarah-test and yves-repo. If a milestone with the same title exists on either repos, it will be skipped.

```python
repos = [{'owner': 'boctors@greenitglobe.com', 'name':'sarah-test'}, {'owner': 'yves@vreegoebezig.be', 'name':'yves_repo'}]
g.addMileStonesToRepos(repos)
```


- `g.getDefaultMilestones()`: returns the milestones for the current quarter.

- `g.generateQuarterMilestones(quarter, year)`: returns the milestones for quarter <quarter> in year <year>.
