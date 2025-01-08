### This POC:

1. Fetches the content of each agency website.
2. Extracts key information: meta description, headings, and a snippet of the main content.
3. Checks for the presence of specified keywords.
4. Uses Gemini's GPT model ( *gemini-1.5-flash* ) to analyze the extracted information and make a decision about whether it belongs to a digital agency.
5. Stores the results ( *URL, domain, approval status, decision explanation, and found keywords* ) in a CSV file.

### Demo

[![Watch the video](https://img.youtube.com/vi/GCsVrfubTz4/0.jpg)](https://youtu.be/GCsVrfubTz4)


### Steps to Run:

1. Create a Virtual Environment and activate it
    ```
    python -m venv venv && .\venv\Scripts\activate
    ```

2. Install the required libraries: 
    ```
    $ pip install requests beautifulsoup4 openai
    ```

3. Rename the `.localenv` file to `.env`  and add your actual Gemini API key

4. Run the script. It will process the example URLs provided and create a CSV file with the results.
    ```
    $ python gemini.py
    ```

5. Your results will be stored as a CSV in the same folder where you've run the script