# Step 1: Load all people that need scraping from Notion (daily)

This script accesses the notion database and writes the notion id as well as the linkedin URL into a file. The file is always replaced with all people that need scraping.

Todos
- [ ] Maybe have some form of state to notify something like "10 people added to automation"

# Step 2: Scrape the profile (continuously)

This step loads just the first person and closes the file to not lock it. Then, a headless browser downloads the profile HTML, and saves it into the workspace under the persons slug as `.html`. Additionally, the text of the html is extracted, and saved as `.txt` alongside the HTML. 

- [ ] Webhook notification?
- [ ] Check if cookie is not valid anymore and we're not logged in

# Step 3: Let GPT extract the data (continuously)

The .txt files are loaded by the GPT script. A prompt is posed to the API, and JSON is returned. This is saved under the slug as a `.json` file.

# Step 4: Write data back to notion (continuously)

This script takes the json, and does the following things:

- Creates a company or gets the ID if it already exists in the company database
- Links the Person to the company
- Sets the status of the person as scraped