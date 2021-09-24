import asyncio
import httpx
import json

oauth_token = "h8RDfEWYbA9DRywds6Jj"
endpoint = "https://gitlab.com/api/graphql"
token_for_extracting_groups = (
    "bdc4d07b6faf65e8f1491cf2fea8944b40ab7b82d426b527456100b518136374"
)

# ----- extracting groups first -------------------------------------------
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


def make_query(group):
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


async def fecth_repositories(oauth_token):
    all_data_fetched_for_repo = []
    async with httpx.AsyncClient() as client:

        for group in groups:
            data = await client.post(
                endpoint,
                json=make_query(group),
                headers={"Authorization": f"Bearer {oauth_token}"},
            )

            json_data = data.json()

            for repositories in json_data["data"]["group"]["projects"]["edges"]:
                all_data_fetched_for_repo.append(
                    {
                        "id": repositories["node"]["id"],
                        "fullpath": repositories["node"]["fullPath"],
                        "name": repositories["node"]["name"],
                        "nameWithNamespace": repositories["node"]["nameWithNamespace"],
                        "openIssuesCount": repositories["node"]["openIssuesCount"],
                        "forksCount": repositories["node"]["forksCount"],
                        "starCount": repositories["node"]["starCount"],
                        "createdAt": repositories["node"]["createdAt"],
                    }
                )

        with open("repositories.json", "w") as outfile:
            json.dump(all_data_fetched_for_repo, outfile)


asyncio.run(fecth_repositories(oauth_token))
