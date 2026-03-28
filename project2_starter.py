# SI 201 HW4 (Library Checkout System)
# Your name:Tracy Yuhei Ni, Gabby Jialu Tang, Shirley Shirui Huang
# Your student id: 04647754, 27755983
# Your email: yuheini@umich.edu, gabbylu@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging
# Make sure the git part is correct 
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from unittest import result

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""

def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    
    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    listings = []
    seen = set()

    links = soup.find_all("a", href=True)

    for link in links:
        href = link.get("href", "")
        match = re.search(r"/rooms/(\d+)", href)
        if not match:
            continue

        listing_id = match.group(1)

        if listing_id in seen:
            continue

        title = ""

        if link.get("aria-label"):
            title = link.get("aria-label").strip()

        if not title:
            for text in link.stripped_strings:
                text = text.strip()
                if " in " in text:
                    title = text
                    break

        if not title:
            parent = link.parent
            while parent and not title:
                for text in parent.stripped_strings:
                    text = text.strip()
                    if " in " in text:
                        title = text
                        break
                parent = parent.parent

        if title:
            title = title.split(" - ")[0].strip()
            listings.append((title, listing_id))
            seen.add(listing_id)

    return listings





    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# Tracy

def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    base_dir = os.path.abspath(os.path.dirname(__file__))
    html_path = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html")

    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    full_text = soup.get_text(" ", strip=True)


    # --------------------
    # policy_number
    # --------------------
    policy_number = ""

    raw_policy_match = re.search(
        r"(?:policy|license|licence|registration|permit)\s*(?:number|no\.?|#)?\s*[:\-]?\s*([A-Za-z0-9\- ]+)",
        full_text,
        re.IGNORECASE
    )

    if raw_policy_match:
        raw_value = raw_policy_match.group(1).strip()

        raw_value = raw_value.split(" ")[0].strip()

        if re.search(r"pending", raw_value, re.IGNORECASE):
            policy_number = "Pending"
        elif re.search(r"exempt", raw_value, re.IGNORECASE):
            policy_number = "Exempt"
        else:
            policy_number = raw_value
    else:

        valid_policy_match = re.search(
            r"(STR-\d{7}|20\d{2}-00\d{4}STR)",
            full_text,
            re.IGNORECASE
        )

        if valid_policy_match:
            policy_number = valid_policy_match.group(1)
        elif re.search(r"\bexempt\b", full_text, re.IGNORECASE):
            policy_number = "Exempt"
        elif re.search(r"\bpending\b", full_text, re.IGNORECASE):
            policy_number = "Pending"
        else:
            fallback_match = re.search(
                r"\b(?:STR[- ]?\d+|[A-Z0-9]{6,}[-A-Z0-9]*)\b",
                full_text
            )
            if fallback_match:
                policy_number = fallback_match.group(0)
            else:
                policy_number = "Pending"


    host_type = "Superhost" if re.search(r"\bSuperhost\b", full_text, re.IGNORECASE) else "regular"

    host_name = ""
    host_match = re.search(r"Hosted by\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)", full_text, re.IGNORECASE)
    if host_match:
        host_name = host_match.group(1).strip()

    room_type = ""
    if re.search(r"\bEntire (?:home|place|guest suite|guesthouse|loft|rental unit|apartment|condo)\b", full_text, re.IGNORECASE):
        room_type = "Entire Room"
    elif re.search(r"\bPrivate room\b", full_text, re.IGNORECASE):
        room_type = "Private Room"
    elif re.search(r"\bShared room\b", full_text, re.IGNORECASE):
        room_type = "Shared Room"

    location_rating = 0.0
    rating_match = re.search(r"Location\s*([0-9]\.[0-9])", full_text, re.IGNORECASE)

    if not rating_match:
        rating_match = re.search(r"([0-9]\.[0-9])\s*Location", full_text, re.IGNORECASE)

    if rating_match:
        location_rating = float(rating_match.group(1))

    return {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }
    
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listings = load_listing_results(html_path)

    dataresult = []

    for title, listing_id in listings:
        details_dict = get_listing_details(listing_id) 
        details = details_dict[listing_id] 

        policy_number = details["policy_number"]
        host_type = details["host_type"]
        host_name = details["host_name"]
        room_type = details["room_type"]
        location_rating = details["location_rating"]

        row = (
            title,
            listing_id,
            policy_number,
            host_type,
            host_name,
            room_type,
            location_rating
        )

        dataresult.append(row)

    return dataresult
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    sorted_data = sorted(data, key=lambda x: x[6], reverse=True)
    #sort data by location_rating, highest first so reverse

    # open file as writing mode
    with open(filename, "w", newline="", encoding = "utf-8-sig") as f:
        writer = csv.writer(f)

        #write header row
        writer.writerow([
            "Listing Title",
            "Listing ID",
            "Policy Number",
            "Host Type",
            "Host Name",
            "Room Type",
            "Location Rating"
        ])

        #write each row of data
        for row in sorted_data:
            writer.writerow(row)
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    room_type_ratings = {}

    for listing in data:
        room_type = listing[5]
        location_rating = listing[6]

        if location_rating == 0.0:
            continue

        if room_type not in room_type_ratings:
            room_type_ratings[room_type] = []

        room_type_ratings[room_type].append(location_rating)

    averages = {}
    for room_type in room_type_ratings:
        averages[room_type] = round(sum(room_type_ratings[room_type]) / len(room_type_ratings[room_type]), 1)

    return averages

    
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    invalid_numbers = []

    for listing in data:
        listing_id = listing[1]
        policy_number = listing[2]

        if policy_number == "Pending" or policy_number == "Exempt":
            continue

        if not re.fullmatch(r"STR-\d{7}|20\d{2}-00\d{4}STR", policy_number):
            invalid_numbers.append(listing_id)

    return invalid_numbers
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
# Tracy
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    base_url = "https://scholar.google.com/scholar"

    params = {
        "q": query
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(base_url, params=params, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    entries = soup.find_all("div", class_="gs_r")

    for entry in entries:
        title_tag = entry.find("h3")

        if title_tag:
            link_tag = title_tag.find("a")

            if link_tag:
                title = link_tag.get_text(strip=True)
                link = link_tag.get("href", "")

                results.append((title, link))

    return results[:10]  

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    # Tracy
    def test_load_listing_results(self):
        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    # Tracy
    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        results = []
        for listing_id in html_list:
            results.append(get_listing_details(listing_id))

        self.assertEqual(results[0]["467507"]["policy_number"], "STR-0005349")
        self.assertEqual(results[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(results[2]["1944564"]["room_type"], "Entire Room")
        self.assertEqual(results[2]["1944564"]["location_rating"], 4.9)

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        for row in self.detailed_data:
            self.assertEqual(len(row), 7)

        self.assertEqual(self.detailed_data[-1], ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8))

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        out_path = os.path.join(self.base_dir, "test.csv")

        output_csv(self.detailed_data, out_path)

        r = []
        with open(out_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                r.append(row)

 
        self.assertEqual(r[1], ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"])

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        result = avg_location_rating_by_room_type(self.detailed_data)

        self.assertEqual(result["Private Room"], 4.9)

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        invalid_listings = validate_policy_numbers(self.detailed_data)

        self.assertEqual(invalid_listings, ["16204265"])
        


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)