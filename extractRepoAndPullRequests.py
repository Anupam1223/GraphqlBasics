import asyncio
import httpx
import csv

oauth_token = "h8RDfEWYbA9DRywds6Jj"
endpoint = "https://gitlab.com/api/graphql"

# ----- extracting groups first -------------------------------------------
token_for_extracting_groups = (
    "bdc4d07b6faf65e8f1491cf2fea8944b40ab7b82d426b527456100b518136374"
)
groups = []
with httpx.Client() as client:
    headers = {"Authorization": f"Bearer {token_for_extracting_groups}"}
    response_from_gitlab = client.get(
        "https://gitlab.com/api/v4/groups", headers=headers
    )
    response_in_json_format = response_from_gitlab.json()
for response_in_itr in response_in_json_format:
    groups.append(response_in_itr["name"])
# -------------------------------------------------------------------------

# ---- extracting all the projet paths ----------------------------------------
def make_query_to_extract_group(group):
    return {
        "query": """{
                        group(fullPath: PATH) {
                            projects(first: 100) {
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                            edges{
                                node {
                                    id
                                    fullPath
                                    name
                                    nameWithNamespace
                                    path
                                    openIssuesCount
                                    forksCount
                                    starCount
                                    createdAt
                                }
                            }
                            }
                        }
                        }
                        """.replace(
            "PATH", '"{}"'.format(group) if group else "null"
        )
    }


async def fecth_project_path(oauth_token):
    project_paths = []
    async with httpx.AsyncClient() as client:

        for group in groups:
            data = await client.post(
                endpoint,
                json=make_query_to_extract_group(group),
                headers={"Authorization": f"Bearer {oauth_token}"},
            )

            response_from_group_in_json_data = data.json()

            for repositories in response_from_group_in_json_data["data"]["group"][
                "projects"
            ]["edges"]:
                project_paths.append(repositories["node"]["fullPath"])
    return project_paths


# ---------------------------------------------------------------------------------


def make_query(path, after_cursor=None):
    return {
        "query": """query {
  project(fullPath: PATH) {
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
          author{
            name
          }
          targetProject{
            name
          }
          title
          commitCount
          description
          mergedAt
          createdAt
          webUrl
          state
          userDiscussionsCount
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
        ).replace(
            "PATH", '"{}"'.format(path) if path else path
        )
    }


async def fecth_mergerequest(oauth_token):

    full_paths = await fecth_project_path(oauth_token)
    header = [
        "Author",
        "Target Project",
        "Title",
        "Commit Count",
        "State",
        "User Comments",
        "Merged Time",
        "Requested Time",
        "Reviews",
    ]
    row = []
    reviews = []

    async with httpx.AsyncClient() as client:

        for path_of_project in full_paths:

            after_cursor = None
            has_next_page = True

            while has_next_page:
                path = path_of_project
                data = await client.post(
                    endpoint,
                    json=make_query(path, after_cursor),
                    headers={"Authorization": f"Bearer {oauth_token}"},
                )

                json_data = data.json()

                for merge_request in json_data["data"]["project"]["mergeRequests"][
                    "edges"
                ]:
                    for reviewrs in merge_request["node"]["reviewers"]["edges"]:
                        reviews.append(reviewrs["node"]["name"])

                    row.append(
                        [
                            merge_request["node"]["author"]["name"],
                            merge_request["node"]["targetProject"]["name"],
                            merge_request["node"]["title"],
                            merge_request["node"]["commitCount"],
                            merge_request["node"]["state"],
                            merge_request["node"]["userDiscussionsCount"],
                            merge_request["node"]["mergedAt"],
                            merge_request["node"]["createdAt"],
                            len(reviews),
                        ]
                    )
                    reviews = []
                has_next_page = json_data["data"]["project"]["mergeRequests"][
                    "pageInfo"
                ]["hasNextPage"]
                after_cursor = json_data["data"]["project"]["mergeRequests"][
                    "pageInfo"
                ]["endCursor"]

    with open(
        "merge_request_with_all_repo.csv", "w", encoding="UTF8", newline=""
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(row)


asyncio.run(fecth_mergerequest(oauth_token))
