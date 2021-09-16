import asyncio
import httpx
import csv

oauth_token = "h8RDfEWYbA9DRywds6Jj"
endpoint = "https://gitlab.com/api/graphql"


def make_query(after_cursor=None):
    return {
        "query": """query {
  project(fullPath: "krispcall/krispcall-client") {
    id
    name
    mergeRequests(first: 100, after:AFTER){
      pageInfo {
        hasNextPage
        hasPreviousPage
        endCursor
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
          reviewers{
            pageInfo{
              hasNextPage
              hasPreviousPage
            }
            edges{
              cursor
              node{
                name
              }
            }
          }
        }
      }
    }
  }
}""".replace(
            "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
        )
    }


async def fecth_mergerequest(oauth_token):
    has_next_page = True
    after_cursor = None
    count = 0
    header = ["id", "title", "commitCount"]
    row = []

    async with httpx.AsyncClient() as client:

        while has_next_page:
            data = await client.post(
                endpoint,
                json=make_query(after_cursor),
                headers={"Authorization": "Bearer {}".format(oauth_token)},
            )

            json_data = data.json()

            for merge_request in json_data["data"]["project"]["mergeRequests"]["edges"]:

                # print(json.dumps(merge_request, indent=4))
                row.append(
                    [
                        merge_request["node"]["id"],
                        merge_request["node"]["title"],
                        merge_request["node"]["commitCount"],
                    ]
                )

                count += 1

            has_next_page = json_data["data"]["project"]["mergeRequests"]["pageInfo"][
                "hasNextPage"
            ]
            after_cursor = json_data["data"]["project"]["mergeRequests"]["pageInfo"][
                "endCursor"
            ]

    print("all of them printed")
    print("total count->", count)

    with open("countries.csv", "w", encoding="UTF8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(row)


asyncio.run(fecth_mergerequest(oauth_token))
