import requests

# Now becomes more valuable once we have multiple API calls


def get(
    url,
    params=None,
):

    response = requests.get(
        url,
        params=params,
    )

    response.raise_for_status()

    return response.json()