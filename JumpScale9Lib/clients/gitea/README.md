# Gitea client


```python
cl = j.clients.gitea.get()



names=[item for item in cl.orgs_currentuser_list().keys()]
names.sort()

for name in names:
    org = cl.org_get(name)

    #CAREFULL WILL GO OVER ALL MILESTONES & LABELS and add them
    org.labels_milestones_add(remove_old=False)


    repoName=[item for item in org.repos_list().keys()][0] #first reponame

    repo = org.repo_get(repoName)

    # repo.labels_add()
    # repo.milestones_add(remove_old=False)


```

The client provides access to the gitea API, see [here](https://docs.greenitglobe.com/api/v1/swagger). For example to list all repos in a gitea organization taht the user belongs to using the API:

```python
cl = j.clients.gitea.get()
orgs = cl.api.orgs # Get all organizations that the user belongs to
repos, response = orgs.orgListRepos('nameoforg')
```

You get a list of `Repository` objects from the generated client, following are example operations on the object:

```python
repo = repos[0]
repo.full_name # returns org/reponame
repo.name
repo.default_branch
```
