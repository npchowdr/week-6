# your code here ...
import os
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

class Genius:
    """Simple client wrapper for the Genius API."""

    def __init__(self, access_token: str):
        self.access_token = access_token
        if not self.access_token:
            raise ValueError("ACCESS_TOKEN is missing. Set it in your environment or pass access_token=...")

        self.base_url = "https://api.genius.com"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

    def _request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a GET request and return the JSON response dictionary."""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def search(self, search_term: str, per_page: int = 10) -> list[dict[str, Any]]:
        """Search Genius for a query and return the full list of hits."""
        json_data = self._request("search", params={"q": search_term, "per_page": per_page})
        return json_data["response"]["hits"]

    def get_artist(self, search_term: str) -> dict[str, Any]:
        """Return artist metadata from the first Genius hit for a search term."""
        hits = self.search(search_term)
        if not hits:
            raise ValueError(f"No Genius results found for search term: {search_term!r}")

        primary_artist = hits[0]["result"]["primary_artist"]
        if primary_artist is None:
            raise ValueError(f"No primary artist found for search term: {search_term!r}")

        artist_id = primary_artist["id"]
        if artist_id is None:
            raise ValueError(f"Artist ID not found for search term: {search_term!r}")

        artist_data = self._request(f"artists/{artist_id}")
        return artist_data
        #return artist_data.get("artist", artist_data)

    def get_artists(self, search_terms: list[str]) -> pd.DataFrame:
        """Return a DataFrame with one row per artist search term."""
        rows: list[dict[str, Any]] = []

        for search_term in search_terms:
            try:
                artist = self.get_artist(search_term)
            except (ValueError, KeyError, TypeError):
                artist = {}

            rows.append(
                {
                    "search_term": search_term,
                    "artist_name": artist.get("name"),
                    "artist_id": artist.get("id"),
                    "followers_count": artist.get("followers_count"),
                }
            )

        return pd.DataFrame(
            rows,
            columns=["search_term", "artist_name", "artist_id", "followers_count"],
        )
