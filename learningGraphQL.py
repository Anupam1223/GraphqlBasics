import requests
import json

accessToken = "h8RDfEWYbA9DRywds6Jj"

endpoint = "https://gitlab.com/api/graphql"
headers = {"Authorization": f"Bearer {accessToken}"}

query = """query {
  project(fullPath: "krispcall/krispcall-client") {
    id
    name
    mergeRequests(first: 100){
      pageInfo {
        hasNextPage
        hasPreviousPage
      }
      edges {
        cursor
        node {
          id
          title
          commitCount
          description
          webUrl
          approved
          approvedBy {
            pageInfo {
              hasNextPage
        			hasPreviousPage
            }
            edges {
              cursor
              node {
                id
                name
              }
            }
          }
          assignees {
            pageInfo {
              hasNextPage
        			hasPreviousPage
            }
            edges {
              cursor
              node {
                id
                name
              }
            }
          }
        }
      }
    }
  }
}"""


r = requests.post(endpoint, json={"query": query}, headers=headers)
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))
else:
    raise Exception(f"Query failed to run with a {r.status_code}.")
