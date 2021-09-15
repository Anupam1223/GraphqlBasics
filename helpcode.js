import fetch from 'node-fetch';
import getCommitsByRepository from './getCommitsByRepository';

import { GITHUB_ACCESS_TOKEN } from '../../../constants/constants';

const query = (repoName) => `
  query {
    rateLimit {
      limit
      cost
      remaining
      resetAt
    }
    viewer {
      repository(name: "${repoName}") {
        nameWithOwner
        refs(first: 100, refPrefix: "refs/heads/") {
          nodes {
            name
            target {
              ... on Commit {
                history(author: {id: "MDQ6VXNlcjg5Mjc0Mjc="}) {
                  totalCount
                  edges {
                    node {
                      ... on Commit {
                        oid
                        committedDate
                      }
                    }
                  }
                  pageInfo {
                    hasNextPage
                    endCursor
                  }
                }
              }
            }
          }
      }
      }
    }
  }
`;

const getCommitHistoriesByRepo = async (repoName = 'zilpi-storefront') => {
  try {
    const response = await fetch(`https://api.github.com/graphql`, {
      method: 'POST',
      body: JSON.stringify({
        query: query(repoName)
      }),
      headers: {
        Authorization: `Bearer ${GITHUB_ACCESS_TOKEN}`
      }
    });
    const jsonResponse = await response.json();
    const { data } = jsonResponse;
    const nextPageCursors = [];
    const repoBranches = data.viewer?.repository?.refs.nodes.map((branch) => {
      if (branch.target.history.pageInfo.hasNextPage) {
        nextPageCursors.push({
          branch: branch.name,
          cursor: branch.target.history.pageInfo.endCursor
        });
      }
      return {
        branch: branch.name,
        target: branch.target
      };
    });
    // console.log('nextPageCursors', nextPageCursors);
    const repoBranchesPagination = [];
    while (nextPageCursors.length) {
      // popping cursor changes the length of nextPageCursor and when reaches to 0, the while iteration stops
      const cursor = nextPageCursors.pop();
      // later user id should also be sent
      const { data: nextPageData } = await getCommitsByRepository(
        repoName,
        cursor.branch,
        cursor.cursor
      );
      console.log('nextPagedata', nextPageData);
      const { target } = nextPageData.data.viewer.repository.refs.nodes[0];
      const {
        history: { pageInfo }
      } = target;
      if (pageInfo.hasNextPage) {
        nextPageCursors.push({
          repository: cursor.repository,
          branch: cursor.branch,
          cursor: pageInfo.endCursor
        });
      }
      repoBranchesPagination.push({
        repository: cursor.repository,
        branch: cursor.branch,
        target
      });
    }
    // Extract and flat all histories
    const repoHistories = [...repoBranchesPagination, ...repoBranches].flatMap(
      (branch) => branch.target.history.edges
    );
    // console.log('repoHistories', repoHistories);
    return repoHistories;
  } catch (error) {
    console.error(error);
  }
};

export default getCommitHistoriesByRepo;

