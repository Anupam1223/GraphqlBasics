import asyncio
import httpx
import json

oauth_token = "h8RDfEWYbA9DRywds6Jj"
endpoint = "https://gitlab.com/api/graphql"
groups = ["Codolytics", "Krispcall"]


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
                                name
                                id
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
    id = []
    name = []
    async with httpx.AsyncClient() as client:

        for group in groups:
            data = await client.post(
                endpoint,
                json=make_query(group),
                headers={"Authorization": f"Bearer {oauth_token}"},
            )

            json_data = data.json()

            for repositories in json_data["data"]["group"]["projects"]["edges"]:
                id.append(
                    repositories["node"]["id"],
                )
                name.append(
                    repositories["node"]["name"],
                )

        json_encoded = dict(zip(id, name))
        with open("repositories.txt", "w") as outfile:
            json.dump(json_encoded, outfile)


asyncio.run(fecth_repositories(oauth_token))
