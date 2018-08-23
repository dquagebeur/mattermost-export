import requests
import json

mattermostUrl = "https://mattermost.<domain>/api/v4"
headers = {"Authorization": "Bearer <personal token>"}

export = {}
neededUser = set()
neededFiles = set()

# Me

resp = requests.get(url=mattermostUrl+"/users/me", headers=headers)
me = resp.json()

# Teams

resp = requests.get(url=mattermostUrl+"/users/"+me["id"]+"/teams", headers=headers)
teams = resp.json()

for t in teams:
    resp = requests.get(url=mattermostUrl+"/teams/"+t["id"]+"/channels", headers=headers)
    export[t["name"]] = resp.json()

    for i in export[t["name"]]:
        resp = requests.get(url=mattermostUrl+"/channels/"+i["id"]+"/posts?since=10", headers=headers)
        jsresp = resp.json()

        try:
            orderedPosts = []

            for j in jsresp["order"]:
                orderedPosts.append(jsresp["posts"][j])
                neededUser.add(jsresp["posts"][j]["user_id"])

                if jsresp["posts"][j].has_key("file_ids"):
                    for f in jsresp["posts"][j]["file_ids"]:
                        neededFiles.add(f)

            orderedPosts.reverse()
            i["posts"] = orderedPosts

        except KeyError:
            pass

# Users

users = {}

for u in neededUser:
    resp = requests.get(url=mattermostUrl+"/users/"+u, headers=headers)
    users[u] = resp.json()

export["users"] = users

# Files

files = {}

for f in neededFiles:
    resp = requests.get(url=mattermostUrl+"/files/"+f+"/info", headers=headers)
    files[f] = resp.json()

    resp = requests.get(url=mattermostUrl+"/files/"+f, headers=headers, stream=True)
    with open(files[f]["name"], 'wb') as fd:
        for chunk in resp.iter_content(64000):
            fd.write(chunk)

export["files"] = files

print json.dumps(export)
